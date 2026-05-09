from __future__ import annotations

import argparse
import json
from pathlib import Path

from mcd3 import Mcd3Entry, read_mcd3
from text_codec import find_ascii_spans


FORMAT_HINTS: tuple[tuple[str, bytes], ...] = (
    ("MSCR", b"MSCR"),
    ("MIG", b"MIG.00.1PSP"),
    ("OMG", b"OMG.00.1PSP"),
    ("TDL", b".TDL"),
    ("PACK0001", b"PACK0001"),
    ("RIFF", b"RIFF"),
    ("VAGp", b"VAGp"),
    ("PSMF", b"PSMF"),
    ("PNG", b"\x89PNG"),
    ("PBP", b"\x00PBP"),
)


def extract_mcd3_entries(
    index_path: Path,
    archives_dir: Path,
    output_dir: Path,
    min_string: int = 6,
    string_limit: int = 8,
    overwrite: bool = False,
) -> dict[str, object]:
    index = read_mcd3(index_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = output_dir / "manifest.json"
    if manifest_path.exists() and not overwrite:
        raise FileExistsError(f"{manifest_path} already exists; pass --overwrite to replace extracted entries")

    entries: list[dict[str, object]] = []
    for entry in index.entries:
        if entry.is_empty or entry.archive_name is None:
            continue

        archive_path = archives_dir / entry.archive_name
        if not archive_path.exists():
            raise FileNotFoundError(archive_path)

        archive_data = archive_path.read_bytes()
        if entry.end_offset > len(archive_data):
            raise ValueError(f"entry {entry.id} extends past {archive_path}")

        data = archive_data[entry.offset : entry.end_offset]
        format_hint = detect_format(data)
        archive_stem = Path(entry.archive_name).stem
        archive_output_dir = output_dir / archive_stem
        archive_output_dir.mkdir(parents=True, exist_ok=True)

        suffix = format_hint.lower() if format_hint else "bin"
        output_name = f"{entry.id:04d}_{suffix}.bin"
        output_path = archive_output_dir / output_name
        if output_path.exists() and not overwrite:
            raise FileExistsError(f"{output_path} already exists; pass --overwrite to replace extracted entries")
        output_path.write_bytes(data)

        strings = [
            {"offset": span.offset, "length": span.length, "text": span.text}
            for span in list(find_ascii_spans(data, min_string))[:string_limit]
        ]
        entries.append(manifest_entry(entry, output_path, data, format_hint, strings))

    manifest = {
        "format": "mcd3-entry-manifest-v1",
        "source_index": str(index_path),
        "archives_dir": str(archives_dir),
        "entry_count": len(entries),
        "entries": entries,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def detect_format(data: bytes) -> str:
    for label, magic in FORMAT_HINTS:
        if data.startswith(magic):
            return label
    return "bin"


def manifest_entry(
    entry: Mcd3Entry,
    output_path: Path,
    data: bytes,
    format_hint: str,
    strings: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "id": entry.id,
        "archive": entry.archive_name,
        "archive_index": entry.archive_index,
        "selector": entry.selector,
        "offset": entry.offset,
        "size": entry.size,
        "stored_size": entry.stored_size,
        "format_hint": format_hint,
        "output": str(output_path),
        "header_hex": data[:16].hex(" "),
        "ascii_preview": strings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract non-empty entries referenced by a Rengoku 2 MCD3 index.")
    parser.add_argument("index", type=Path, help="Path to DATA000.BIN.")
    parser.add_argument("archives_dir", type=Path, help="Directory containing DATA001.BIN through DATA005.BIN.")
    parser.add_argument("output_dir", type=Path, help="Ignored output directory for extracted entries.")
    parser.add_argument("--min-string", type=int, default=6, help="Minimum ASCII string length in manifest previews.")
    parser.add_argument("--string-limit", type=int, default=8, help="Maximum string previews per entry.")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing manifest and entry files.")
    args = parser.parse_args()

    manifest = extract_mcd3_entries(
        args.index,
        args.archives_dir,
        args.output_dir,
        min_string=args.min_string,
        string_limit=args.string_limit,
        overwrite=args.overwrite,
    )
    print(f"extracted {manifest['entry_count']} entries to {args.output_dir}")
    print(f"manifest {args.output_dir / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

