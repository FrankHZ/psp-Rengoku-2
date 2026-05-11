from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_BUILD_ROOT = Path("local/work/combined_chs_v23_tutorial_usa_aligned_bitplane")
DEFAULT_OUTPUT_DIR = Path("local/work/v23_translation_review_pack")

ALIGNMENTS = {
    "DATA001/0003": Path("local/work/align_JP0003_USA0009_boot_ui.json"),
    "DATA001/0008": Path("local/work/align_JP0008_USA0017_tutorial_full_v1.json"),
    "DATA001/0012": Path("local/work/align_JP0012_USA0022_story.json"),
    "DATA001/0015": Path("local/work/align_JP0015_USA0026_ui.json"),
    "DATA001/0016": Path("local/work/align_JP0016_USA0027_ui.json"),
    "DATA001/0017": Path("local/work/align_JP0017_USA0028_help.json"),
    "DATA002/0065": Path("local/work/align_JP0065_USA0066_ui.json"),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Export per-bin translation review JSON from a current CHS build.")
    parser.add_argument("--build-root", type=Path, default=DEFAULT_BUILD_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    summary = export_review_pack(args.build_root, args.output_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def export_review_pack(build_root: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summaries: list[dict[str, Any]] = []

    for build_json in sorted(build_root.glob("DATA???_????_chs.json")):
        table = table_from_build_json(build_json)
        alignment_payload = read_json(ALIGNMENTS.get(table))
        alignment = build_alignment_index(alignment_payload)
        payload = read_json(build_json)
        entries = []
        exact = 0
        fallback = 0
        missing = 0

        for entry in payload.get("entries", []):
            record = int(entry["record"])
            run = int(entry.get("run", 0))
            align_row, match_type = find_alignment(alignment, record, run)
            if match_type == "exact":
                exact += 1
            elif match_type.startswith("record"):
                fallback += 1
            else:
                missing += 1
            entries.append(
                {
                    "table": table,
                    "record_path": f"{table}#{record:04d}:{run}",
                    "record": record,
                    "run": run,
                    "source_max_units": int(entry["length"]),
                    "current_chs": entry.get("translation", ""),
                    "current_chs_units": len(entry.get("translation_codes", [])),
                    "has_rough_marker": "粗译" in str(entry.get("translation", "")),
                    "english_alignment": align_row.get("reference_text", "") if align_row else "",
                    "alignment_match": match_type,
                    "english_units": align_row.get("reference_units") if align_row else None,
                    "english_fits_source_slot": align_row.get("fits_source_slot") if align_row else None,
                    "source_partial_text": align_row.get("source_partial_text", "") if align_row else "",
                }
            )

        archive, entry_id = table.split("/")
        out_path = output_dir / f"{archive}_{entry_id}_translation_review.json"
        out_payload = {
            "format": "translation-review-pack-v1",
            "build_root": build_root.as_posix(),
            "table": table,
            "source_build_json": build_json.as_posix(),
            "alignment_source": ALIGNMENTS.get(table, Path("")).as_posix() if table in ALIGNMENTS else "",
            "notes": [
                "Generated under local/work because English alignment text is reference material.",
                "alignment_match=exact means record and run both matched.",
                "alignment_match=record_fallback_run0 means exact run was missing, but the same record run 0 was available.",
            ],
            "entries": entries,
        }
        out_path.write_text(json.dumps(out_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        summaries.append(
            {
                "table": table,
                "rows": len(entries),
                "rough_markers": sum(1 for row in entries if row["has_rough_marker"]),
                "exact_alignment": exact,
                "record_fallback_alignment": fallback,
                "missing_alignment": missing,
                "file": out_path.as_posix(),
            }
        )

    summary = {
        "artifact": output_dir.as_posix(),
        "build_root": build_root.as_posix(),
        "files": summaries,
        "totals": {
            "rows": sum(row["rows"] for row in summaries),
            "rough_markers": sum(row["rough_markers"] for row in summaries),
            "exact_alignment": sum(row["exact_alignment"] for row in summaries),
            "record_fallback_alignment": sum(row["record_fallback_alignment"] for row in summaries),
            "missing_alignment": sum(row["missing_alignment"] for row in summaries),
        },
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_readme(output_dir / "README.md", summary)
    return summary


def table_from_build_json(path: Path) -> str:
    archive, entry = path.stem.split("_")[0:2]
    return f"{archive}/{entry}"


def read_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_alignment_index(payload: dict[str, Any]) -> dict[str, dict[tuple[int, int], dict[str, Any]]]:
    exact: dict[tuple[int, int], dict[str, Any]] = {}
    by_record: dict[tuple[int, int], dict[str, Any]] = {}
    for row in payload.get("entries", []):
        record = int(row["record"])
        run = int(row.get("run", 0))
        exact[(record, run)] = row
        by_record.setdefault((record, run), row)
    return {"exact": exact, "by_record": by_record}


def find_alignment(index: dict[str, dict[tuple[int, int], dict[str, Any]]], record: int, run: int) -> tuple[dict[str, Any] | None, str]:
    exact = index.get("exact", {})
    row = exact.get((record, run))
    if row is not None:
        return row, "exact"
    row = exact.get((record, 0))
    if row is not None:
        return row, "record_fallback_run0"
    return None, "missing"


def write_readme(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# v23 Translation Review Pack",
        "",
        "One JSON file per patched text bin/table. These files include current v23 CHS text",
        "plus local USA alignment text for tester review. Keep this directory local/ignored.",
        "",
        "Totals:",
        "",
        f"- rows: {summary['totals']['rows']}",
        f"- rough markers: {summary['totals']['rough_markers']}",
        f"- exact alignments: {summary['totals']['exact_alignment']}",
        f"- record-fallback alignments: {summary['totals']['record_fallback_alignment']}",
        f"- missing alignments: {summary['totals']['missing_alignment']}",
        "",
        "Files:",
        "",
    ]
    for item in summary["files"]:
        lines.append(
            f"- `{Path(item['file']).name}`: {item['table']}, rows {item['rows']}, rough {item['rough_markers']}, "
            f"exact {item['exact_alignment']}, fallback {item['record_fallback_alignment']}, missing {item['missing_alignment']}"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
