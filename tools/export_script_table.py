from __future__ import annotations

import argparse
import json
from pathlib import Path

from extract_offset_table_runs import extract_file_runs
from glyph_map import decode_glyph_values, read_glyph_map


def export_script_table(
    input_path: Path,
    output_path: Path,
    glyph_map_path: Path | None = None,
) -> list[dict[str, object]]:
    glyphs = read_glyph_map(glyph_map_path) if glyph_map_path else {}
    current_section = ""
    rows: list[dict[str, object]] = []

    for run in extract_file_runs(input_path):
        kind = str(run["kind"])
        text = str(run["text"])
        role = "glyph"
        decoded_known = 0

        if kind == "text":
            role = "command" if text.startswith("#") else "text"
            decoded = text
            decoded_known = len(text)
            if text.startswith("#start"):
                current_section = text
        else:
            codes = [int(str(code), 0) for code in run["codes"]]
            decoded, decoded_known = decode_glyph_values(codes, glyphs) if glyphs else (" ".join(run["codes"]), 0)

        rows.append(
            {
                "id": len(rows),
                "section": current_section,
                "record": int(run["entry"]),
                "run": int(run["run"]),
                "entry_offset": int(run["entry_offset"]),
                "role": role,
                "kind": kind,
                "length": int(run["length"]),
                "codes": run["codes"],
                "decoded_known": decoded_known,
                "text": decoded,
                "translation": decoded if role == "text" else "",
                "notes": "",
            }
        )

    payload = {
        "source": str(input_path),
        "format": "script-table-v1",
        "assumptions": [
            "This is a view over an offset-table container, not a distinct container parser.",
            "Rows with direct u16 ASCII text beginning with # are script commands.",
            "#start commands define a rough section label for following rows.",
            "Glyph rows still require a script-specific glyph map before Japanese text is translator-ready.",
            "Importer support for this format is not implemented yet.",
        ],
        "entries": rows,
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Export script-like offset-table rows with command context.")
    parser.add_argument("input", type=Path, help="Offset-table script file.")
    parser.add_argument("output", type=Path, help="Output JSON path.")
    parser.add_argument("--glyph-map", type=Path, help="Optional CSV with code,char columns.")
    args = parser.parse_args()

    rows = export_script_table(args.input, args.output, args.glyph_map)
    command_count = sum(1 for row in rows if row["role"] == "command")
    glyph_count = sum(1 for row in rows if row["role"] == "glyph")
    print(f"exported {len(rows)} rows ({command_count} commands, {glyph_count} glyph rows) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
