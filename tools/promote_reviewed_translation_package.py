from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from build_chs_tutorial import iter_translation_tokens


SHEET_SPECS = {
    "boot_ui.json": (
        "DATA001/0003",
        Path("local/work/translation_refine_v1/merged_target_sheets_all_fit_v1/DATA001_0003_full_current_target_sheet.json"),
        "DATA001_0003_full_current_target_sheet.json",
    ),
    "tutorial.json": (
        "DATA001/0008",
        Path("local/work/translation_refine_v1/merged_target_sheets_all_fit_v1/DATA001_0008_full_current_target_sheet.json"),
        "DATA001_0008_full_current_target_sheet.json",
    ),
    "story_data001_0012.json": (
        "DATA001/0012",
        Path("local/work/translation_refine_v1/merged_target_sheets_all_fit_v1/DATA001_0012_full_current_target_sheet.json"),
        "DATA001_0012_full_current_target_sheet.json",
    ),
    "ui.json": (
        "DATA001/0016",
        Path("local/work/translation_refine_v1/merged_target_sheets_v40_ui_data002/DATA001_0016_full_current_target_sheet.json"),
        "DATA001_0016_full_current_target_sheet.json",
    ),
    "help_manual.json": (
        "DATA001/0017",
        Path("local/work/translation_refine_v1/merged_target_sheets_all_fit_v1/DATA001_0017_full_current_target_sheet.json"),
        "DATA001_0017_full_current_target_sheet.json",
    ),
    "data002_ui.json": (
        "DATA002/0065",
        Path("local/work/translation_refine_v1/merged_target_sheets_v40_ui_data002/DATA002_0065_full_current_target_sheet.json"),
        "DATA002_0065_full_current_target_sheet.json",
    ),
    "story_data003_1089.json": (
        "DATA003/1089",
        Path("local/work/translation_refine_v1/merged_target_sheets_v39_story_glossary/DATA003_1089_jp_first_target_sheet.json"),
        "DATA003_1089_jp_first_target_sheet.json",
    ),
}


RUNTIME_FIT_OVERRIDES = {
    "DATA001/0012#0166:0": "正因我什么都没做…\n才会中枪…",
    "DATA001/0012#0263:0": "让你领略魅惑之战…！",
    "DATA001/0012#0317:0": "少见你激动啊…小心送命哦?",
    "DATA001/0012#0338:0": "@GRAM@，真高兴\n就像我亲手培育的一样！",
    "DATA001/0012#0339:0": "格律普斯，你疯了吗？\n你说是你培育了我？",
    "DATA001/0012#0340:0": "听起来,像我们已交手无数次…",
    "DATA001/0012#0347:0": "累了……一直……独自一人……\n这样……就能休息了……",
    "DATA001/0012#0371:0": "求你解释！\n那些家伙和我到底发生了什么！！！",
    "DATA001/0017#0094:0": "1. 何为H.E.A.V.E.N.",
    "DATA001/0017#0096:0": "2. H.E.A.V.E.N.-A",
    "DATA001/0017#0098:0": "3. H.E.A.V.E.N.-B",
    "DATA001/0017#0100:0": "4. H.E.A.V.E.N.-C",
    "DATA003/1089#0320:0": "无数人造人的未来",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Promote local reviewed JSON package into v41 target/review sheets.")
    parser.add_argument("--review-root", type=Path, default=Path("translation_reviewed"))
    parser.add_argument(
        "--target-root",
        type=Path,
        default=Path("local/work/translation_refine_v1/merged_target_sheets_v41_reviewed_all"),
    )
    parser.add_argument(
        "--review-output",
        type=Path,
        default=Path("local/work/translation_review_slim_v12_reviewed_all"),
    )
    args = parser.parse_args()

    args.target_root.mkdir(parents=True, exist_ok=True)
    args.review_output.mkdir(parents=True, exist_ok=True)

    summaries: list[dict[str, Any]] = []
    combined_entries: list[dict[str, Any]] = []
    for review_name, (table, base_target, out_name) in SHEET_SPECS.items():
        review_path = args.review_root / review_name
        if not review_path.exists():
            raise FileNotFoundError(review_path)
        review_rows = load_rows(review_path)
        target_payload = json.loads(base_target.read_text(encoding="utf-8"))
        changes = apply_review_rows(target_payload, review_rows, table)
        out_target = args.target_root / out_name
        write_json(out_target, target_payload)
        out_review = args.review_output / review_name
        write_json(out_review, review_rows)
        rough = count_rough(review_rows)
        summaries.append(
            {
                "file": review_name,
                "table": table,
                "rows": len(review_rows),
                "changed_rows": len(changes),
                "rough_markers": rough,
                "target": out_target.as_posix(),
                "review": out_review.as_posix(),
                "sample_changes": changes[:10],
            }
        )
        for row in review_rows:
            combined = {"review_file": review_name}
            combined.update(row)
            combined_entries.append(combined)

    equipment_summary = copy_equipment_review(args.review_root, args.review_output)
    summaries.append(equipment_summary)
    for row in load_rows(args.review_root / "equipment.json"):
        combined = {"review_file": "equipment.json"}
        combined.update(row)
        combined_entries.append(combined)

    write_json(args.review_output / "all_entries.json", combined_entries)
    summary = {
        "format": "translation-review-slim-v12-reviewed-all",
        "source_review_root": args.review_root.as_posix(),
        "target_root": args.target_root.as_posix(),
        "review_output": args.review_output.as_posix(),
        "files": summaries,
        "totals": {
            "files": len(summaries),
            "entries": len(combined_entries),
            "changed_rows": sum(item["changed_rows"] for item in summaries),
            "rough_markers": sum(item["rough_markers"] for item in summaries),
        },
    }
    write_json(args.review_output / "summary.json", summary)
    write_readme(args.review_output / "README.md", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def load_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"expected review file to contain a list: {path}")
    return payload


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def apply_review_rows(payload: dict[str, Any], review_rows: list[dict[str, Any]], table: str) -> list[dict[str, Any]]:
    review_by_key: dict[tuple[int, int], dict[str, Any]] = {}
    for row in review_rows:
        row_table, record, run = parse_id(str(row["id"]))
        if row_table != table:
            raise ValueError(f"review row {row['id']} does not match table {table}")
        review_by_key[(record, run)] = row

    changes: list[dict[str, Any]] = []
    target_keys: set[tuple[int, int]] = set()
    for row in payload["entries"]:
        key = (int(row["record"]), int(row.get("run", 0)))
        target_keys.add(key)
        review = review_by_key.get(key)
        if review is None:
            continue
        review_id = str(review["id"])
        new = normalize_runtime_text(RUNTIME_FIT_OVERRIDES.get(review_id, str(review.get("chs", ""))))
        max_units = source_max_units(row)
        unit_count = translation_units(new)
        if max_units is not None and unit_count > max_units:
            raise ValueError(
                f"{table}#{key[0]:04d}:{key[1]} exceeds source units: {unit_count} > {max_units}: {new!r}"
            )
        old = str(row.get("chs_draft", ""))
        row["chs_draft"] = new
        row["source"] = "translation_reviewed"
        row["notes"] = append_note(
            str(row.get("notes", "")),
            "reviewed_v41_fit" if review_id in RUNTIME_FIT_OVERRIDES else "reviewed_v41",
        )
        if old != new:
            changes.append({"id": review["id"], "old": old, "new": new, "max_units": max_units})

    missing_targets = sorted(set(review_by_key) - target_keys)
    if missing_targets:
        raise ValueError(f"review rows missing from target sheet {table}: {missing_targets[:20]}")
    return changes


def copy_equipment_review(review_root: Path, review_output: Path) -> dict[str, Any]:
    source = review_root / "equipment.json"
    rows = load_rows(source)
    target = review_output / "equipment.json"
    write_json(target, rows)
    return {
        "file": "equipment.json",
        "table": "DATA001/0015",
        "rows": len(rows),
        "changed_rows": count_equipment_changes(rows),
        "rough_markers": count_rough(rows),
        "target": "generated separately by tools/make_equipment_jp_first_layers.py",
        "review": target.as_posix(),
        "sample_changes": [],
    }


def count_equipment_changes(rows: list[dict[str, Any]]) -> int:
    count = 0
    for row in rows:
        current = row.get("current_chs")
        if current is not None and current != row.get("chs_unshrunk"):
            count += 1
    return count


def translation_units(text: str) -> int:
    return sum(1 for _ in iter_translation_tokens(text.replace("\r\n", "\n").replace("\r", "\n")))


def normalize_runtime_text(text: str) -> str:
    return text.replace("\u3000", " ")


def source_max_units(row: dict[str, Any]) -> int | None:
    if "source_max_units" in row:
        return int(row["source_max_units"])
    if "max_units" in row:
        return int(row["max_units"])
    return None


def parse_id(record_id: str) -> tuple[str, int, int]:
    match = re.fullmatch(r"([^#]+)#(\d+):(\d+)", record_id)
    if not match:
        raise ValueError(f"unsupported record id: {record_id!r}")
    return match.group(1), int(match.group(2)), int(match.group(3))


def append_note(existing: str, note: str) -> str:
    parts = [part.strip() for part in existing.split("|") if part.strip()]
    if note not in parts:
        parts.append(note)
    return " | ".join(parts)


def count_rough(rows: list[dict[str, Any]]) -> int:
    return sum(1 for row in rows if "粗译" in json.dumps(row, ensure_ascii=False))


def write_readme(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Translation Review Slim v12 Reviewed All",
        "",
        f"Source: `{summary['source_review_root']}`",
        f"Target sheets: `{summary['target_root']}`",
        "",
        "Files:",
        "",
    ]
    for item in summary["files"]:
        lines.append(
            f"- `{item['file']}`: {item['rows']} rows, {item['changed_rows']} changed/promoted, "
            f"{item['rough_markers']} rough markers"
        )
    lines.extend(
        [
            "",
            "Totals:",
            "",
            f"- entries: {summary['totals']['entries']}",
            f"- changed/promoted rows: {summary['totals']['changed_rows']}",
            f"- rough markers: {summary['totals']['rough_markers']}",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
