from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
import struct


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory PPSSPP dumped texture PNGs.")
    parser.add_argument("dump_dir", type=Path, help="Directory containing dumped texture PNG files.")
    parser.add_argument("--page-size", type=lambda value: int(value, 0), default=0x2100)
    args = parser.parse_args()

    files = sorted(args.dump_dir.glob("*.png"))
    by_address: dict[int, list[Path]] = defaultdict(list)
    for path in files:
        by_address[int(path.name[:8], 16)].append(path)

    min_address = min(by_address) if by_address else 0
    print("address\tpage_from_min\tcount\twidth\theight\tcolor_type\tfiles")
    for address, paths in sorted(by_address.items()):
        width, height, bit_depth, color_type = png_info(paths[0])
        page_from_min = (address - min_address) // args.page_size
        print(
            f"0x{address:08x}\t{page_from_min}\t{len(paths)}\t{width}\t{height}\t"
            f"{png_color_type_name(color_type, bit_depth)}\t{', '.join(path.name for path in paths)}"
        )

    return 0


def png_info(path: Path) -> tuple[int, int, int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")

    position = 8
    while position < len(data):
        length = struct.unpack(">I", data[position : position + 4])[0]
        chunk_type = data[position + 4 : position + 8]
        chunk_data = data[position + 8 : position + 8 + length]
        position += 12 + length
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, _, _, _ = struct.unpack(">IIBBBBB", chunk_data)
            return width, height, bit_depth, color_type

    raise ValueError(f"{path} has no IHDR chunk")


def png_color_type_name(color_type: int, bit_depth: int) -> str:
    names = {
        0: "grayscale",
        2: "rgb",
        3: "indexed",
        4: "grayscale_alpha",
        6: "rgba",
    }
    return f"{names.get(color_type, f'unknown_{color_type}')}{bit_depth}"


if __name__ == "__main__":
    raise SystemExit(main())

