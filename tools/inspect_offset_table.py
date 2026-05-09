from __future__ import annotations

import argparse
from pathlib import Path

from offset_table import read_offset_table


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect simple u32-count/u32-offset table containers.")
    parser.add_argument("input", type=Path, nargs="+", help="Files or directories to inspect.")
    parser.add_argument("--limit", type=int, default=12, help="Maximum records to print per file.")
    args = parser.parse_args()

    for path in expand_inputs(args.input):
        try:
            table = read_offset_table(path)
        except ValueError as error:
            print(f"{path}\tSKIP\t{error}")
            continue

        print(
            f"{path}\tword0=0x{table.word0:x}\tcount={table.count}\t"
            f"table_end=0x{table.table_end:x}\tsize={path.stat().st_size}"
        )
        print("index\toffset\tsize\tu16_preview")
        for entry in table.entries[: args.limit]:
            preview = " ".join(f"{value:04x}" for value in entry.u16_preview)
            print(f"{entry.index}\t0x{entry.offset:x}\t{entry.size}\t{preview}")
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
