from __future__ import annotations

import argparse
from pathlib import Path

from mcd3 import read_mcd3
from mig import swizzle_texture_bytes, unswizzle_texture_bytes
from PIL import Image, ImageDraw, ImageFont
from render_mig_font_cell import render_bmfont_glyph_mask
from tdl import read_tdl_bytes


DEFAULT_CREDIT_TEXT = "小方 oid Codex 汉化"
DEFAULT_CREDIT_FONT = Path("local/fonts/full-semibold-18.fnt")
DEFAULT_ANK_FONT_PAGE = Path("local/work/tdl_DATA001_0002/0000_codeANK9x14_00_0.bin")
USRDIR_RELATIVE_PATH = Path("PSP_GAME") / "USRDIR"
MCD3_INDEX_NAME = "DATA000.BIN"
TITLE_ARCHIVE_NAME = "DATA001.BIN"
FONT_TDL_ENTRY_ID = 2
ANK_FONT_CHILD_INDEX = 0
TITLE_TDL_ENTRY_ID = 4
TITLE_TLOGO_CHILD_INDEX = 0
TITLE_TLOGO_PIXEL_OFFSET = 0x80
TITLE_TLOGO_WIDTH = 512
TITLE_TLOGO_HEIGHT = 256
TITLE_TLOGO_INK_INDEX = 0xFF
TITLE_TLOGO_WHITE_ALPHA_INDICES = (
    (236, 11),
    (238, 33),
    (241, 71),
    (244, 111),
    (246, 153),
    (249, 199),
    (251, 233),
    (255, 255),
)


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
            f" entry {TITLE_TDL_ENTRY_ID} child {TITLE_TLOGO_CHILD_INDEX}"
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
    tdl = read_tdl_bytes(bytes(tdl_data), Path("<DATA001/0004>"))
    child = tdl.entries[TITLE_TLOGO_CHILD_INDEX]
    if child.name != "tlogo":
        raise ValueError(f"expected child {TITLE_TLOGO_CHILD_INDEX} to be tlogo, got {child.name!r}")

    mig_data = bytearray(tdl_data[child.offset : child.end_offset])
    pixel_size = TITLE_TLOGO_WIDTH * TITLE_TLOGO_HEIGHT
    pixel_end = TITLE_TLOGO_PIXEL_OFFSET + pixel_size
    if pixel_end > len(mig_data):
        raise ValueError("tlogo pixel data extends past MIG child")

    linear = bytearray(
        unswizzle_texture_bytes(
            bytes(mig_data[TITLE_TLOGO_PIXEL_OFFSET:pixel_end]),
            width_bytes=TITLE_TLOGO_WIDTH,
            height=TITLE_TLOGO_HEIGHT,
        )
    )

    mask = Image.new("L", (TITLE_TLOGO_WIDTH, TITLE_TLOGO_HEIGHT), 0)
    ank_indices = extract_ank_font_indices(bytes(archive), index)
    draw_credit_mask(mask, text, ank_indices)
    mask_pixels = mask.tobytes()
    for index, alpha in enumerate(mask_pixels):
        if alpha:
            linear[index] = alpha_to_tlogo_white_index(alpha)

    mig_data[TITLE_TLOGO_PIXEL_OFFSET:pixel_end] = swizzle_texture_bytes(
        bytes(linear),
        width_bytes=TITLE_TLOGO_WIDTH,
        height=TITLE_TLOGO_HEIGHT,
    )
    tdl_data[child.offset : child.end_offset] = mig_data

    if not dry_run:
        archive[entry.offset : entry.end_offset] = tdl_data
        target.write_bytes(archive)


def draw_credit_mask(mask: Image.Image, text: str, ank_indices: tuple[int, int, bytes] | None = None) -> None:
    x = 8
    y = 234
    if ank_indices is None:
        ank_indices = load_default_ank_font_indices()
    draw_bmfont_credit(mask, text, x, y, ank_indices)


def draw_bmfont_credit(mask: Image.Image, text: str, x: int, y: int, ank_indices: tuple[int, int, bytes] | None) -> None:
    cursor_x = x
    ascii_font = load_ascii_font(11)
    ascii_draw = ImageDraw.Draw(mask)
    for char in text:
        if char == " ":
            cursor_x += 4
            continue
        if is_cjk_ideograph(char):
            glyph = render_bmfont_glyph_mask(char, DEFAULT_CREDIT_FONT, 14, 14, 0, -2, 13)
            mask.paste(glyph, (cursor_x, y))
            cursor_x += 13
            continue
        if ank_indices is not None and 0x20 <= ord(char) <= 0x7D:
            glyph = render_ank_glyph_mask(char, ank_indices)
            mask.paste(glyph, (cursor_x, y - 1))
            cursor_x += ank_glyph_advance(glyph)
            continue
        bbox = ascii_draw.textbbox((0, 0), char, font=ascii_font)
        ascii_draw.text((cursor_x, y + 2), char, font=ascii_font, fill=255)
        cursor_x += max(1, bbox[2] - bbox[0]) + 1


def alpha_to_tlogo_white_index(alpha: int) -> int:
    for index, threshold in TITLE_TLOGO_WHITE_ALPHA_INDICES:
        if alpha <= threshold:
            return index
    return TITLE_TLOGO_INK_INDEX


def is_cjk_ideograph(char: str) -> bool:
    codepoint = ord(char)
    return 0x3400 <= codepoint <= 0x9FFF or 0xF900 <= codepoint <= 0xFAFF


def extract_ank_font_indices(data001_archive: bytes, index) -> tuple[int, int, bytes]:
    entry = index.entries[FONT_TDL_ENTRY_ID]
    if entry.archive_name != TITLE_ARCHIVE_NAME:
        raise ValueError(f"expected font entry {FONT_TDL_ENTRY_ID} in {TITLE_ARCHIVE_NAME}, got {entry.archive_name!r}")
    tdl_data = data001_archive[entry.offset : entry.end_offset]
    tdl = read_tdl_bytes(tdl_data, Path("<DATA001/0002>"))
    child = tdl.entries[ANK_FONT_CHILD_INDEX]
    if child.name != "codeANK9x14_00_0":
        raise ValueError(f"expected child {ANK_FONT_CHILD_INDEX} to be codeANK9x14_00_0, got {child.name!r}")
    return decode_4bpp_mig_indices(tdl_data[child.offset : child.end_offset])


def load_default_ank_font_indices() -> tuple[int, int, bytes] | None:
    if not DEFAULT_ANK_FONT_PAGE.exists():
        return None
    return decode_4bpp_mig_indices(DEFAULT_ANK_FONT_PAGE.read_bytes())


def decode_4bpp_mig_indices(mig_data: bytes) -> tuple[int, int, bytes]:
    if not mig_data.startswith(b"MIG.00.1PSP"):
        raise ValueError("expected MIG.00.1PSP ANK font page")
    width = int.from_bytes(mig_data[0xD8:0xDA], "little")
    height = int.from_bytes(mig_data[0xDA:0xDC], "little")
    if width == 0 or height == 0:
        raise ValueError("ANK font page does not declare dimensions")
    pixel_size = width * height // 2
    pixel_offset = len(mig_data) - pixel_size
    packed = unswizzle_texture_bytes(mig_data[pixel_offset : pixel_offset + pixel_size], width // 2, height)
    indices = bytearray()
    for value in packed:
        indices.extend((value & 0x0F, value >> 4))
    return width, height, bytes(indices)


def render_ank_glyph_mask(char: str, ank_indices: tuple[int, int, bytes]) -> Image.Image:
    texture_width, _texture_height, indices = ank_indices
    cell = ord(char) - 0x20
    col = cell % 14
    row = cell // 14
    glyph = Image.new("L", (9, 14), 0)
    pixels = glyph.load()
    for y in range(14):
        for x in range(9):
            value = indices[(row * 14 + y) * texture_width + (col * 9 + x)] & 0x03
            if value:
                pixels[x, y] = value * 85
    return glyph


def ank_glyph_advance(glyph: Image.Image) -> int:
    bbox = glyph.getbbox()
    if bbox is None:
        return 4
    width = bbox[2] - bbox[0]
    return min(9, max(3, width + 1))


def draw_credit(image: Image.Image, text: str) -> None:
    mask = Image.new("L", image.size, 0)
    draw_credit_mask(mask, text)
    draw = ImageDraw.Draw(image, "RGBA")
    for y in range(image.height):
        for x in range(image.width):
            if mask.getpixel((x, y)):
                draw.point((x, y), fill=(245, 248, 255, 230))


def load_ascii_font(size: int) -> ImageFont.ImageFont:
    for path in (
        Path("C:/Windows/Fonts/seguisb.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ):
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


if __name__ == "__main__":
    raise SystemExit(main())
