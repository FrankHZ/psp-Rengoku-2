from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from build_chs_tutorial import RESERVED_SOURCE_ICON_CELLS, reserved_runtime_logical_slots


DEFAULT_ESTIMATE = Path("local/work/full_translation_glyph_estimate_v1/all_rows_estimate.csv")
DEFAULT_OUTPUT = Path("local/work/chs_coverage_v19_manual_prose_layout")
DEFAULT_BUILD_ROOT = Path(
    "local/work/combined_chs_v19_manual_prose_layout_0003_0008_0012anchored_0015full_0016full_0017full_0065"
)
DEFAULT_STAGE = DEFAULT_BUILD_ROOT / "stage_combined_chs.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize CHS parsed-row coverage and current build gaps.")
    parser.add_argument("--estimate-csv", type=Path, default=DEFAULT_ESTIMATE)
    parser.add_argument("--build-root", type=Path, default=DEFAULT_BUILD_ROOT)
    parser.add_argument("--stage", type=Path, help="Stage config to summarize. Defaults to BUILD_ROOT/stage_combined_chs.json.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    rows = read_csv(args.estimate_csv)
    build_keys = read_build_keys(args.build_root)
    stage_path = args.stage or (args.build_root / "stage_combined_chs.json")
    stage = read_json(stage_path) if stage_path.exists() else {}
    font_patches = stage.get("font_patches", [])
    font_summary = summarize_font_patches(font_patches)
    assigned_glyphs = font_summary["logical_assigned_glyphs"]
    reserved_logical_cells = (
        len(reserved_runtime_logical_slots())
        if font_summary["assignment_model"] == "bitplane"
        else len(RESERVED_SOURCE_ICON_CELLS)
    )

    for row in rows:
        key = row_key(row)
        if key in build_keys:
            row["v15_status"] = "current_build"
        elif row.get("status") in {"local_draft", "local_draft_only"}:
            row["v15_status"] = "local_draft_not_built"
        else:
            row["v15_status"] = "estimate_only_not_built"

    per_table = summarize_tables(rows)
    summary = {
        "artifact": str(args.output),
        "estimate_source": str(args.estimate_csv),
        "current_build_root": str(args.build_root),
        "current_stage": str(stage_path),
        "assigned_glyphs_current_build": assigned_glyphs,
        "assignment_model": font_summary["assignment_model"],
        "physical_cells_used": font_summary["physical_cells_used"],
        "low_layer_glyphs": font_summary["low_layer_glyphs"],
        "high_layer_glyphs": font_summary["high_layer_glyphs"],
        "logical_glyph_capacity": font_summary["logical_glyph_capacity"],
        "physical_glyph_cells": font_summary["physical_glyph_cells"],
        "reserved_source_icon_cells": len(RESERVED_SOURCE_ICON_CELLS),
        "reserved_source_logical_cells": reserved_logical_cells,
        "glyph_headroom": font_summary["logical_glyph_capacity"] - assigned_glyphs if assigned_glyphs else None,
        "usable_chs_glyph_headroom": (
            font_summary["logical_glyph_capacity"] - assigned_glyphs - reserved_logical_cells
            if assigned_glyphs
            else None
        ),
        "totals": summarize_rows(rows),
        "per_table": per_table,
        "manual_layout_status": {
            "fixed_body_records": [16, 18, 20, 22, 24, 26, 28, 30, 34, 36, 42, 44, 53, 57, 71, 73, 77, 85, 91],
            "notes": "DATA001/0017 queued manual body records now use explicit manual-layout overrides.",
        },
    }

    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "not_in_current_build.csv", [r for r in rows if r["v15_status"] != "current_build"])
    write_csv(args.output / "all_rows_coverage.csv", rows)
    write_csv(args.output / "per_table_coverage.csv", table_rows(per_table))
    (args.output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary["totals"], ensure_ascii=False, indent=2))
    return 0


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


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_font_patches(font_patches: list[dict[str, Any]]) -> dict[str, Any]:
    logical_chars = {str(item.get("char", "")) for item in font_patches if item.get("char")}
    physical_cells = {
        (int(item["target_child"]), int(item["target_cell"]))
        for item in font_patches
        if "target_child" in item and "target_cell" in item
    }
    low_layer_glyphs = sum(1 for item in font_patches if item.get("layer") == "low")
    high_layer_glyphs = sum(1 for item in font_patches if item.get("layer") == "high")
    uses_bitplanes = any(item.get("mode") == "render_bitplane" for item in font_patches)
    return {
        "assignment_model": "bitplane" if uses_bitplanes else "single",
        "logical_assigned_glyphs": len(logical_chars),
        "physical_cells_used": len(physical_cells),
        "low_layer_glyphs": low_layer_glyphs,
        "high_layer_glyphs": high_layer_glyphs,
        "logical_glyph_capacity": 1782 if uses_bitplanes else 891,
        "physical_glyph_cells": 891,
    }


def read_build_keys(build_root: Path) -> set[tuple[str, int, int]]:
    keys: set[tuple[str, int, int]] = set()
    for path in build_root.glob("DATA???_????_chs.json"):
        payload = read_json(path)
        table = payload.get("table") or table_from_path(path)
        for entry in payload.get("entries", []):
            keys.add((str(table), int(entry["record"]), int(entry.get("run", 0))))
    return keys


def table_from_path(path: Path) -> str:
    archive, entry = path.name.split("_")[0:2]
    return f"{archive}/{entry}"


def row_key(row: dict[str, str]) -> tuple[str, int, int]:
    return (row["table"], int(row["record"]), int(row["run"]))


def summarize_rows(rows: list[dict[str, str]]) -> dict[str, int]:
    counts = {
        "total_parsed_rows": len(rows),
        "rows_in_current_build": 0,
        "rows_not_in_current_build": 0,
        "local_draft_rows_not_built": 0,
        "estimate_only_rows_not_built": 0,
    }
    for row in rows:
        status = row["v15_status"]
        if status == "current_build":
            counts["rows_in_current_build"] += 1
        else:
            counts["rows_not_in_current_build"] += 1
        if status == "local_draft_not_built":
            counts["local_draft_rows_not_built"] += 1
        if status == "estimate_only_not_built":
            counts["estimate_only_rows_not_built"] += 1
    return counts


def summarize_tables(rows: list[dict[str, str]]) -> dict[str, dict[str, int]]:
    tables: dict[str, dict[str, int]] = {}
    for row in rows:
        table = row["table"]
        counts = tables.setdefault(
            table,
            {
                "parsed_rows": 0,
                "rows_in_current_build": 0,
                "rows_not_in_current_build": 0,
                "local_draft_rows_not_built": 0,
                "estimate_only_rows_not_built": 0,
            },
        )
        counts["parsed_rows"] += 1
        status = row["v15_status"]
        if status == "current_build":
            counts["rows_in_current_build"] += 1
        else:
            counts["rows_not_in_current_build"] += 1
        if status == "local_draft_not_built":
            counts["local_draft_rows_not_built"] += 1
        if status == "estimate_only_not_built":
            counts["estimate_only_rows_not_built"] += 1
    return dict(sorted(tables.items()))


def table_rows(per_table: dict[str, dict[str, int]]) -> list[dict[str, Any]]:
    return [{"table": table, **counts} for table, counts in per_table.items()]


if __name__ == "__main__":
    raise SystemExit(main())
