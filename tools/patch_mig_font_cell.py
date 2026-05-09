from __future__ import annotations

import argparse
from pathlib import Path

from analyze_font_grid import parse_cell_size
from mig import decode_mig_indices, replace_mig_indices


PATTERNS = ("box", "cross", "slash", "filled")


def patch_font_cell(
    source_path: Path,
    output_path: Path,
    cell_index: int,
    pattern: str,
    ink_index: int = 15,
) -> None:
    patch_font_cells(source_path, output_path, [cell_index], pattern, ink_index)


def patch_font_cells(
    source_path: Path,
    output_path: Path,
    cell_indices: list[int],
    pattern: str,
    ink_index: int = 15,
) -> None:
    if pattern not in PATTERNS:
        raise ValueError(f"unsupported pattern {pattern!r}")
    if ink_index < 1 or ink_index > 15:
        raise ValueError("ink index must be in range 1..15")

    cell_w, cell_h = parse_cell_size(source_path.stem)
    image_w, image_h, original = decode_mig_indices(source_path)
    cols = image_w // cell_w
    rows = image_h // cell_h
    capacity = cols * rows
    for cell_index in cell_indices:
        if cell_index < 0 or cell_index >= capacity:
            raise ValueError(f"cell index {cell_index} is outside page capacity {capacity}")

    indices = bytearray(original)
    for cell_index in cell_indices:
        cell_row = cell_index // cols
        cell_col = cell_index % cols
        x0 = cell_col * cell_w
        y0 = cell_row * cell_h

        for y in range(cell_h):
            for x in range(cell_w):
                if pattern_pixel(pattern, x, y, cell_w, cell_h):
                    indices[(y0 + y) * image_w + x0 + x] = ink_index
                else:
                    indices[(y0 + y) * image_w + x0 + x] = 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    replace_mig_indices(source_path, bytes(indices), output_path)


def parse_cell_range(value: str) -> list[int]:
    cells: list[int] = []
    for part in value.replace(",", " ").split():
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            start = int(start_text, 0)
            end = int(end_text, 0)
            if end < start:
                raise ValueError(f"cell range end is before start: {part}")
            cells.extend(range(start, end + 1))
        else:
            cells.append(int(part, 0))
    return cells


def pattern_pixel(pattern: str, x: int, y: int, width: int, height: int) -> bool:
    if pattern == "filled":
        return 1 <= x < width - 1 and 1 <= y < height - 1
    if pattern == "box":
        return x in (1, width - 2) or y in (1, height - 2)
    if pattern == "cross":
        return x == y or x == width - y - 1
    if pattern == "slash":
        return x == width - y - 1 or x == width - y - 2
    raise ValueError(f"unsupported pattern {pattern!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch one cell in a 4bpp MIG font page with a test pattern.")
    parser.add_argument("source", type=Path, help="Source MIG font page.")
    parser.add_argument("output", type=Path, help="Output MIG font page.")
    parser.add_argument("--cell", type=int, help="Cell index to replace.")
    parser.add_argument("--cells", help="Cell indexes/ranges to replace, such as '0-20,33'.")
    parser.add_argument("--pattern", choices=PATTERNS, default="box")
    parser.add_argument("--ink-index", type=int, default=15, help="4bpp palette index for the test mark.")
    args = parser.parse_args()

    if args.cell is None and not args.cells:
        parser.error("one of --cell or --cells is required")

    cells = []
    if args.cell is not None:
        cells.append(args.cell)
    if args.cells:
        cells.extend(parse_cell_range(args.cells))

    patch_font_cells(args.source, args.output, sorted(set(cells)), args.pattern, args.ink_index)
    print(f"patched {args.source} cells {','.join(str(cell) for cell in sorted(set(cells)))} -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
