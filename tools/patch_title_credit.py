from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from mcd3 import read_mcd3
from mig import swizzle_texture_bytes, unswizzle_texture_bytes
from tdl import read_tdl_bytes


TITLE_ENTRY_ID = 6
TITLE_BACK_CHILD = 0
TITLE_BACK_WIDTH = 128
TITLE_BACK_HEIGHT = 256
TITLE_BACK_PIXEL_OFFSET = 0x4D0
DEFAULT_CREDIT_TEXT = "CHS PATCH v43"


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch a small credit line into Rengoku 2 title background texture.")
    parser.add_argument("extracted_root", type=Path, help="PPSSPP-ready extracted build root.")
    parser.add_argument("--text", default=DEFAULT_CREDIT_TEXT, help="ASCII credit text to draw.")
    parser.add_argument("--dry-run", action="store_true", help="Validate target offsets without writing.")
    args = parser.parse_args()

    patch_title_credit(args.extracted_root, args.text, dry_run=args.dry_run)
    if args.dry_run:
        print("dry run: no file written")
    else:
        print(f"patched title credit in {args.extracted_root}")
    return 0


def patch_title_credit(extracted_root: Path, text: str = DEFAULT_CREDIT_TEXT, dry_run: bool = False) -> None:
    usrdir = extracted_root / "PSP_GAME" / "USRDIR"
    index_path = usrdir / "DATA000.BIN"
    archive_path = usrdir / "DATA001.BIN"
    index = read_mcd3(index_path)
    entry = index.entries[TITLE_ENTRY_ID]
    if entry.archive_name != "DATA001.BIN":
        raise ValueError(f"entry {TITLE_ENTRY_ID} is not in DATA001.BIN")

    archive = bytearray(archive_path.read_bytes())
    title_tdl = bytearray(archive[entry.offset : entry.end_offset])
    tdl = read_tdl_bytes(bytes(title_tdl), Path("DATA001/0006_tdl.bin"))
    child = tdl.entries[TITLE_BACK_CHILD]
    if child.name != "tback":
        raise ValueError(f"expected child {TITLE_BACK_CHILD} to be tback, got {child.name!r}")
    if child.size < TITLE_BACK_PIXEL_OFFSET + TITLE_BACK_WIDTH * TITLE_BACK_HEIGHT * 4:
        raise ValueError("tback child is too small for expected 128x256x32bpp texture")

    start = child.offset + TITLE_BACK_PIXEL_OFFSET
    end = start + TITLE_BACK_WIDTH * TITLE_BACK_HEIGHT * 4
    swizzled = bytes(title_tdl[start:end])
    linear = unswizzle_texture_bytes(swizzled, width_bytes=TITLE_BACK_WIDTH * 4, height=TITLE_BACK_HEIGHT)
    image = Image.frombytes("RGBA", (TITLE_BACK_WIDTH, TITLE_BACK_HEIGHT), abgr_to_rgba(linear))
    draw_credit(image, text)
    patched_linear = rgba_to_abgr(image.tobytes())
    title_tdl[start:end] = swizzle_texture_bytes(
        patched_linear,
        width_bytes=TITLE_BACK_WIDTH * 4,
        height=TITLE_BACK_HEIGHT,
    )

    if dry_run:
        return
    archive[entry.offset : entry.end_offset] = title_tdl
    archive_path.write_bytes(archive)


def draw_credit(image: Image.Image, text: str) -> None:
    draw = ImageDraw.Draw(image)
    font = load_font(9)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = max(2, image.width - text_w - 4)
    y = image.height - text_h - 8
    pad = 2
    draw.rectangle(
        (x - pad, y - pad, x + text_w + pad, y + text_h + pad),
        fill=(0, 0, 0, 112),
    )
    draw.text((x, y), text, font=font, fill=(220, 235, 255, 224))


def load_font(size: int) -> ImageFont.ImageFont:
    for path in (
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
    ):
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def abgr_to_rgba(data: bytes) -> bytes:
    output = bytearray(len(data))
    for offset in range(0, len(data), 4):
        alpha, blue, green, red = data[offset : offset + 4]
        output[offset : offset + 4] = bytes((red, green, blue, alpha))
    return bytes(output)


def rgba_to_abgr(data: bytes) -> bytes:
    output = bytearray(len(data))
    for offset in range(0, len(data), 4):
        red, green, blue, alpha = data[offset : offset + 4]
        output[offset : offset + 4] = bytes((alpha, blue, green, red))
    return bytes(output)


if __name__ == "__main__":
    raise SystemExit(main())
