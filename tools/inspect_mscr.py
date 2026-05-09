from __future__ import annotations

import argparse
from pathlib import Path

from mscr import read_mscr


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect an MSCR map/scene resource bundle.")
    parser.add_argument("input", type=Path, nargs="+", help="MSCR files to inspect.")
    parser.add_argument("--limit", type=int, default=8, help="Maximum embedded TDL names to print per MSCR.")
    args = parser.parse_args()

    print("path\tsize\tdeclared_size\tsection_count\tword4\tword5\tembedded_tdl_entries\tnames")
    for path in args.input:
        mscr = read_mscr(path)
        names = ""
        count = ""
        if mscr.embedded_tdl:
            count = str(mscr.embedded_tdl.entry_count)
            names = " | ".join(entry.name for entry in mscr.embedded_tdl.entries[: args.limit])
        print(
            f"{path}\t{path.stat().st_size}\t{mscr.declared_size}\t{mscr.section_count}\t"
            f"0x{mscr.word4:X}\t0x{mscr.word5:X}\t{count}\t{names}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

