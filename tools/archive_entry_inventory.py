from __future__ import annotations

import argparse
import math
import struct
import sys
from pathlib import Path

from mcd3 import Mcd3Entry, read_mcd3
from text_codec import find_ascii_spans


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory entries referenced by an MCD3 index.")
    parser.add_argument("index", type=Path, help="Path to DATA000.BIN.")
    parser.add_argument("archives_dir", type=Path, help="Directory containing DATA001.BIN through DATA005.BIN.")
    parser.add_argument("--archive", help="Only show entries from one archive name, such as DATA004.BIN.")
    parser.add_argument("--min-string", type=int, default=6, help="Minimum ASCII string length.")
    parser.add_argument("--limit", type=int, default=6, help="Preview limit for strings per entry.")
    parser.add_argument("--max-entries", type=int, help="Maximum number of entries to print.")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

    index = read_mcd3(args.index)
    try:
        print("id\tarchive\toffset\tsize\theader_ascii\theader_hex\tentropy\tformat_hint\tascii_preview")
        printed = 0
        for entry in index.entries:
            if entry.is_empty or entry.archive_name is None:
                continue
            if args.archive and entry.archive_name.lower() != args.archive.lower():
                continue
            if args.max_entries is not None and printed >= args.max_entries:
                break

            archive_path = args.archives_dir / entry.archive_name
            archive_data = archive_path.read_bytes()
            data = archive_data[entry.offset : entry.end_offset]
            strings = list(find_ascii_spans(data, args.min_string))[: args.limit]
            preview = " | ".join(f"0x{span.offset:X}:{span.text}" for span in strings)
            print(
                f"{entry.id}\t{entry.archive_name}\t{entry.offset}\t{entry.size}\t"
                f"{_printable(data[:16])}\t{data[:16].hex(' ')}\t{_entropy(data):.3f}\t"
                f"{_format_hint(data)}\t{preview}"
            )
            printed += 1
    except OSError:
        return 0
    return 0


def _format_hint(data: bytes) -> str:
    if data.startswith(b"MSCR") and len(data) >= 0x20:
        _, word1, declared_size, section_count, word4, word5, word6, word7 = struct.unpack_from("<4sIIIIIII", data, 0)
        return (
            f"MSCR word1=0x{word1:X} declared_size={declared_size} "
            f"sections={section_count} words=[0x{word4:X},0x{word5:X},0x{word6:X},0x{word7:X}]"
        )
    for magic in (b"MIG.00.1PSP", b"OMG.00.1PSP", b".TDL", b"PACK0001", b"RIFF", b"VAGp", b"PSMF"):
        if data.startswith(magic):
            return magic.decode("ascii", errors="replace")
    return ""


def _printable(data: bytes) -> str:
    return "".join(chr(value) if 0x20 <= value < 0x7F else "." for value in data)


def _entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = [0] * 256
    for value in data:
        counts[value] += 1
    total = len(data)
    return -sum((count / total) * math.log2(count / total) for count in counts if count)


if __name__ == "__main__":
    raise SystemExit(main())
