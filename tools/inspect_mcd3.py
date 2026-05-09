from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from mcd3 import Mcd3Entry, read_mcd3


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a Rengoku 2 MCD3 archive index.")
    parser.add_argument("index", type=Path, help="Path to DATA000.BIN.")
    parser.add_argument(
        "--archives-dir",
        type=Path,
        help="Directory containing DATA001.BIN through DATA005.BIN for bounds and header checks.",
    )
    parser.add_argument("--samples", type=int, default=8, help="Number of non-empty entries to show per archive.")
    args = parser.parse_args()

    index = read_mcd3(args.index)
    archive_sizes = _archive_sizes(args.archives_dir, index.archive_names) if args.archives_dir else {}

    print(f"path\t{index.path}")
    print(f"header_size\t0x{index.header_size:X}")
    print(f"archive_count\t{index.archive_count}")
    print(f"entry_count\t{index.entry_count}")
    print()
    print("archives")
    print("index\tname\tentries\tfirst_id\tlast_id\tmax_end\tarchive_size\tstatus")

    grouped: dict[int | None, list[Mcd3Entry]] = defaultdict(list)
    for entry in index.entries:
        grouped[entry.archive_index].append(entry)

    for archive_index, name in enumerate(index.archive_names):
        entries = [entry for entry in grouped.get(archive_index, []) if not entry.is_empty]
        first_id = entries[0].id if entries else ""
        last_id = entries[-1].id if entries else ""
        max_end = max((entry.end_offset for entry in entries), default=0)
        archive_size = archive_sizes.get(name)
        status = "unknown"
        if archive_size is not None:
            status = "ok" if max_end <= archive_size else "out-of-bounds"
        print(
            f"{archive_index}\t{name}\t{len(entries)}\t{first_id}\t{last_id}\t"
            f"{max_end}\t{archive_size if archive_size is not None else ''}\t{status}"
        )

    empty_count = sum(1 for entry in index.entries if entry.is_empty)
    print(f"\nempty_entries\t{empty_count}")

    if args.archives_dir:
        print("\nsamples")
        print("id\tarchive\tselector\toffset\tsize\tstored_size\theader")
        for archive_index, name in enumerate(index.archive_names):
            archive_path = args.archives_dir / name
            archive_data = archive_path.read_bytes() if archive_path.exists() else b""
            entries = [entry for entry in grouped.get(archive_index, []) if not entry.is_empty]
            for entry in entries[: args.samples]:
                header = archive_data[entry.offset : entry.offset + min(entry.size, 16)].hex(" ")
                print(
                    f"{entry.id}\t{name}\t0x{entry.selector:X}\t{entry.offset}\t"
                    f"{entry.size}\t{entry.stored_size}\t{header}"
                )

    return 0


def _archive_sizes(archives_dir: Path, names: tuple[str, ...]) -> dict[str, int]:
    sizes = {}
    for name in names:
        path = archives_dir / name
        if path.exists():
            sizes[name] = path.stat().st_size
    return sizes


if __name__ == "__main__":
    raise SystemExit(main())

