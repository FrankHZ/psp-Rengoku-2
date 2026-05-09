from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import struct

from offset_table import read_offset_table


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize u16 value patterns in offset-table candidate records.")
    parser.add_argument("input", type=Path, nargs="+", help="Offset-table files or directories.")
    parser.add_argument("--top", type=int, default=24)
    args = parser.parse_args()

    for path in expand_inputs(args.input):
        try:
            table = read_offset_table(path)
        except ValueError:
            continue

        data = path.read_bytes()
        values: Counter[int] = Counter()
        prefixes: Counter[tuple[int, ...]] = Counter()
        sizes: Counter[int] = Counter(entry.size for entry in table.entries)
        for entry in table.entries:
            record = data[entry.offset : entry.end_offset]
            u16s = struct.unpack_from(f"<{len(record) // 2}H", record, 0) if len(record) >= 2 else ()
            values.update(u16s)
            prefixes.update([u16s[: min(8, len(u16s))]])

        print(f"{path}\tcount={table.count}\tsize={path.stat().st_size}\ttable_end=0x{table.table_end:x}")
        print("sizes\t" + " ".join(f"{size}:{count}" for size, count in sizes.most_common(args.top)))
        print("u16_top\t" + " ".join(f"0x{value:04x}:{count}" for value, count in values.most_common(args.top)))
        print("prefix_top")
        for prefix, count in prefixes.most_common(min(args.top, 8)):
            print(f"  {count}\t" + " ".join(f"{value:04x}" for value in prefix))
    return 0


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
