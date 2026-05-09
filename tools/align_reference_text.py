from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from glyph_map import decode_glyph_values


REFERENCE_CODE_LABELS = {
    0x011A: "[CIRCLE]",
    0x013E: "[X]",
    0x015F: "[SQUARE]",
    0x0161: "[TRIANGLE]",
}


def align_reference_text(
    source_json_path: Path,
    reference_json_path: Path,
    output_path: Path,
    records: set[int] | None = None,
) -> list[dict[str, Any]]:
    source_payload = json.loads(source_json_path.read_text(encoding="utf-8"))
    reference_payload = json.loads(reference_json_path.read_text(encoding="utf-8"))

    reference_by_key = {
        (int(entry["record"]), int(entry["run"])): entry for entry in reference_payload.get("entries", [])
    }

    rows: list[dict[str, Any]] = []
    for source_entry in source_payload.get("entries", []):
        record = int(source_entry["record"])
        run = int(source_entry["run"])
        if records is not None and record not in records:
            continue

        reference_entry = reference_by_key.get((record, run))
        if reference_entry is None:
            continue

        source_max_units = int(source_entry["length"])
        reference_text = display_text(reference_entry)
        reference_units = code_unit_length(reference_entry, reference_text)
        rows.append(
            {
                "record": record,
                "run": run,
                "source_kind": source_entry.get("kind"),
                "source_max_units": source_max_units,
                "source_partial_text": source_entry.get("text", ""),
                "reference_kind": reference_entry.get("kind"),
                "reference_units": reference_units,
                "reference_text": reference_text,
                "fits_source_slot": reference_units <= source_max_units,
                "notes": "",
            }
        )

    payload = {
        "format": "reference-alignment-v1",
        "source": str(source_json_path),
        "reference": str(reference_json_path),
        "assumptions": [
            "Rows are matched by offset-table record index and run index.",
            "Reference text is for local alignment only; do not commit generated alignment files if they contain copyrighted text.",
            "fits_source_slot only checks the current same-size/shorter importer budget.",
        ],
        "entries": rows,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return rows


def display_text(entry: dict[str, Any]) -> str:
    text = str(entry.get("text") or "")
    if entry.get("kind") != "glyph_codes":
        return text

    values = parse_codes(entry.get("codes", []))
    decoded, _known = decode_glyph_values(values, REFERENCE_CODE_LABELS)
    return decoded


def code_unit_length(entry: dict[str, Any], text: str) -> int:
    if entry.get("kind") == "glyph_codes":
        return len(parse_codes(entry.get("codes", [])))
    return len(text)


def parse_codes(codes: Any) -> list[int]:
    if not isinstance(codes, list):
        return []
    return [int(str(code), 0) for code in codes]


def main() -> int:
    parser = argparse.ArgumentParser(description="Align source offset-table text JSON with a local reference export.")
    parser.add_argument("source_json", type=Path, help="Source extraction JSON, usually the Japanese dump.")
    parser.add_argument("reference_json", type=Path, help="Reference extraction JSON, usually an ignored local USA dump.")
    parser.add_argument("output", type=Path, help="Output alignment JSON. Keep generated files under local/work.")
    parser.add_argument("--record", type=int, action="append", help="Only include a record. May be repeated.")
    args = parser.parse_args()

    rows = align_reference_text(
        args.source_json,
        args.reference_json,
        args.output,
        records=set(args.record) if args.record else None,
    )
    print(f"aligned {len(rows)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
