from __future__ import annotations

import argparse
from pathlib import Path

from extract_mcd3_entries import detect_format
from pack0001 import read_pack0001
from text_codec import find_ascii_spans


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a PACK0001 container.")
    parser.add_argument("input", type=Path, help="Path to a PACK0001 file.")
    parser.add_argument("--extract-dir", type=Path, help="Optional ignored directory to extract child resources into.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite extracted child files.")
    args = parser.parse_args()

    pack = read_pack0001(args.input)
    data = args.input.read_bytes()
    print(f"path\t{pack.path}")
    print(f"entry_count\t{pack.entry_count}")
    print(f"table_offset\t0x{pack.table_offset:X}")
    print()
    print("index\toffset\tsize\tformat_hint\theader_hex\tascii_preview")

    for entry in pack.entries:
        child = data[entry.offset : entry.end_offset]
        strings = list(find_ascii_spans(child, 5))[:4]
        preview = " | ".join(f"0x{span.offset:X}:{span.text}" for span in strings)
        print(
            f"{entry.index}\t{entry.offset}\t{entry.size}\t{detect_format(child)}\t"
            f"{child[:16].hex(' ')}\t{preview}"
        )

    if args.extract_dir:
        args.extract_dir.mkdir(parents=True, exist_ok=True)
        for entry in pack.entries:
            child = data[entry.offset : entry.end_offset]
            output = args.extract_dir / f"{entry.index:04d}_{detect_format(child).lower()}.bin"
            if output.exists() and not args.overwrite:
                raise FileExistsError(f"{output} exists; pass --overwrite")
            output.write_bytes(child)
        print(f"\nextracted\t{len(pack.entries)}\t{args.extract_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

