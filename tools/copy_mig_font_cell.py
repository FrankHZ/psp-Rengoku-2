from __future__ import annotations

import argparse
from pathlib import Path

from analyze_font_grid import parse_cell_size
from mig import decode_mig_indices, replace_mig_indices


def copy_font_cell(
    source_page: Path,
    source_cell: int,
    target_page: Path,
    target_cell: int,
    output_path: Path,
) -> None:
    source_cell_w, source_cell_h = parse_cell_size(source_page.stem)
    target_cell_w, target_cell_h = parse_cell_size(target_page.stem)
    if (source_cell_w, source_cell_h) != (target_cell_w, target_cell_h):
        raise ValueError("source and target font cells must have the same dimensions")

    source_w, source_h, source_indices = decode_mig_indices(source_page)
    target_w, target_h, target_indices = decode_mig_indices(target_page)
    if (source_w, source_h) != (target_w, target_h):
        raise ValueError("source and target pages must have the same dimensions")

    cell_w = source_cell_w
    cell_h = source_cell_h
    cols = source_w // cell_w
    capacity = cols * (source_h // cell_h)
    for label, cell in (("source", source_cell), ("target", target_cell)):
        if cell < 0 or cell >= capacity:
            raise ValueError(f"{label} cell {cell} is outside page capacity {capacity}")

    source_x = (source_cell % cols) * cell_w
    source_y = (source_cell // cols) * cell_h
    target_x = (target_cell % cols) * cell_w
    target_y = (target_cell // cols) * cell_h

    output = bytearray(target_indices)
    for y in range(cell_h):
        source_start = (source_y + y) * source_w + source_x
        source_end = source_start + cell_w
        target_start = (target_y + y) * target_w + target_x
        output[target_start : target_start + cell_w] = source_indices[source_start:source_end]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    replace_mig_indices(target_page, bytes(output), output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Copy one glyph cell between compatible 4bpp MIG font pages.")
    parser.add_argument("source_page", type=Path)
    parser.add_argument("source_cell", type=int)
    parser.add_argument("target_page", type=Path)
    parser.add_argument("target_cell", type=int)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    copy_font_cell(args.source_page, args.source_cell, args.target_page, args.target_cell, args.output)
    print(f"copied {args.source_page} cell {args.source_cell} -> {args.output} cell {args.target_cell}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
