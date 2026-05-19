from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


DEFAULT_CREDIT_TEXT = "CHS PATCH v43"
PIC1_RELATIVE_PATH = Path("PSP_GAME") / "PIC1.PNG"


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch a small credit line into the PSP title background PIC1.PNG.")
    parser.add_argument("extracted_root", type=Path, help="PPSSPP-ready extracted build root.")
    parser.add_argument("--text", default=DEFAULT_CREDIT_TEXT, help="ASCII credit text to draw.")
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
    font = load_font(12)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = image.width - text_w - 12
    y = image.height - text_h - 10
    pad_x = 5
    pad_y = 3
    draw.rounded_rectangle(
        (x - pad_x, y - pad_y, x + text_w + pad_x, y + text_h + pad_y),
        radius=3,
        fill=(0, 0, 0, 96),
    )
    draw.text((x, y), text, font=font, fill=(218, 230, 246, 210))


def load_font(size: int) -> ImageFont.ImageFont:
    for path in (
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ):
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


if __name__ == "__main__":
    raise SystemExit(main())
