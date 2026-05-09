from __future__ import annotations

import argparse
import json
from pathlib import Path

from extract_offset_table_runs import extract_file_runs
from glyph_map import decode_glyph_values, read_glyph_map
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


def export_offset_table_runs(
    input_path: Path,
    output_path: Path,
    glyph_map_path: Path | None = None,
) -> list[dict[str, object]]:
    runs = extract_file_runs(input_path)
    glyphs = read_glyph_map(glyph_map_path) if glyph_map_path else {}
    entries: list[dict[str, object]] = []
    for index, run in enumerate(runs):
        if run["kind"] == "text":
            source_text = str(run["text"])
            decoded_known = int(run["length"])
        else:
            values = [int(str(code), 0) for code in run["codes"]]
            source_text, decoded_known = decode_glyph_values(values, glyphs) if glyphs else (" ".join(run["codes"]), 0)
        entries.append(
            {
                "id": index,
                "record": int(run["entry"]),
                "run": int(run["run"]),
                "entry_offset": int(run["entry_offset"]),
                "kind": run["kind"],
                "length": int(run["length"]),
                "codes": run["codes"],
                "decoded_known": decoded_known,
                "text": source_text,
                "translation": source_text if run["kind"] == "text" else "",
                "notes": "",
            }
        )

    payload = {
        "source": str(input_path),
        "format": "offset-table-runs-v1",
        "assumptions": [
            "Records are addressed by offset-table record index and run index.",
            "kind=text runs are direct u16 ASCII code-unit strings.",
            "kind=glyph_codes runs require a glyph map before translator-facing Japanese extraction is complete.",
            "When --glyph-map is supplied, glyph_codes text is a partial decode and unknown glyphs are shown as middots.",
            "Importer supports same-size or shorter text/glyph-code replacements for this format.",
        ],
        "entries": entries,
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description="Export candidate text strings from a binary file to JSON.")
    parser.add_argument("input", type=Path, help="Source binary file.")
    parser.add_argument("output", type=Path, help="Output JSON file.")
    parser.add_argument("--format", choices=("raw", "offset-table-runs"), default="raw")
    parser.add_argument("--glyph-map", type=Path, help="CSV with code,char columns for decoding glyph-code runs.")
    parser.add_argument("--min-length", type=int, default=4, help="Minimum decoded character length.")
    parser.add_argument(
        "--encoding",
        action="append",
        choices=("ascii", "utf-8", "shift_jis"),
        help="Encoding to scan. May be repeated. Defaults to all supported encodings.",
    )
    args = parser.parse_args()

    if args.format == "offset-table-runs":
        entries = export_offset_table_runs(args.input, args.output, args.glyph_map)
    else:
        encodings = tuple(args.encoding) if args.encoding else ("ascii", "utf-8", "shift_jis")
        entries = export_text(args.input, args.output, args.min_length, encodings=encodings)
    print(f"exported {len(entries)} entries to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
