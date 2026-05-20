from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


PIC0_RELATIVE_PATH = Path("PSP_GAME") / "PIC0.PNG"


def main() -> int:
    parser = argparse.ArgumentParser(description="Replace PSP_GAME/PIC0.PNG in a staged PSP extracted build.")
    parser.add_argument("extracted_root", type=Path, help="PPSSPP-ready extracted build root.")
    parser.add_argument("replacement_png", type=Path, help="Replacement 320x180 PNG.")
    parser.add_argument("--output", type=Path, help="Optional output PNG path. Defaults to PSP_GAME/PIC0.PNG in-place.")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs without writing.")
    args = parser.parse_args()

    target = patch_pic0(args.extracted_root, args.replacement_png, output=args.output, dry_run=args.dry_run)
    if args.dry_run:
        print(f"dry run: {args.replacement_png} is a valid PIC0 replacement")
    else:
        print(f"wrote {target}")
    return 0


def patch_pic0(
    extracted_root: Path,
    replacement_png: Path,
    *,
    output: Path | None = None,
    dry_run: bool = False,
) -> Path:
    target = output if output is not None else extracted_root / PIC0_RELATIVE_PATH
    source_target = extracted_root / PIC0_RELATIVE_PATH
    if not source_target.exists():
        raise FileNotFoundError(f"missing staged PIC0 target: {source_target}")

    expected_size = read_png_size(source_target)
    validate_pic0_replacement(replacement_png, expected_size)
    if dry_run:
        return target

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(replacement_png.read_bytes())
    return target


def validate_pic0_replacement(path: Path, expected_size: tuple[int, int] | None = None) -> Image.Image:
    if not path.exists():
        raise FileNotFoundError(path)
    with Image.open(path) as image:
        if expected_size is not None and image.size != expected_size:
            raise ValueError(
                f"PIC0 replacement must be {expected_size[0]}x{expected_size[1]}, "
                f"got {image.size[0]}x{image.size[1]}"
            )
        if image.format != "PNG":
            raise ValueError(f"PIC0 replacement must be a PNG, got {image.format or 'unknown'}")
        return image.convert("RGBA")


def read_png_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        if image.format != "PNG":
            raise ValueError(f"staged PIC0 target must be a PNG, got {image.format or 'unknown'}")
        return image.size


if __name__ == "__main__":
    raise SystemExit(main())
