from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

from analyze_font_grid import expand_inputs, parse_cell_size, cell_has_ink
from export_glyph_cells import glyph_id_contiguous, glyph_id_page100
from mig import decode_mig_indices


def inventory_font_cells(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for page_index, path in enumerate(expand_inputs(paths)):
        rows.extend(inventory_page_cells(path, page_index))
    return rows


def inventory_page_cells(path: Path, page_index: int) -> list[dict[str, Any]]:
    cell_w, cell_h = parse_cell_size(path.stem)
    width, height, indices = decode_mig_indices(path)
    cols = width // cell_w
    rows = height // cell_h

    result: list[dict[str, Any]] = []
    for row in range(rows):
        for col in range(cols):
            cell_index = row * cols + col
            x = col * cell_w
            y = row * cell_h
            has_ink = cell_has_ink(indices, width, x, y, cell_w, cell_h)
            result.append(
                {
                    "page_index": page_index,
                    "source": path.name,
                    "cell_index": cell_index,
                    "row": row,
                    "col": col,
                    "x": x,
                    "y": y,
                    "width": cell_w,
                    "height": cell_h,
                    "has_ink": has_ink,
                    "glyph_id_contiguous": f"0x{glyph_id_contiguous(path.stem, page_index, cell_index):04x}",
                    "glyph_id_page100": f"0x{glyph_id_page100(path.stem, page_index, cell_index):04x}",
                }
            )
    return result


def write_csv(rows: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "page_index",
        "source",
        "cell_index",
        "row",
        "col",
        "x",
        "y",
        "width",
        "height",
        "has_ink",
        "glyph_id_contiguous",
        "glyph_id_page100",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory occupied and empty cells in supported MIG font pages.")
    parser.add_argument("input", type=Path, nargs="+", help="MIG files or directories containing MIG files.")
    parser.add_argument("--output", type=Path, help="Optional CSV output path.")
    parser.add_argument("--empty-only", action="store_true", help="Only print/write empty cells.")
    args = parser.parse_args()

    rows = inventory_font_cells(args.input)
    if args.empty_only:
        rows = [row for row in rows if not row["has_ink"]]

    if args.output:
        write_csv(rows, args.output)

    print("page\tsource\tcell\trow\tcol\thas_ink\tglyph_id_contiguous\tglyph_id_page100")
    for row in rows:
        print(
            f"{row['page_index']}\t{row['source']}\t{row['cell_index']}\t{row['row']}\t{row['col']}\t"
            f"{int(bool(row['has_ink']))}\t{row['glyph_id_contiguous']}\t{row['glyph_id_page100']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
