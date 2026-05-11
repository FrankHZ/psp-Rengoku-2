from __future__ import annotations

import argparse
import csv
from pathlib import Path

from PIL import Image, ImageDraw

from analyze_font_grid import parse_cell_size
from mig import decode_mig_indices, write_png_rgba


def main() -> int:
    parser = argparse.ArgumentParser(description="Render per-index layers from MIG font/candidate pages.")
    parser.add_argument("input", type=Path, nargs="?", default=Path("local/work/tdl_DATA001_0002"))
    parser.add_argument("--output-dir", type=Path, default=Path("local/work/mig_index_layers_v1"))
    parser.add_argument("--indexes", default="1-15", help="Palette indexes to render, e.g. 1-15 or 1,3,15.")
    args = parser.parse_args()

    paths = expand_inputs(args.input)
    indexes = parse_indexes(args.indexes)
    rows = render_index_layers(paths, indexes, args.output_dir)
    write_manifest(args.output_dir / "manifest.csv", rows)
    write_contact_sheet(args.output_dir / "contact_sheet.png", rows)
    write_readme(args.output_dir / "README.md", rows, indexes)
    print(f"wrote {args.output_dir}")
    return 0


def expand_inputs(path: Path) -> list[Path]:
    if path.is_dir():
        return sorted(candidate for candidate in path.glob("*.bin") if candidate.is_file())
    return [path]


def parse_indexes(value: str) -> list[int]:
    indexes: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = (int(piece, 0) for piece in part.split("-", 1))
            indexes.update(range(start, end + 1))
        else:
            indexes.add(int(part, 0))
    return sorted(index for index in indexes if 0 <= index <= 15)


def render_index_layers(paths: list[Path], indexes: list[int], output_dir: Path) -> list[dict[str, str]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    for page_index, path in enumerate(paths):
        width, height, indices = decode_mig_indices(path)
        cell_w, cell_h = parse_cell_size(path.stem)
        columns = width // cell_w
        grid_rows = height // cell_h
        for palette_index in indexes:
            mask = bytes(255 if value == palette_index else 0 for value in indices)
            ink_pixels = sum(1 for value in mask if value)
            occupied_cells = count_occupied_cells(mask, width, cell_w, cell_h, columns, grid_rows)
            output_name = f"{page_index:04d}_{path.stem}_idx{palette_index:02d}.png"
            write_mask_png(output_dir / output_name, width, height, mask)
            rows.append(
                {
                    "page_index": str(page_index),
                    "source": path.name,
                    "palette_index": str(palette_index),
                    "ink_pixels": str(ink_pixels),
                    "occupied_cells": str(occupied_cells),
                    "png": output_name,
                }
            )
    return rows


def count_occupied_cells(
    mask: bytes,
    width: int,
    cell_w: int,
    cell_h: int,
    columns: int,
    rows: int,
) -> int:
    occupied = 0
    for row in range(rows):
        for column in range(columns):
            found = False
            for y in range(row * cell_h, min((row + 1) * cell_h, len(mask) // width)):
                start = y * width + column * cell_w
                end = start + cell_w
                if any(mask[start:end]):
                    found = True
                    break
            if found:
                occupied += 1
    return occupied


def write_mask_png(path: Path, width: int, height: int, mask: bytes) -> None:
    rgba = bytearray()
    for value in mask:
        if value:
            rgba.extend((255, 255, 255, 255))
        else:
            rgba.extend((0, 0, 0, 0))
    write_png_rgba(path, width, height, bytes(rgba))


def write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_contact_sheet(path: Path, rows: list[dict[str, str]]) -> None:
    useful = [row for row in rows if int(row["ink_pixels"]) > 0]
    if not useful:
        return
    columns = 6
    tile_w = 128
    label_h = 34
    sheet_rows = (len(useful) + columns - 1) // columns
    sheet = Image.new("RGBA", (columns * tile_w, sheet_rows * (128 + label_h)), (20, 20, 20, 255))
    draw = ImageDraw.Draw(sheet)
    for index, row in enumerate(useful):
        image = Image.open(path.parent / row["png"]).convert("RGBA")
        x = (index % columns) * tile_w
        y = (index // columns) * (128 + label_h)
        sheet.alpha_composite(image, (x, y))
        label = f"{row['page_index']} idx{row['palette_index']} cells {row['occupied_cells']}"
        draw.text((x + 2, y + 130), label, fill=(255, 255, 255, 255))
    sheet.save(path)


def write_readme(path: Path, rows: list[dict[str, str]], indexes: list[int]) -> None:
    useful = [row for row in rows if int(row["ink_pixels"]) > 0]
    lines = [
        "# MIG Index Layers",
        "",
        "Purpose: render each palette-index layer separately. This detects hidden glyph layers that normal palette rendering may hide.",
        "",
        "## Summary",
        "",
        f"- Palette indexes scanned: {', '.join(str(index) for index in indexes)}",
        f"- Non-empty layers: {len(useful)}",
        "",
        "## Files",
        "",
        "- `manifest.csv`: per-page, per-index ink counts.",
        "- `contact_sheet.png`: non-empty index layers.",
        "",
        "## Non-Empty Layers",
        "",
        "| Page | Source | Index | Ink pixels | Occupied cells | PNG |",
        "| ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for row in useful:
        lines.append(
            f"| {row['page_index']} | `{row['source']}` | {row['palette_index']} | "
            f"{row['ink_pixels']} | {row['occupied_cells']} | `{row['png']}` |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
