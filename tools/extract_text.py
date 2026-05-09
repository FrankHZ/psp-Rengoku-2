from __future__ import annotations

import argparse
import json
from pathlib import Path

from text_codec import find_candidate_spans


def export_text(
    input_path: Path,
    output_path: Path,
    min_length: int = 4,
    encodings: tuple[str, ...] = ("ascii", "utf-8", "shift_jis"),
) -> list[dict[str, object]]:
    data = input_path.read_bytes()
    entries = [
        {
            "id": index,
            "offset": span.offset,
            "length": span.length,
            "encoding": span.encoding,
            "text": span.text,
            "translation": span.text,
            "notes": "",
        }
        for index, span in enumerate(find_candidate_spans(data, min_length, encodings=encodings))
    ]

    payload = {
        "source": str(input_path),
        "format": "raw-candidate-spans-v1",
        "assumptions": [
            "Offsets are byte offsets into the source file.",
            "Lengths are original byte lengths.",
            "Import supports same-size or shorter replacements only.",
        ],
        "entries": entries,
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description="Export candidate text strings from a binary file to JSON.")
    parser.add_argument("input", type=Path, help="Source binary file.")
    parser.add_argument("output", type=Path, help="Output JSON file.")
    parser.add_argument("--min-length", type=int, default=4, help="Minimum decoded character length.")
    parser.add_argument(
        "--encoding",
        action="append",
        choices=("ascii", "utf-8", "shift_jis"),
        help="Encoding to scan. May be repeated. Defaults to all supported encodings.",
    )
    args = parser.parse_args()

    encodings = tuple(args.encoding) if args.encoding else ("ascii", "utf-8", "shift_jis")
    entries = export_text(args.input, args.output, args.min_length, encodings=encodings)
    print(f"exported {len(entries)} entries to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
