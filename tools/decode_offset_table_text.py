from __future__ import annotations

import argparse
from pathlib import Path
import struct

from glyph_map import decode_glyph_values, read_glyph_map
from offset_table import read_offset_table


def main() -> int:
    parser = argparse.ArgumentParser(description="Decode offset-table records with a seed glyph-code map.")
    parser.add_argument("glyph_map", type=Path, help="CSV with columns code,char.")
    parser.add_argument("input", type=Path, nargs="+", help="Offset-table files or directories.")
    parser.add_argument("--min-known", type=int, default=4)
    parser.add_argument("--limit", type=int, default=40)
    args = parser.parse_args()

    glyphs = read_glyph_map(args.glyph_map)
    printed = 0
    print("file\tentry\toffset\tsize\tknown\tdecoded")
    for path in expand_inputs(args.input):
        try:
            table = read_offset_table(path)
        except ValueError:
            continue
        data = path.read_bytes()
        for entry in table.entries:
            record = data[entry.offset : entry.end_offset]
            values = read_u16_values(record)
            decoded, known = decode_values(values, glyphs)
            if known < args.min_known:
                continue
            print(f"{path.name}\t{entry.index}\t0x{entry.offset:x}\t{entry.size}\t{known}\t{decoded}")
            printed += 1
            if args.limit and printed >= args.limit:
                return 0
    return 0


def read_u16_values(data: bytes) -> tuple[int, ...]:
    even_size = len(data) - (len(data) % 2)
    if even_size == 0:
        return ()
    return struct.unpack(f"<{even_size // 2}H", data[:even_size])


def decode_values(values: tuple[int, ...], glyphs: dict[int, str]) -> tuple[str, int]:
    return decode_glyph_values(values, glyphs)


def compact(parts: list[str]) -> str:
    text = "".join(parts)
    while "  " in text:
        text = text.replace("  ", " ")
    while "||" in text:
        text = text.replace("||", "|")
    return text.strip()


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
