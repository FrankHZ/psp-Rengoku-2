from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path

from mcd3 import read_mcd3
from PIL import Image, ImageDraw, ImageFont


DEFAULT_CREDIT_TEXT = "小方 oid Codex 汉化"
USRDIR_RELATIVE_PATH = Path("PSP_GAME") / "USRDIR"
MCD3_INDEX_NAME = "DATA000.BIN"
TITLE_ARCHIVE_NAME = "DATA002.BIN"
TITLE_PNG_ENTRY_ID = 112


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch a small credit line into the in-game title background PNG.")
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
            f" entry {TITLE_PNG_ENTRY_ID}"
        )
    return 0


def patch_title_credit(extracted_root: Path, text: str = DEFAULT_CREDIT_TEXT, dry_run: bool = False) -> None:
    usrdir = extracted_root / USRDIR_RELATIVE_PATH
    index = read_mcd3(usrdir / MCD3_INDEX_NAME)
    entry = index.entries[TITLE_PNG_ENTRY_ID]
    if entry.archive_name != TITLE_ARCHIVE_NAME:
        raise ValueError(
            f"expected entry {TITLE_PNG_ENTRY_ID} in {TITLE_ARCHIVE_NAME}, got {entry.archive_name!r}"
        )

    target = usrdir / TITLE_ARCHIVE_NAME
    archive = bytearray(target.read_bytes())
    if entry.end_offset > len(archive):
        raise ValueError(f"entry {TITLE_PNG_ENTRY_ID} extends past {target}")

    original_png = bytes(archive[entry.offset : entry.end_offset])
    image = Image.open(BytesIO(original_png)).convert("RGBA")
    if image.size != (480, 272):
        raise ValueError(f"expected title PNG to be 480x272, got {image.size[0]}x{image.size[1]}")

    draw_credit(image, text)
    if not dry_run:
        buffer = BytesIO()
        image.convert("RGB").save(buffer, format="PNG", optimize=True)
        patched_png = buffer.getvalue()
        if len(patched_png) > entry.size:
            raise ValueError(
                f"patched title PNG is {len(patched_png)} bytes, larger than entry {TITLE_PNG_ENTRY_ID} size {entry.size}"
            )
        archive[entry.offset : entry.end_offset] = patched_png + b"\x00" * (entry.size - len(patched_png))
        target.write_bytes(archive)


def draw_credit(image: Image.Image, text: str) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    font = load_font(13)
    x = 8
    # The title PNG is uploaded into a 512x256 runtime texture whose visible
    # title band starts below the top edge; keep the credit inside that band.
    y = 42
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
