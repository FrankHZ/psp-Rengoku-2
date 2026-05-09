from __future__ import annotations

import argparse
import math
from pathlib import Path

from text_codec import find_ascii_spans


KNOWN_MARKERS = (
    b"MCD3",
    b"MIG.00.1PSP",
    b"OMG.00.1PSP",
    b"MSCR",
    b".TDL",
    b".tm2",
    b"TIM2",
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a lightweight read-only inventory of binary files.")
    parser.add_argument("paths", nargs="+", type=Path, help="Files or directories to inspect.")
    parser.add_argument("--min-string", type=int, default=6, help="Minimum ASCII string length.")
    parser.add_argument("--limit", type=int, default=8, help="String/marker preview limit per file.")
    args = parser.parse_args()

    files = _expand_files(args.paths)
    print("path\tsize\theader_ascii\theader_hex\tentropy\tmarkers\tascii_preview")
    for path in files:
        data = path.read_bytes()
        header = data[:16]
        markers = _markers(data, args.limit)
        strings = list(find_ascii_spans(data, args.min_string))[: args.limit]
        print(
            f"{path}\t{len(data)}\t{_printable(header)}\t{header.hex(' ')}\t"
            f"{_entropy(data):.3f}\t{_join(markers)}\t{_join(f'0x{s.offset:X}:{s.text}' for s in strings)}"
        )
    return 0


def _expand_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(child for child in path.rglob("*") if child.is_file()))
        elif path.is_file():
            files.append(path)
        else:
            raise FileNotFoundError(path)
    return files


def _markers(data: bytes, limit: int) -> list[str]:
    found = []
    for marker in KNOWN_MARKERS:
        start = 0
        while len(found) < limit:
            index = data.find(marker, start)
            if index < 0:
                break
            found.append(f"0x{index:X}:{marker.decode('ascii', errors='replace')}")
            start = index + 1
    return found


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


def _join(values) -> str:
    return " | ".join(str(value).replace("\t", " ") for value in values)


if __name__ == "__main__":
    raise SystemExit(main())

