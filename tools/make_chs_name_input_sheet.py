from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_SOURCE_EXPORT = Path("local/work/extract_text_DATA002_0065_seeded.json")
DEFAULT_OUTPUT_DIR = Path("local/work/name_input_chs_v1")
DEFAULT_OUTPUT_JSON = DEFAULT_OUTPUT_DIR / "DATA002_0065_name_input_chs.json"
DEFAULT_OUTPUT_CSV = DEFAULT_OUTPUT_DIR / "DATA002_0065_name_input_chs.csv"

NAME_INPUT_ROWS = {
    82: "用此名吗？",
    83: "确定",
    84: "取消",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Create the DATA002/0065 name-input confirmation CHS sheet.")
    parser.add_argument("--source-export", type=Path, default=DEFAULT_SOURCE_EXPORT)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    args = parser.parse_args()

    payload = make_name_input_sheet(args.source_export)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(args.output_csv, payload["entries"])
    summary = {
        "source_export": str(args.source_export).replace("\\", "/"),
        "output_json": str(args.output_json).replace("\\", "/"),
        "output_csv": str(args.output_csv).replace("\\", "/"),
        "rows": len(payload["entries"]),
        "records": sorted(NAME_INPUT_ROWS),
    }
    (args.output_json.parent / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def make_name_input_sheet(source_export: Path) -> dict[str, Any]:
    source = json.loads(source_export.read_text(encoding="utf-8"))
    rows_by_record = {(int(row["record"]), int(row["run"])): row for row in source["entries"]}
    entries = []
    for record, translation in NAME_INPUT_ROWS.items():
        source_row = rows_by_record[(record, 0)]
        max_units = int(source_row["length"])
        if len(translation) > max_units:
            raise ValueError(f"record {record} translation needs {len(translation)} units, max is {max_units}")
        entries.append(
            {
                "table": "DATA002/0065",
                "record": record,
                "run": 0,
                "role": "name_input_confirmation",
                "source_kind": source_row.get("kind", "glyph_codes"),
                "source_max_units": max_units,
                "source_codes": " ".join(source_row.get("codes", [])),
                "source_text": source_row.get("text", ""),
                "chs_draft": translation,
                "chs_units": len(translation),
                "chs_fits_source_budget": True,
                "notes": "Preserves runtime player name as a variable; only confirmation labels are patched.",
            }
        )
    return {
        "format": "translator-sheet-v1",
        "table": "DATA002/0065",
        "role": "name-input confirmation CHS draft",
        "source_export": str(source_export).replace("\\", "/"),
        "entries": entries,
    }


def write_csv(path: Path, entries: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(entries[0])
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)


if __name__ == "__main__":
    raise SystemExit(main())
