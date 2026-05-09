from __future__ import annotations

import argparse
from pathlib import Path

from mcd3 import read_mcd3


def replace_mcd3_entry(index_path: Path, archives_dir: Path, entry_id: int, replacement_path: Path, output_path: Path) -> None:
    index = read_mcd3(index_path)
    if entry_id < 0 or entry_id >= len(index.entries):
        raise ValueError(f"entry id {entry_id} is outside the MCD3 index")

    entry = index.entries[entry_id]
    if entry.is_empty or entry.archive_name is None:
        raise ValueError(f"entry id {entry_id} is empty")

    replacement = replacement_path.read_bytes()
    if len(replacement) != entry.size:
        raise ValueError(f"replacement size {len(replacement)} does not match indexed entry size {entry.size}")

    archive_path = archives_dir / entry.archive_name
    archive = bytearray(archive_path.read_bytes())
    if entry.end_offset > len(archive):
        raise ValueError(f"entry id {entry_id} extends past {archive_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    archive[entry.offset : entry.end_offset] = replacement
    output_path.write_bytes(archive)


def main() -> int:
    parser = argparse.ArgumentParser(description="Replace one same-size MCD3 entry in a copied archive file.")
    parser.add_argument("index", type=Path, help="Path to DATA000.BIN.")
    parser.add_argument("archives_dir", type=Path, help="Directory containing DATA001.BIN through DATA005.BIN.")
    parser.add_argument("entry_id", type=int, help="MCD3 entry id to replace.")
    parser.add_argument("replacement", type=Path, help="Same-size replacement entry payload.")
    parser.add_argument("output", type=Path, help="Output archive path. The source archive is never modified.")
    args = parser.parse_args()

    replace_mcd3_entry(args.index, args.archives_dir, args.entry_id, args.replacement, args.output)
    print(f"replaced entry {args.entry_id} into {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
