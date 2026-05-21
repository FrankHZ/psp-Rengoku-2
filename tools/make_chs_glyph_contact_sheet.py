from __future__ import annotations

import argparse
import csv
import math
import re
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


DEFAULT_BUILD_ROOT = Path("local/work/combined_chs_v44_reviewed_token")
DEFAULT_OUTPUT_DIR = DEFAULT_BUILD_ROOT / "glyph_contact_sheet"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a contact sheet for generated CHS runtime glyph assignments.")
    parser.add_argument("--build-root", type=Path, default=DEFAULT_BUILD_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--columns", type=int, default=16)
    parser.add_argument("--scale", type=int, default=3)
    args = parser.parse_args()

    assignments_path = args.build_root / "runtime_glyph_assignments.csv"
    previews_dir = args.build_root / "previews"
    rows = read_assignments(assignments_path)
    indexed = index_preview_paths(rows, previews_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_index_csv(args.output_dir / "glyph_contact_index.csv", indexed)
    write_contact_sheet(args.output_dir / "glyph_contact_sheet.png", indexed, args.columns, args.scale)
    write_readme(args.output_dir / "README.md", args.build_root, indexed, args.columns)
    print(f"wrote {args.output_dir}")
    return 0


def read_assignments(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    for index, row in enumerate(rows):
        row["assignment_index"] = str(index)
        row["layer"] = parse_layer(row.get("notes", ""))
    return rows


def parse_layer(notes: str) -> str:
    match = re.search(r"layer=(low|high)", notes)
    return match.group(1) if match else ""


def index_preview_paths(rows: list[dict[str, str]], previews_dir: Path) -> list[dict[str, str]]:
    indexed: list[dict[str, str]] = []
    for row in rows:
        char = row["char"]
        codepoint = ord(char)
        child = int(row["child"])
        cell = int(row["cell"])
        layer = row["layer"]
        preview = previews_dir / f"child{child}_cell{cell:02d}_{layer}_{codepoint:04x}.png"
        indexed.append(
            {
                **row,
                "unicode": f"U+{codepoint:04X}",
                "preview": preview.as_posix(),
                "preview_exists": "yes" if preview.exists() else "no",
            }
        )
    return indexed


def write_index_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fields = [
        "assignment_index",
        "char",
        "unicode",
        "code",
        "archive",
        "entry",
        "child",
        "source",
        "cell",
        "layer",
        "runtime_texture",
        "base",
        "preview",
        "preview_exists",
        "notes",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_contact_sheet(path: Path, rows: list[dict[str, str]], columns: int, scale: int) -> None:
    if not rows:
        Image.new("RGB", (1, 1), "white").save(path)
        return

    font = load_font(14)
    label_font = load_font(11)
    cell_w = 108
    cell_h = 88
    margin = 12
    header_h = 34
    rows_count = math.ceil(len(rows) / columns)
    width = margin * 2 + columns * cell_w
    height = margin * 2 + header_h + rows_count * cell_h
    sheet = Image.new("RGB", (width, height), (250, 250, 250))
    draw = ImageDraw.Draw(sheet)
    draw.text((margin, 8), f"Generated CHS glyph contact sheet: {len(rows)} assignments", fill=(20, 20, 20), font=font)

    for index, row in enumerate(rows):
        col = index % columns
        grid_row = index // columns
        x = margin + col * cell_w
        y = margin + header_h + grid_row * cell_h
        draw.rectangle((x, y, x + cell_w - 4, y + cell_h - 4), fill=(255, 255, 255), outline=(205, 205, 205))
        paste_preview(sheet, row, x + 5, y + 5, scale)
        draw.text((x + 50, y + 5), row["char"], fill=(0, 0, 0), font=font)
        draw.text((x + 50, y + 25), row["unicode"], fill=(60, 60, 60), font=label_font)
        draw.text((x + 5, y + 52), f'{row["code"]} {row["layer"]}', fill=(50, 50, 50), font=label_font)
        draw.text((x + 5, y + 68), f'c{row["child"]} cell {row["cell"]}', fill=(90, 90, 90), font=label_font)

    sheet.save(path)


def paste_preview(sheet: Image.Image, row: dict[str, str], x: int, y: int, scale: int) -> None:
    preview = Path(row["preview"])
    if not preview.exists():
        return
    glyph = Image.open(preview).convert("RGBA")
    glyph = glyph.resize((glyph.width * scale, glyph.height * scale), Image.Resampling.NEAREST)
    back = Image.new("RGBA", (42, 42), (245, 245, 245, 255))
    gx = x + (back.width - glyph.width) // 2
    gy = y + (back.height - glyph.height) // 2
    sheet.paste(back.convert("RGB"), (x, y))
    sheet.paste(glyph, (gx, gy), glyph)


def load_font(size: int) -> ImageFont.ImageFont:
    for path in (
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/msgothic.ttc"),
    ):
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size)
            except OSError:
                pass
    return ImageFont.load_default()


def write_readme(path: Path, build_root: Path, rows: list[dict[str, str]], columns: int) -> None:
    missing = sum(1 for row in rows if row["preview_exists"] != "yes")
    lines = [
        "# Generated CHS Glyph Contact Sheet",
        "",
        f"Build root: `{build_root.as_posix()}`",
        f"Assignments: {len(rows)}",
        f"Columns: {columns}",
        f"Missing preview images: {missing}",
        "",
        "Files:",
        "",
        "- `glyph_contact_sheet.png`: visual contact sheet in runtime assignment order.",
        "- `glyph_contact_index.csv`: mapping from assignment index to character, source page, cell, layer, runtime code, and preview path.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
