from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


PLACEHOLDER_MARKERS = ("粗译",)


def main() -> int:
    parser = argparse.ArgumentParser(description="Report rough placeholder rows in full target sheets.")
    parser.add_argument("--estimate-csv", type=Path, default=Path("local/work/full_translation_glyph_estimate_v1/all_rows_estimate.csv"))
    parser.add_argument("--fit-csv", type=Path, default=Path("local/work/full_current_target_sheets_v2/fit_adjustments.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("local/work/placeholder_investigation_v1"))
    args = parser.parse_args()

    summary = report_placeholders(args.estimate_csv, args.fit_csv, args.output_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def report_placeholders(estimate_csv: Path, fit_csv: Path, output_dir: Path) -> dict[str, Any]:
    rows = read_csv(estimate_csv)
    placeholder_rows = [
        row
        for row in rows
        if any(marker in row.get("estimated_chs_or_passthrough", "") for marker in PLACEHOLDER_MARKERS)
    ]
    fit_rows = read_csv(fit_csv) if fit_csv.exists() and fit_csv.stat().st_size else []
    fit_keys = {(row["table"], int(row["record"]), int(row["run"])): row for row in fit_rows}

    report_rows: list[dict[str, Any]] = []
    for row in placeholder_rows:
        key = (row["table"], int(row["record"]), int(row["run"]))
        fit = fit_keys.get(key)
        report_rows.append(
            {
                "table": row["table"],
                "record": row["record"],
                "run": row["run"],
                "length": row["length"],
                "placeholder": row["estimated_chs_or_passthrough"],
                "fitted": fit["fitted"] if fit else "",
                "has_usa_reference": bool(row.get("usa_reference_text", "")),
                "usa_reference_text": row.get("usa_reference_text", ""),
                "jp_partial_text": row.get("jp_partial_text", ""),
                "notes": row.get("notes", ""),
            }
        )

    by_table: dict[str, dict[str, int]] = {}
    for row in report_rows:
        table = row["table"]
        stats = by_table.setdefault(table, {"placeholder_rows": 0, "with_usa_reference": 0, "fit_adjusted": 0})
        stats["placeholder_rows"] += 1
        if row["has_usa_reference"]:
            stats["with_usa_reference"] += 1
        if row["fitted"]:
            stats["fit_adjusted"] += 1

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "placeholder_rows.csv", report_rows)
    write_csv(output_dir / "placeholder_summary.csv", [{"table": table, **stats} for table, stats in sorted(by_table.items())])
    summary = {
        "artifact": str(output_dir),
        "placeholder_rows": len(report_rows),
        "with_usa_reference": sum(1 for row in report_rows if row["has_usa_reference"]),
        "fit_adjusted": sum(1 for row in report_rows if row["fitted"]),
        "by_table": by_table,
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_readme(output_dir / "README.md", summary)
    return summary


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_readme(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Placeholder Investigation v1",
        "",
        "This report tracks rough placeholder rows such as `教程粗译###` in the",
        "full current-target sheets. These placeholders indicate rows where the",
        "estimate generator had no reviewed CHS row and no usable USA alignment text.",
        "",
        f"Placeholder rows: {summary['placeholder_rows']}",
        f"Rows with USA reference text: {summary['with_usa_reference']}",
        f"Rows fitted to slot budget in v22: {summary['fit_adjusted']}",
        "",
        "Files:",
        "",
        "- `placeholder_rows.csv`: row-level placeholder details.",
        "- `placeholder_summary.csv`: counts by table.",
        "- `summary.json`: machine-readable summary.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
