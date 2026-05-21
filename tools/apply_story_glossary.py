from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply the CHS story name glossary to DATA003/1089 target/review sheets.")
    parser.add_argument("--glossary", type=Path, default=Path("docs/chs-glossary.json"))
    parser.add_argument(
        "--target",
        type=Path,
        default=Path("local/work/translation_refine_v1/merged_target_sheets_v41_reviewed_all/DATA003_1089_jp_first_target_sheet.json"),
    )
    parser.add_argument(
        "--review",
        type=Path,
        default=Path("local/work/translation_review_slim_v12_reviewed_all/story_data003_1089.json"),
    )
    parser.add_argument(
        "--target-output",
        type=Path,
        default=Path("local/work/translation_refine_v1/merged_target_sheets_v41_reviewed_all/DATA003_1089_jp_first_target_sheet.json"),
    )
    parser.add_argument(
        "--review-output",
        type=Path,
        default=Path("local/work/translation_review_slim_v12_reviewed_all/story_data003_1089.json"),
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("local/work/translation_refine_v1/merged_target_sheets_v41_reviewed_all/story_glossary_summary.json"),
    )
    args = parser.parse_args()

    replacements = load_replacements(args.glossary)
    target_payload = json.loads(args.target.read_text(encoding="utf-8"))
    review_rows = json.loads(args.review.read_text(encoding="utf-8"))

    target_changes = apply_to_target(target_payload, replacements)
    review_changes = apply_to_review(review_rows, replacements)

    args.target_output.parent.mkdir(parents=True, exist_ok=True)
    args.review_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.target_output.write_text(json.dumps(target_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.review_output.write_text(json.dumps(review_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {
        "target_rows_changed": len(target_changes),
        "review_rows_changed": len(review_changes),
        "target_changes": target_changes,
        "review_changes": review_changes,
    }
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"target_rows_changed": len(target_changes), "review_rows_changed": len(review_changes)}, ensure_ascii=False, indent=2))
    return 0


def load_replacements(path: Path) -> list[tuple[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    replacements: list[tuple[str, str]] = []
    for term in payload["terms"]:
        target = str(term["chs"])
        for source in term.get("replace", []):
            source_text = str(source)
            if source_text and source_text != target:
                replacements.append((source_text, target))
    replacements.sort(key=lambda item: len(item[0]), reverse=True)
    return replacements


def apply_terms(text: str, replacements: list[tuple[str, str]]) -> str:
    result = text
    for source, target in replacements:
        result = replace_term(result, source, target)
    return result


def replace_term(text: str, source: str, target: str) -> str:
    if target.startswith(source):
        suffix = target[len(source) :]
        if suffix:
            return re.sub(re.escape(source) + rf"(?!{re.escape(suffix)})", target, text)
    return text.replace(source, target)


def apply_to_target(payload: dict[str, Any], replacements: list[tuple[str, str]]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for row in payload["entries"]:
        old = str(row.get("chs_draft", ""))
        new = apply_terms(old, replacements)
        if new == old:
            continue
        row["chs_draft"] = new
        row["notes"] = f"{row.get('notes', '')} | glossary_v1".strip(" |")
        changes.append({"record": row.get("record"), "run": row.get("run"), "old": old, "new": new})
    return changes


def apply_to_review(rows: list[dict[str, Any]], replacements: list[tuple[str, str]]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for row in rows:
        old = str(row.get("chs", ""))
        new = apply_terms(old, replacements)
        if new == old:
            continue
        row["chs"] = new
        row["fit_note"] = f"{row.get('fit_note', '')}|glossary_v1".strip("|")
        changes.append({"id": row.get("id"), "old": old, "new": new})
    return changes


if __name__ == "__main__":
    raise SystemExit(main())
