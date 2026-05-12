from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from build_jp_glyph_table_v2 import read_2bpp_cell, short_status


DEFAULT_TABLE = Path("local/work/jp_glyph_table_v2/jp_glyph_table_v2.csv")
DEFAULT_SOURCE_ROOT = Path("local/work/jp_glyph_clear_pages_v1")
DEFAULT_RESEARCH_ROOT = Path("local/work/jp_glyph_usage_research_v1")
DEFAULT_OUTPUT_ROOT = DEFAULT_RESEARCH_ROOT / "marked_contact_sheets"
SPECIAL_REVIEW_CODES = {
    "0x011e",  # fullwidth slash
    "0x013b",  # fullwidth plus
    "0x013c",  # minus
    "0x013e",  # multiplication sign
    "0x02ac",  # omega
    "0x02ad",  # alpha
    "0x02ae",  # beta
    "0x02af",  # gamma
    "0x027a",  # trademark
    "0x027b",  # left double quote
    "0x027c",  # right double quote
    "0x0282",  # euro
    "0x0327",  # roman numeral two
    "0x0328",  # roman numeral three
    "0x0329",  # roman numeral four
    "0x032a",  # roman numeral five
    "0x032c",  # roman numeral seven
    "0x032d",  # roman numeral eight
    "0x032e",  # roman numeral nine
    "0x032f",  # roman numeral ten
    "0x03b6",  # square mm
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Mark glyph cells needing identification on v2-style 2bpp contact sheets.")
    parser.add_argument("--table", type=Path, default=DEFAULT_TABLE)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--research-root", type=Path, default=DEFAULT_RESEARCH_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()

    table_rows = read_csv(args.table)
    all_rows = read_csv(args.research_root / "unknown_or_blank_used_cells.csv")
    focused_targets = rows_to_targets(
        [row for row in all_rows if int(row.get("extracted_usage_count") or 0) > 0]
    )
    all_targets = rows_to_targets(all_rows)

    args.output_root.mkdir(parents=True, exist_ok=True)
    write_marked_pages(
        args.output_root / "extracted_usage",
        table_rows,
        focused_targets,
        args.source_root,
        "NEEDS ID",
    )
    write_marked_pages(
        args.output_root / "all_flagged",
        table_rows,
        all_targets,
        args.source_root,
        "FLAGGED",
    )
    special_targets = used_special_review_targets(args.research_root / "reviewed_glyph_usage.csv")
    write_marked_pages(
        args.output_root / "special_used",
        table_rows,
        special_targets,
        args.source_root,
        "VERIFY",
    )
    write_readme(args.output_root, focused_targets, all_targets, special_targets)
    print(f"wrote {args.output_root}")
    return 0


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def read_targets(path: Path) -> dict[tuple[str, int], dict[str, str]]:
    targets: dict[tuple[str, int], dict[str, str]] = {}
    if not path.exists() or path.stat().st_size == 0:
        return targets
    for row in read_csv(path):
        targets[(row["page"], int(row["cell"]))] = row
    return targets


def rows_to_targets(rows: list[dict[str, str]]) -> dict[tuple[str, int], dict[str, str]]:
    return {(row["page"], int(row["cell"])): row for row in rows}


def used_special_review_targets(path: Path) -> dict[tuple[str, int], dict[str, str]]:
    targets: dict[tuple[str, int], dict[str, str]] = {}
    if not path.exists():
        return targets
    for row in read_csv(path):
        if row.get("code") not in SPECIAL_REVIEW_CODES:
            continue
        if int(row.get("extracted_usage_count") or 0) <= 0:
            continue
        targets[(row["page"], int(row["cell"]))] = row
    return targets


def write_marked_pages(
    output_dir: Path,
    rows: list[dict[str, str]],
    targets: dict[tuple[str, int], dict[str, str]],
    source_root: Path,
    marker_text: str,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for old_sheet in output_dir.glob("*_marked.png"):
        try:
            old_sheet.unlink()
        except PermissionError:
            pass
    rows_by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        page = page_key(row)
        if any(target_page == page for target_page, _cell in targets):
            rows_by_page[page].append(row)

    for page, page_rows in sorted(rows_by_page.items()):
        page_targets = {cell: target for (target_page, cell), target in targets.items() if target_page == page}
        if not page_targets:
            continue
        output = output_dir / f"{page}_marked.png"
        write_marked_contact_sheet(output, page_rows, page_targets, source_root, marker_text)


def page_key(row: dict[str, str]) -> str:
    return f"block{int(row['block']):02d}_child{int(row['child']):02d}_{row['source']}_{row['layer']}"


def write_marked_contact_sheet(
    path: Path,
    rows: list[dict[str, str]],
    targets: dict[int, dict[str, str]],
    source_root: Path,
    marker_text: str,
) -> None:
    if not rows:
        return
    rows = sorted(rows, key=lambda row: int(row["cell"]))
    first = rows[0]
    cols = int(first["grid_cols"])
    cell_w = int(first["cell_w"])
    cell_h = int(first["cell_h"])
    scale = 5 if cell_w == 14 else 6
    tile_w = max(cell_w * scale + 22, 82)
    tile_h = cell_h * scale + 54
    sheet_rows = (len(rows) + cols - 1) // cols
    image = Image.new("RGB", (cols * tile_w, sheet_rows * tile_h), "white")
    draw = ImageDraw.Draw(image)
    small, glyph_font, marker_font = load_fonts()

    for row in rows:
        cell = int(row["cell"])
        x = int(row["col"]) * tile_w
        y = int(row["row"]) * tile_h
        is_target = cell in targets
        border = (220, 30, 30) if is_target else (190, 190, 190)
        border_width = 3 if is_target else 1
        draw.rectangle((x, y, x + tile_w - 1, y + tile_h - 1), outline=border, width=border_width)
        glyph = read_2bpp_cell(source_root, row)
        if glyph is not None:
            glyph = glyph.resize((cell_w * scale, cell_h * scale), Image.Resampling.NEAREST).convert("RGB")
            image.paste(glyph, (x + (tile_w - glyph.width) // 2, y + 16))
        if is_target:
            draw.rectangle((x + 1, y + 1, x + tile_w - 2, y + 15), fill=(220, 30, 30))
            draw.text((x + 3, y + 2), marker_text, fill=(255, 255, 255), font=marker_font)
            target = targets[cell]
            usage = target.get("extracted_usage_count") or "0"
            draw.rectangle((x + 1, y + tile_h - 15, x + tile_w - 2, y + tile_h - 2), fill=(255, 245, 180))
            draw.text((x + 3, y + tile_h - 14), f"uses {usage}", fill=(80, 40, 0), font=small)
        else:
            draw.text((x + 2, y + 2), f"{cell:03d} {row['code']}", fill=(0, 0, 0), font=small)
        current = str(row.get("current") or "")
        status = short_status(str(row.get("status") or ""))
        color = (0, 100, 0) if row.get("status") in {"confirmed_seed", "reviewed_ocr_full_block", "reviewed_ocr_partial_block"} else (160, 80, 0)
        draw.text((x + 2, y + cell_h * scale + 20), current, fill=color, font=glyph_font)
        draw.text((x + 2, y + cell_h * scale + 42), status, fill=(80, 80, 80), font=small)

    image.save(path)


def load_fonts() -> tuple[ImageFont.ImageFont, ImageFont.ImageFont, ImageFont.ImageFont]:
    try:
        return (
            ImageFont.truetype("C:/Windows/Fonts/consola.ttf", size=11),
            ImageFont.truetype("C:/Windows/Fonts/msgothic.ttc", size=18),
            ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", size=10),
        )
    except OSError:
        default = ImageFont.load_default()
        return default, default, default


def write_readme(
    output_root: Path,
    focused: dict[tuple[str, int], dict[str, str]],
    all_targets: dict[tuple[str, int], dict[str, str]],
    special_targets: dict[tuple[str, int], dict[str, str]],
) -> None:
    lines = [
        "# Marked Glyph Identification Contact Sheets",
        "",
        "These sheets use the same 2bpp page cropping and layout style as `local/work/jp_glyph_table_v2/contact_sheets/`.",
        "",
        "- `extracted_usage/`: cells with unknown/blank reviewed text that appear in extracted JP `glyph_codes` records.",
        "- `all_flagged/`: broader set including raw-bin-only sightings.",
        "- `special_used/`: used cells from special/symbol pages that may need Unicode confirmation.",
        "",
        f"Extracted-usage cells marked: {len(focused)}",
        f"All flagged cells marked: {len(all_targets)}",
        f"Special-review cells marked: {len(special_targets)}",
    ]
    (output_root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
