from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


DEFAULT_RESEARCH_ROOT = Path("local/work/jp_glyph_usage_research_v1")
DEFAULT_CELL_ROOT = Path("local/work/jp_glyph_clear_pages_v1/cells")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build contact sheets for glyph cells that still need identification.")
    parser.add_argument("--research-root", type=Path, default=DEFAULT_RESEARCH_ROOT)
    parser.add_argument("--cell-root", type=Path, default=DEFAULT_CELL_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_RESEARCH_ROOT / "contact_sheets")
    args = parser.parse_args()

    rows = read_csv(args.research_root / "unknown_or_blank_used_cells.csv")
    for row in rows:
        row["cell_png"] = cell_png_for_row(args.cell_root, row)

    extracted_rows = [row for row in rows if int(row.get("extracted_usage_count") or 0) > 0]
    all_rows = rows

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_sheet(args.output_dir / "needs_identification_extracted_usage.png", extracted_rows, "Needs identification: extracted glyph-code usage")
    write_sheet(args.output_dir / "needs_identification_all_flagged.png", all_rows, "Needs identification: all flagged cells")
    write_csv(args.output_dir / "needs_identification_extracted_usage.csv", extracted_rows)
    write_csv(args.output_dir / "needs_identification_all_flagged.csv", all_rows)
    write_readme(args.output_dir, extracted_rows, all_rows)
    print(f"wrote {args.output_dir}")
    return 0


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def cell_png_for_row(cell_root: Path, row: dict[str, str]) -> str:
    source = row["source"]
    child = int(row["child"])
    layer = row["layer"]
    cell = int(row["cell"])
    return (cell_root / f"child{child:02d}_{source}_{layer}_cell{cell:03d}.png").as_posix()


def write_sheet(path: Path, rows: list[dict[str, Any]], title: str) -> None:
    rows = sorted(rows, key=lambda row: (int(row["block"]), int(row["cell"])))
    cols = 4
    tile_w = 285
    tile_h = 142
    margin = 20
    title_h = 42
    sheet_rows = max(1, (len(rows) + cols - 1) // cols)
    image = Image.new("RGB", (margin * 2 + cols * tile_w, margin * 2 + title_h + sheet_rows * tile_h), "white")
    draw = ImageDraw.Draw(image)
    small, bold = fonts()
    draw.text((margin, margin), f"{title} ({len(rows)} cells)", fill=(20, 20, 20), font=bold)

    for index, row in enumerate(rows):
        col = index % cols
        out_row = index // cols
        x = margin + col * tile_w
        y = margin + title_h + out_row * tile_h
        draw.rectangle((x, y, x + tile_w - 8, y + tile_h - 8), outline=(190, 190, 190), width=1)
        draw_cell(draw, image, row, x, y, small, bold)

    image.save(path)


def draw_cell(
    draw: ImageDraw.ImageDraw,
    sheet: Image.Image,
    row: dict[str, Any],
    x: int,
    y: int,
    small: ImageFont.ImageFont,
    bold: ImageFont.ImageFont,
) -> None:
    cell_path = Path(row["cell_png"])
    if cell_path.exists():
        cell = Image.open(cell_path).convert("RGBA")
        max_w = 82
        max_h = 92
        scale = min(max_w / cell.width, max_h / cell.height)
        if scale < 1:
            new_size = (max(1, int(cell.width * scale)), max(1, int(cell.height * scale)))
            cell = cell.resize(new_size, Image.Resampling.NEAREST)
        elif cell.width <= 14 and cell.height <= 14:
            scale_up = 5
            cell = cell.resize((cell.width * scale_up, cell.height * scale_up), Image.Resampling.NEAREST)
        preview = Image.new("RGB", (max_w + 10, max_h + 10), (32, 32, 32))
        paste_x = (preview.width - cell.width) // 2
        paste_y = (preview.height - cell.height) // 2
        preview.paste(cell.convert("RGB"), (paste_x, paste_y), cell)
        sheet.paste(preview, (x + 10, y + 10))
    else:
        draw.rectangle((x + 10, y + 10, x + 92, y + 92), fill=(240, 200, 200), outline=(180, 80, 80))
        draw.text((x + 16, y + 44), "missing", fill=(80, 0, 0), font=small)

    code = row.get("code") or "(no code)"
    count = row.get("extracted_usage_count") or "0"
    raw = row.get("raw_bin_hit_count") or "0"
    page = row.get("page") or ""
    block = row.get("block") or ""
    cell_num = row.get("cell") or ""
    grid = f"r{row.get('row')} c{row.get('col')}"

    text_x = x + 105
    text_y = y + 10
    lines = [
        code,
        f"block {block} cell {cell_num}",
        grid,
        f"glyph uses: {count}",
        f"raw hits: {raw}",
        short_page(page),
    ]
    for i, line in enumerate(lines):
        draw.text((text_x, text_y + i * 18), line, fill=(20, 20, 20), font=bold if i == 0 else small)


def short_page(page: str) -> str:
    page = page.replace("block", "b").replace("_code", "_")
    return page[:22]


def fonts() -> tuple[ImageFont.ImageFont, ImageFont.ImageFont]:
    candidates = [
        Path("C:/Windows/Fonts/consola.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), 13), ImageFont.truetype(str(path), 15)
    return ImageFont.load_default(), ImageFont.load_default()


def write_readme(output_dir: Path, extracted_rows: list[dict[str, Any]], all_rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Glyph Identification Contact Sheets",
        "",
        "- `needs_identification_extracted_usage.png`: unknown/blank reviewed cells that appear in extracted `glyph_codes` runs.",
        "- `needs_identification_all_flagged.png`: all unknown/blank cells flagged by the usage research, including raw-bin-only sightings.",
        "- Matching CSV files include the same rows plus the source cell crop path.",
        "",
        f"Focused extracted-usage cells: {len(extracted_rows)}",
        f"All flagged cells: {len(all_rows)}",
    ]
    (output_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
