from __future__ import annotations

import argparse
from pathlib import Path

from tdl import read_tdl


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a .TDL resource container.")
    parser.add_argument("input", type=Path, help="Path to a .TDL entry file.")
    parser.add_argument("--extract-dir", type=Path, help="Optional ignored directory to extract child resources into.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite extracted child files.")
    args = parser.parse_args()

    tdl = read_tdl(args.input)
    print(f"path\t{tdl.path}")
    print(f"entry_count\t{tdl.entry_count}")
    print(f"declared_data_size\t{tdl.declared_data_size}")
    print(f"flags_or_reserved\t0x{tdl.flags_or_reserved:X}")
    print()
    print("index\tname\toffset\tsize\theader_hex")

    data = args.input.read_bytes()
    for entry in tdl.entries:
        header = data[entry.offset : entry.offset + min(entry.size, 16)].hex(" ")
        print(f"{entry.index}\t{entry.name}\t{entry.offset}\t{entry.size}\t{header}")

    if args.extract_dir:
        args.extract_dir.mkdir(parents=True, exist_ok=True)
        for entry in tdl.entries:
            output = args.extract_dir / f"{entry.index:04d}_{entry.name or 'unnamed'}.bin"
            if output.exists() and not args.overwrite:
                raise FileExistsError(f"{output} exists; pass --overwrite")
            output.write_bytes(data[entry.offset : entry.end_offset])
        print(f"\nextracted\t{len(tdl.entries)}\t{args.extract_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

