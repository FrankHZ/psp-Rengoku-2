from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from build_chs_tutorial import iter_translation_tokens


DEFAULT_TABLES = (
    "DATA001/0003",
    "DATA001/0008",
    "DATA001/0012",
    "DATA001/0015",
    "DATA001/0016",
    "DATA001/0017",
    "DATA002/0065",
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge a validated build root with estimate rows into full target sheets.")
    parser.add_argument("--build-root", type=Path, required=True)
    parser.add_argument("--coverage-csv", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    counts = make_full_current_target_sheets(args.build_root, args.coverage_csv, args.output_dir)
    print(json.dumps(counts, ensure_ascii=False, indent=2))
    return 0


def make_full_current_target_sheets(build_root: Path, coverage_csv: Path, output_dir: Path) -> dict[str, Any]:
    rows_by_table: dict[str, dict[tuple[int, int], dict[str, Any]]] = {table: {} for table in DEFAULT_TABLES}
    source_counts: dict[str, dict[str, int]] = {table: {"validated": 0, "estimate": 0} for table in DEFAULT_TABLES}
    adjustments: list[dict[str, Any]] = []

    for path in sorted(build_root.glob("DATA???_????_chs.json")):
        table = table_from_generated_path(path)
        if table not in rows_by_table:
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for entry in payload.get("entries", []):
            key = (int(entry["record"]), int(entry.get("run", 0)))
            rows_by_table[table][key] = {
                "table": table,
                "record": key[0],
                "run": key[1],
                "chs_draft": entry.get("translation", ""),
                "source_max_units": int(entry["length"]),
                "source": "validated-build",
                "notes": f"validated source from {path.as_posix()}",
            }
            source_counts[table]["validated"] += 1

    with coverage_csv.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            table = row["table"]
            if table not in rows_by_table:
                continue
            key = (int(row["record"]), int(row["run"]))
            if key in rows_by_table[table]:
                continue
            text = row.get("estimated_chs_or_passthrough", "")
            if text == "":
                continue
            max_units = int(row["length"])
            fitted_text = fit_estimate_text(table, key[0], text, max_units)
            if fitted_text != text:
                adjustments.append(
                    {
                        "table": table,
                        "record": key[0],
                        "run": key[1],
                        "max_units": max_units,
                        "original": text,
                        "fitted": fitted_text,
                    }
                )
            rows_by_table[table][key] = {
                "table": table,
                "record": key[0],
                "run": key[1],
                "chs_draft": fitted_text,
                "source_max_units": max_units,
                "source": row.get("v15_status", row.get("status", "estimate")),
                "notes": "filled from coverage estimate row",
            }
            source_counts[table]["estimate"] += 1

    output_dir.mkdir(parents=True, exist_ok=True)
    summary: dict[str, Any] = {"tables": {}, "total_rows": 0}
    for table in DEFAULT_TABLES:
        rows = [rows_by_table[table][key] for key in sorted(rows_by_table[table])]
        archive, entry = table.split("/")
        path = output_dir / f"{archive}_{entry}_full_current_target_sheet.json"
        path.write_text(json.dumps({"entries": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        summary["tables"][table] = {
            "rows": len(rows),
            "validated_rows": source_counts[table]["validated"],
            "estimate_rows": source_counts[table]["estimate"],
            "sheet": path.as_posix(),
        }
        summary["total_rows"] += len(rows)

    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_adjustments(output_dir / "fit_adjustments.csv", adjustments)
    return summary


def fit_estimate_text(table: str, record: int, text: str, max_units: int) -> str:
    if encoded_unit_count(text) <= max_units:
        return text

    shortened = text.replace("粗译", "")
    if encoded_unit_count(shortened) <= max_units:
        return shortened

    prefix = {
        "DATA001/0008": "教",
        "DATA001/0012": "故",
        "DATA001/0016": "界",
        "DATA002/0065": "名",
    }.get(table, "文")
    candidates = (
        f"{prefix}{record:03d}",
        f"{prefix}{record}",
        f"{record:03d}",
        f"{record}",
        "?",
    )
    for candidate in candidates:
        if encoded_unit_count(candidate) <= max_units:
            return candidate
    return ""


def encoded_unit_count(text: str) -> int:
    return sum(1 for _ in iter_translation_tokens(text))


def write_adjustments(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["table", "record", "run", "max_units", "original", "fitted"])
        writer.writeheader()
        writer.writerows(rows)


def table_from_generated_path(path: Path) -> str:
    archive, entry = path.stem.split("_")[0:2]
    return f"{archive}/{entry}"


if __name__ == "__main__":
    raise SystemExit(main())
