from __future__ import annotations

import argparse
from pathlib import Path

from mcd3 import read_mcd3
from mig import swizzle_texture_bytes, unswizzle_texture_bytes
from PIL import Image, ImageDraw, ImageFont
from tdl import read_tdl_bytes


DEFAULT_CREDIT_TEXT = "小方 oid Codex 汉化"
USRDIR_RELATIVE_PATH = Path("PSP_GAME") / "USRDIR"
MCD3_INDEX_NAME = "DATA000.BIN"
TITLE_ARCHIVE_NAME = "DATA001.BIN"
TITLE_TDL_ENTRY_ID = 6
TITLE_TBACK_CHILD_INDEX = 0
TITLE_TBACK_PIXEL_OFFSET = 0x450
TITLE_TBACK_WIDTH = 512
TITLE_TBACK_HEIGHT = 256
TITLE_TBACK_INK_INDEX = 0xF0


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch a small credit line into the in-game title background texture.")
    parser.add_argument("extracted_root", type=Path, help="PPSSPP-ready extracted build root.")
    parser.add_argument("--text", default=DEFAULT_CREDIT_TEXT, help="Credit text to draw.")
    parser.add_argument("--dry-run", action="store_true", help="Validate the target image without writing.")
    args = parser.parse_args()

    patch_title_credit(args.extracted_root, args.text, dry_run=args.dry_run)
    if args.dry_run:
        print("dry run: no file written")
    else:
        print(
            "patched title credit in "
            f"{args.extracted_root / USRDIR_RELATIVE_PATH / TITLE_ARCHIVE_NAME}"
            f" entry {TITLE_TDL_ENTRY_ID} child {TITLE_TBACK_CHILD_INDEX}"
        )
    return 0


def patch_title_credit(extracted_root: Path, text: str = DEFAULT_CREDIT_TEXT, dry_run: bool = False) -> None:
    usrdir = extracted_root / USRDIR_RELATIVE_PATH
    index = read_mcd3(usrdir / MCD3_INDEX_NAME)
    entry = index.entries[TITLE_TDL_ENTRY_ID]
    if entry.archive_name != TITLE_ARCHIVE_NAME:
        raise ValueError(
            f"expected entry {TITLE_TDL_ENTRY_ID} in {TITLE_ARCHIVE_NAME}, got {entry.archive_name!r}"
        )

    target = usrdir / TITLE_ARCHIVE_NAME
    archive = bytearray(target.read_bytes())
    if entry.end_offset > len(archive):
        raise ValueError(f"entry {TITLE_TDL_ENTRY_ID} extends past {target}")

    tdl_data = bytearray(archive[entry.offset : entry.end_offset])
    tdl = read_tdl_bytes(bytes(tdl_data), Path("<DATA001/0006>"))
    child = tdl.entries[TITLE_TBACK_CHILD_INDEX]
    if child.name != "tback":
        raise ValueError(f"expected child {TITLE_TBACK_CHILD_INDEX} to be tback, got {child.name!r}")

    mig_data = bytearray(tdl_data[child.offset : child.end_offset])
    pixel_size = TITLE_TBACK_WIDTH * TITLE_TBACK_HEIGHT
    pixel_end = TITLE_TBACK_PIXEL_OFFSET + pixel_size
    if pixel_end > len(mig_data):
        raise ValueError("tback pixel data extends past MIG child")

    linear = bytearray(
        unswizzle_texture_bytes(
            bytes(mig_data[TITLE_TBACK_PIXEL_OFFSET:pixel_end]),
            width_bytes=TITLE_TBACK_WIDTH,
            height=TITLE_TBACK_HEIGHT,
        )
    )

    mask = Image.new("L", (TITLE_TBACK_WIDTH, TITLE_TBACK_HEIGHT), 0)
    draw_credit_mask(mask, text)
    mask_pixels = mask.tobytes()
    for index, alpha in enumerate(mask_pixels):
        if alpha:
            linear[index] = TITLE_TBACK_INK_INDEX

    mig_data[TITLE_TBACK_PIXEL_OFFSET:pixel_end] = swizzle_texture_bytes(
        bytes(linear),
        width_bytes=TITLE_TBACK_WIDTH,
        height=TITLE_TBACK_HEIGHT,
    )
    tdl_data[child.offset : child.end_offset] = mig_data

    if not dry_run:
        archive[entry.offset : entry.end_offset] = tdl_data
        target.write_bytes(archive)


def draw_credit_mask(mask: Image.Image, text: str) -> None:
    draw = ImageDraw.Draw(mask)
    font = load_font(13)
    x = 8
    y = 38
    draw.text((x, y), text, font=font, fill=255)


def draw_credit(image: Image.Image, text: str) -> None:
    mask = Image.new("L", image.size, 0)
    draw_credit_mask(mask, text)
    draw = ImageDraw.Draw(image, "RGBA")
    for y in range(image.height):
        for x in range(image.width):
            if mask.getpixel((x, y)):
                draw.point((x, y), fill=(245, 248, 255, 230))


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
