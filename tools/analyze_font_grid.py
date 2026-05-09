from __future__ import annotations

import argparse
import re
from pathlib import Path

from mig import decode_mig_indices


FONT_NAME_RE = re.compile(r"code(?:ANK|JAP)(\d+)x(\d+)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze nonempty glyph cells in rendered/extracted MIG font pages.")
    parser.add_argument("input", type=Path, nargs="+", help="MIG files or directories containing MIG files.")
    args = parser.parse_args()

    print("file\twidth\theight\tcell_w\tcell_h\tcols\trows\tcapacity\tnonempty\tleftover_x\tleftover_y")
    for path in expand_inputs(args.input):
        result = analyze_font_grid(path)
        print(
            f"{path.name}\t{result['width']}\t{result['height']}\t{result['cell_w']}\t{result['cell_h']}\t"
            f"{result['cols']}\t{result['rows']}\t{result['capacity']}\t{result['nonempty']}\t"
            f"{result['leftover_x']}\t{result['leftover_y']}"
        )
    return 0


def analyze_font_grid(path: Path) -> dict[str, int]:
    cell_w, cell_h = parse_cell_size(path.stem)
    width, height, indices = decode_mig_indices(path)
    cols = width // cell_w
    rows = height // cell_h
    nonempty = 0
    for row in range(rows):
        for col in range(cols):
            if cell_has_ink(indices, width, col * cell_w, row * cell_h, cell_w, cell_h):
                nonempty += 1

    return {
        "width": width,
        "height": height,
        "cell_w": cell_w,
        "cell_h": cell_h,
        "cols": cols,
        "rows": rows,
        "capacity": cols * rows,
        "nonempty": nonempty,
        "leftover_x": width - cols * cell_w,
        "leftover_y": height - rows * cell_h,
    }


def parse_cell_size(name: str) -> tuple[int, int]:
    match = FONT_NAME_RE.search(name)
    if not match:
        raise ValueError(f"cannot infer font cell size from {name}")
    return int(match.group(1)), int(match.group(2))


def cell_has_ink(indices: bytes, image_width: int, x: int, y: int, width: int, height: int) -> bool:
    for row in range(y, y + height):
        start = row * image_width + x
        if any(index != 0 for index in indices[start : start + width]):
            return True
    return False


def expand_inputs(paths: list[Path]) -> list[Path]:
    expanded: list[Path] = []
    for path in paths:
        if path.is_dir():
            expanded.extend(sorted(child for child in path.glob("*.bin") if child.is_file()))
        elif path.is_file():
            expanded.append(path)
        else:
            raise FileNotFoundError(path)
    return expanded


if __name__ == "__main__":
    raise SystemExit(main())
