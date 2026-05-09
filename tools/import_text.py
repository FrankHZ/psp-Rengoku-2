from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from text_codec import encode_replacement


def import_text(source_path: Path, json_path: Path, output_path: Path) -> int:
    data = bytearray(source_path.read_bytes())
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    entries: list[dict[str, Any]] = payload.get("entries", [])

    applied = 0
    for entry in entries:
        offset = int(entry["offset"])
        length = int(entry["length"])
        encoding = str(entry["encoding"])
        replacement_text = str(entry.get("translation") or entry.get("text") or "")

        if offset < 0 or length < 0 or offset + length > len(data):
            raise ValueError(f"entry {entry.get('id', '?')} points outside source file")

        replacement = encode_replacement(replacement_text, encoding, length)
        data[offset : offset + length] = replacement
        applied += 1

    output_path.write_bytes(data)
    return applied


def main() -> int:
    parser = argparse.ArgumentParser(description="Import edited JSON text into a copy of a source file.")
    parser.add_argument("source", type=Path, help="Original source binary file.")
    parser.add_argument("json", type=Path, help="Edited extraction JSON.")
    parser.add_argument("output", type=Path, help="Output binary file. The source is never modified in place.")
    args = parser.parse_args()

    applied = import_text(args.source, args.json, args.output)
    print(f"applied {applied} entries to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

