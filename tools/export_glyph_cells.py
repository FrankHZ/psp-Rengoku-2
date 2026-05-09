from __future__ import annotations

import argparse
import csv
from pathlib import Path

from analyze_font_grid import expand_inputs, parse_cell_size
from mig import render_mig_rgba, write_png_rgba


def main() -> int:
    parser = argparse.ArgumentParser(description="Export individual glyph cells from supported MIG font pages.")
    parser.add_argument("input", type=Path, nargs="+", help="MIG files or directories containing MIG files.")
    parser.add_argument("output_dir", type=Path, help="Output directory for cell PNGs and manifest.csv.")
    parser.add_argument("--base-address", type=lambda value: int(value, 0), help="Optional runtime address for page 0.")
    parser.add_argument("--page-size", type=lambda value: int(value, 0), default=0x2100)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = args.output_dir / "manifest.csv"
    rows: list[dict[str, object]] = []

    for page_index, path in enumerate(expand_inputs(args.input)):
        rows.extend(export_page_cells(path, args.output_dir, page_index, args.base_address, args.page_size, args.overwrite))

    with manifest_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "page_index",
                "runtime_address",
                "source",
                "cell_index",
                "glyph_id_contiguous",
                "glyph_id_page100",
                "row",
                "col",
                "x",
                "y",
                "width",
                "height",
                "png",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"exported {len(rows)} cells to {args.output_dir}")
    return 0


def export_page_cells(
    path: Path,
    output_dir: Path,
    page_index: int,
    base_address: int | None,
    page_size: int,
    overwrite: bool,
) -> list[dict[str, object]]:
    width, height, rgba = render_mig_rgba(path)
    cell_w, cell_h = parse_cell_size(path.stem)
    cols = width // cell_w
    rows = height // cell_h
    page_dir = output_dir / path.stem
    page_dir.mkdir(parents=True, exist_ok=True)

    manifest_rows: list[dict[str, object]] = []
    for row in range(rows):
        for col in range(cols):
            cell_index = row * cols + col
            x = col * cell_w
            y = row * cell_h
            cell_rgba = crop_rgba(rgba, width, x, y, cell_w, cell_h)
            output_path = page_dir / f"cell_{cell_index:03d}_r{row:02d}_c{col:02d}.png"
            if output_path.exists() and not overwrite:
                raise FileExistsError(f"{output_path} exists; pass --overwrite")
            write_png_rgba(output_path, cell_w, cell_h, cell_rgba)
            runtime_address = "" if base_address is None else f"0x{base_address + page_index * page_size:08x}"
            manifest_rows.append(
                {
                    "page_index": page_index,
                    "runtime_address": runtime_address,
                    "source": path.name,
                    "cell_index": cell_index,
                    "glyph_id_contiguous": f"0x{glyph_id_contiguous(path.stem, page_index, cell_index):04x}",
                    "glyph_id_page100": f"0x{glyph_id_page100(path.stem, page_index, cell_index):04x}",
                    "row": row,
                    "col": col,
                    "x": x,
                    "y": y,
                    "width": cell_w,
                    "height": cell_h,
                    "png": output_path.relative_to(output_dir).as_posix(),
                }
            )
    return manifest_rows


def glyph_id_contiguous(stem: str, page_index: int, cell_index: int) -> int:
    if "codeANK" in stem:
        return cell_index
    return 126 + (page_index - 1) * 81 + cell_index


def glyph_id_page100(stem: str, page_index: int, cell_index: int) -> int:
    if "codeANK" in stem:
        return cell_index
    return page_index * 0x100 + cell_index


def crop_rgba(rgba: bytes, image_width: int, x: int, y: int, width: int, height: int) -> bytes:
    cropped = bytearray()
    stride = image_width * 4
    for row in range(y, y + height):
        start = row * stride + x * 4
        cropped.extend(rgba[start : start + width * 4])
    return bytes(cropped)


if __name__ == "__main__":
    raise SystemExit(main())
