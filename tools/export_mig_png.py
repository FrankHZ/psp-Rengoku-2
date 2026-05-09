from __future__ import annotations

import argparse
from pathlib import Path

from mig import render_mig_rgba, write_png_rgba


def main() -> int:
    parser = argparse.ArgumentParser(description="Export supported MIG.00.1PSP textures to PNG.")
    parser.add_argument("input", type=Path, nargs="+", help="MIG files or directories containing MIG files.")
    parser.add_argument("output_dir", type=Path, help="Output directory for PNG files.")
    parser.add_argument("--palette-mode", choices=("rgba", "abgr", "bgra"), default="rgba")
    parser.add_argument("--debug-contrast", action="store_true", help="Export white glyph indices on transparent background.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing PNG files.")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for input_path in expand_inputs(args.input):
        width, height, rgba = render_mig_rgba(
            input_path,
            palette_mode=args.palette_mode,
            debug_contrast=args.debug_contrast,
        )
        output_path = args.output_dir / f"{input_path.stem}.png"
        if output_path.exists() and not args.overwrite:
            raise FileExistsError(f"{output_path} exists; pass --overwrite")
        write_png_rgba(output_path, width, height, rgba)
        count += 1

    print(f"exported {count} PNG files to {args.output_dir}")
    return 0


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
