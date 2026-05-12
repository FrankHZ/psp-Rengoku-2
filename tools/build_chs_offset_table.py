from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from build_chs_tutorial import (
    apply_source_hard_breaks,
    assign_chars,
    build_font_patches,
    encode_translation,
    write_assignments_csv,
)
from stage_font_probe import stage_font_probe


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a bounded Simplified Chinese offset-table-runs slice.")
    parser.add_argument("--sheet", type=Path, required=True, help="Translator sheet with record/run/chs_draft rows.")
    parser.add_argument("--table", default="DATA001/0015", help="Target table, e.g. DATA001/0008 or DATA001/0015.")
    parser.add_argument("--source-export", type=Path, help="Source offset-table-runs export JSON.")
    parser.add_argument("--source-entry", type=Path, help="Source extracted MCD3 entry binary.")
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--font", type=Path, default=Path("C:/Windows/Fonts/simsun.ttc"))
    parser.add_argument("--font-index", type=int, default=0)
    parser.add_argument("--font-size", type=int, default=13)
    parser.add_argument("--render-mode", choices=("grayscale", "binary", "palette3"), default="palette3")
    parser.add_argument("--threshold", type=int, default=64)
    parser.add_argument("--gray-threshold", type=int, default=176)
    parser.add_argument("--stroke-radius", type=int, default=0)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    table = parse_table_id(args.table)
    build_chs_offset_table(
        sheet_path=args.sheet,
        table=table,
        source_export_path=args.source_export or infer_source_export(table),
        source_entry_path=args.source_entry or infer_source_entry(table),
        work_root=args.work_root,
        output_root=args.output_root,
        font_path=args.font,
        font_index=args.font_index,
        font_size=args.font_size,
        render_mode=args.render_mode,
        threshold=args.threshold,
        gray_threshold=args.gray_threshold,
        stroke_radius=args.stroke_radius,
        overwrite=args.overwrite,
    )
    print(f"staged {args.output_root}")
    return 0


def build_chs_offset_table(
    sheet_path: Path,
    table: tuple[str, int],
    source_export_path: Path,
    source_entry_path: Path,
    work_root: Path,
    output_root: Path,
    font_path: Path,
    font_index: int = 0,
    font_size: int = 13,
    render_mode: str = "palette3",
    threshold: int = 64,
    gray_threshold: int = 176,
    stroke_radius: int = 0,
    overwrite: bool = False,
) -> None:
    archive, entry_id = table

    rows = load_translator_sheet(sheet_path, table=f"{archive}/{entry_id:04d}")
    source_export = json.loads(source_export_path.read_text(encoding="utf-8"))
    source_by_record = {(entry["record"], entry["run"]): entry for entry in source_export["entries"]}

    assignments = assign_chars(rows)
    text_payload = build_offset_table_payload(
        rows,
        source_by_record,
        source=str(source_entry_path).replace("\\", "/"),
        table=f"{archive}/{entry_id:04d}",
    )
    apply_translation_codes(text_payload["entries"], assignments)
    font_patches = build_font_patches(
        assignments,
        font_path,
        font_index,
        font_size,
        render_mode,
        threshold,
        gray_threshold,
        stroke_radius,
        work_root / "previews",
    )

    work_root.mkdir(parents=True, exist_ok=True)
    text_json = work_root / f"{archive}_{entry_id:04d}_chs.json"
    assignments_csv = work_root / "runtime_glyph_assignments.csv"
    stage_json = work_root / f"stage_{archive}_{entry_id:04d}_chs.json"

    text_json.write_text(json.dumps(text_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_assignments_csv(assignments_csv, assignments)

    stage_config = {
        "extracted_root": "local/extracted/Rengoku 2",
        "entries_root": "local/work/mcd3_entries",
        "work_root": str(work_root / "stage"),
        "output_root": str(output_root),
        "font_patches": font_patches,
        "text_patch": {
            "entry_id": entry_id,
            "source_entry": str(source_entry_path),
            "json": str(text_json),
        },
        "overwrite": overwrite,
    }
    stage_json.write_text(json.dumps(stage_config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    stage_font_probe(stage_config)


def parse_table_id(table: str) -> tuple[str, int]:
    parts = table.upper().split("/")
    if len(parts) != 2 or not parts[0].startswith("DATA"):
        raise ValueError(f"unsupported table id {table!r}; expected DATA001/0015")
    return parts[0], int(parts[1], 10)


def infer_source_export(table: tuple[str, int]) -> Path:
    archive, entry_id = table
    if archive == "DATA003" and entry_id == 1089:
        return Path("local/work/script_DATA003_1089_dialogue_seeded.json")
    return Path(f"local/work/extract_text_{archive}_{entry_id:04d}_seeded.json")


def infer_source_entry(table: tuple[str, int]) -> Path:
    archive, entry_id = table
    return Path(f"local/work/mcd3_entries/{archive}/{entry_id:04d}_bin.bin")


def load_translator_sheet(path: Path, table: str | None = None) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_rows = payload["entries"] if isinstance(payload, dict) and "entries" in payload else payload
    if not isinstance(raw_rows, list):
        raise ValueError("translator sheet must be a JSON list or an object with an entries list")

    rows: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_rows):
        if not isinstance(raw, dict):
            raise ValueError(f"row {index} is not an object")
        row_table = raw.get("table")
        if table is not None and row_table not in (None, table):
            raise ValueError(f"row {index} targets unsupported table {row_table!r}; expected {table}")
        chs = str(raw.get("chs_draft", raw.get("chs_translation", raw.get("translation", ""))))
        if chs == "":
            continue
        rows.append(
            {
                "record": int(raw["record"]),
                "run": int(raw["run"]),
                "chs_translation": chs,
                "role": raw.get("role", ""),
                "source_max_units": raw.get("source_max_units", raw.get("length")),
                "notes": raw.get("notes", ""),
            }
        )
    if not rows:
        raise ValueError("translator sheet has no rows with chs_draft/chs_translation")
    return rows


def build_offset_table_payload(
    rows: list[dict[str, Any]],
    source_by_record: dict[tuple[int, int], dict[str, Any]],
    source: str,
    table: str,
) -> dict[str, Any]:
    entries = []
    for index, row in enumerate(rows):
        record = int(row["record"])
        run = int(row["run"])
        source_entry = source_by_record[(record, run)]
        max_units = int(source_entry["length"])
        sheet_units = row.get("source_max_units")
        if sheet_units not in (None, "") and int(sheet_units) != max_units:
            raise ValueError(f"record {record} run {run} sheet budget {sheet_units} does not match source {max_units}")
        entries.append(
            {
                "id": f"chs-{table.replace('/', '-')}-{index:03d}",
                "record": record,
                "run": run,
                "entry_offset": source_entry.get("entry_offset"),
                "kind": "glyph_codes",
                "length": max_units,
                "codes": source_entry.get("codes", []),
                "translation": row["chs_translation"],
                "translation_codes": [],
                "notes": f"generated by tools/build_chs_offset_table.py; role={row.get('role', '')}".rstrip(),
            }
        )
    return {"format": "offset-table-runs-v1", "source": source, "entries": entries}


def apply_translation_codes(entries: list[dict[str, Any]], assignments: dict[str, dict[str, Any]]) -> None:
    for entry in entries:
        laid_out = apply_source_hard_breaks(str(entry["translation"]), entry.get("codes", []))
        codes = encode_translation(laid_out, assignments)
        max_units = int(entry["length"])
        if len(codes) > max_units:
            raise ValueError(
                f"record {entry['record']} run {entry['run']} needs {len(codes)} units, max is {max_units}"
            )
        entry["translation"] = laid_out
        entry["translation_codes"] = [f"0x{code:04x}" for code in codes]


if __name__ == "__main__":
    raise SystemExit(main())
