from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


DEFAULT_CREDIT_TEXT = "小方 oid Codex 汉化"
PIC1_RELATIVE_PATH = Path("PSP_GAME") / "PIC1.PNG"


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch a small credit line into the PSP title background PIC1.PNG.")
    parser.add_argument("extracted_root", type=Path, help="PPSSPP-ready extracted build root.")
    parser.add_argument("--text", default=DEFAULT_CREDIT_TEXT, help="Credit text to draw.")
    parser.add_argument("--dry-run", action="store_true", help="Validate the target image without writing.")
    args = parser.parse_args()

    patch_title_credit(args.extracted_root, args.text, dry_run=args.dry_run)
    if args.dry_run:
        print("dry run: no file written")
    else:
        print(f"patched title credit in {args.extracted_root / PIC1_RELATIVE_PATH}")
    return 0


def patch_title_credit(extracted_root: Path, text: str = DEFAULT_CREDIT_TEXT, dry_run: bool = False) -> None:
    target = extracted_root / PIC1_RELATIVE_PATH
    if not target.exists():
        raise FileNotFoundError(target)

    image = Image.open(target).convert("RGBA")
    if image.size != (480, 272):
        raise ValueError(f"expected PIC1.PNG to be 480x272, got {image.size[0]}x{image.size[1]}")

    draw_credit(image, text)
    if not dry_run:
        image.convert("RGB").save(target, format="PNG", optimize=True)


def draw_credit(image: Image.Image, text: str) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    font = load_font(13)
    x = 8
    y = 7
    draw.text((x + 1, y + 1), text, font=font, fill=(0, 0, 0, 96))
    draw.text((x, y), text, font=font, fill=(245, 248, 255, 230))


def load_font(size: int) -> ImageFont.ImageFont:
    for path in (
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/simsun.ttc"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ):
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


if __name__ == "__main__":
    raise SystemExit(main())
