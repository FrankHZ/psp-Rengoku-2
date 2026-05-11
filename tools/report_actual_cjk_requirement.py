from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from build_chs_tutorial import visible_translation_chars


DEFAULT_ROW_QUEUE = Path("local/work/full_translation_glyph_estimate_v1/row_queue.csv")
DEFAULT_OUTPUT = Path("local/work/actual_cjk_requirement_v1")
DEFAULT_OVERRIDES = Path("local/work/actual_cjk_requirement_v1/translation_overrides.json")


def main() -> int:
    parser = argparse.ArgumentParser(description="Report actual unique CJK needed by translated/current rows.")
    parser.add_argument("--row-queue", type=Path, default=DEFAULT_ROW_QUEUE)
    parser.add_argument("--overrides", type=Path, default=DEFAULT_OVERRIDES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    rows = read_csv(args.row_queue)
    overrides = read_overrides(args.overrides)
    merged = merge_rows(rows, overrides)
    summary = summarize(merged)

    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "actual_rows.csv", merged)
    write_csv(args.output / "missing_rows.csv", [row for row in merged if row["actual_status"] == "missing"])
    write_csv(args.output / "per_table_summary.csv", per_table_rows(merged))
    (args.output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
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


def read_overrides(path: Path) -> dict[tuple[str, int, int], dict[str, Any]]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    overrides = {}
    for row in payload.get("entries", []):
        overrides[(str(row["table"]), int(row["record"]), int(row.get("run", 0)))] = row
    return overrides


def merge_rows(rows: list[dict[str, str]], overrides: dict[tuple[str, int, int], dict[str, Any]]) -> list[dict[str, Any]]:
    merged = []
    seen = set()
    for row in rows:
        key = (row["table"], int(row["record"]), int(row["run"]))
        seen.add(key)
        override = overrides.get(key)
        translation = row.get("translation", "")
        status = "translated" if translation else "missing"
        source = row.get("status", "")
        notes = row.get("notes", "")
        if override:
            translation = str(override.get("translation", ""))
            status = str(override.get("status", "translated" if translation else "missing"))
            source = str(override.get("source", "override"))
            notes = str(override.get("notes", notes))
        elif row.get("status") == "missing_translation" and row.get("source_text", "").startswith("reserved"):
            translation = row["source_text"]
            status = "ascii_passthrough"
            source = "reserved_passthrough"
            notes = "ASCII reserved placeholder; no CJK needed."
        elif row.get("status") == "missing_translation" and is_ascii_passthrough(row.get("source_text", "")):
            translation = row["source_text"]
            status = "ascii_passthrough"
            source = "source_ascii_passthrough"
            notes = "ASCII source passthrough; no CJK needed."
        actual = dict(row)
        actual["actual_translation"] = translation
        actual["actual_status"] = status
        actual["actual_source"] = source
        actual["actual_notes"] = notes
        actual["actual_cjk_glyphs"] = "".join(sorted(cjk_chars(translation)))
        merged.append(actual)
    for key, override in sorted(overrides.items()):
        if key in seen:
            continue
        table, record, run = key
        translation = str(override.get("translation", ""))
        status = str(override.get("status", "translated" if translation else "missing"))
        actual = {
            "table": table,
            "record": record,
            "run": run,
            "kind": str(override.get("kind", "")),
            "length": str(override.get("length", "")),
            "status": "extra_candidate",
            "translation": "",
            "source_text": str(override.get("source_text", "")),
            "notes": str(override.get("notes", "")),
            "actual_translation": translation,
            "actual_status": status,
            "actual_source": str(override.get("source", "extra_override")),
            "actual_notes": str(override.get("notes", "")),
            "actual_cjk_glyphs": "".join(sorted(cjk_chars(translation))),
        }
        merged.append(actual)
    return merged


def is_ascii_passthrough(text: str) -> bool:
    return bool(text) and all(ord(char) < 0x80 for char in text)


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    all_cjk = set()
    all_non_ascii = set()
    statuses: dict[str, int] = {}
    for row in rows:
        statuses[row["actual_status"]] = statuses.get(row["actual_status"], 0) + 1
        for char in visible_translation_chars(str(row.get("actual_translation", ""))):
            if ord(char) > 0x7E:
                all_non_ascii.add(char)
            if is_cjk(char):
                all_cjk.add(char)
    return {
        "rows": len(rows),
        "status_counts": dict(sorted(statuses.items())),
        "translated_or_passthrough_rows": sum(count for status, count in statuses.items() if status != "missing"),
        "missing_rows": statuses.get("missing", 0),
        "unique_cjk_required": len(all_cjk),
        "unique_non_ascii_required": len(all_non_ascii),
        "unique_cjk_chars": "".join(sorted(all_cjk)),
    }


def per_table_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tables: dict[str, dict[str, Any]] = {}
    for row in rows:
        table = str(row["table"])
        entry = tables.setdefault(
            table,
            {
                "table": table,
                "rows": 0,
                "missing": 0,
                "unique_cjk_required": 0,
                "_chars": set(),
            },
        )
        entry["rows"] += 1
        if row["actual_status"] == "missing":
            entry["missing"] += 1
        entry["_chars"].update(cjk_chars(str(row.get("actual_translation", ""))))
    result = []
    for entry in sorted(tables.values(), key=lambda item: item["table"]):
        chars = entry.pop("_chars")
        entry["unique_cjk_required"] = len(chars)
        result.append(entry)
    return result


def cjk_chars(text: str) -> set[str]:
    return {char for char in visible_translation_chars(text) if is_cjk(char)}


def is_cjk(char: str) -> bool:
    value = ord(char)
    return (
        0x3400 <= value <= 0x4DBF
        or 0x4E00 <= value <= 0x9FFF
        or 0xF900 <= value <= 0xFAFF
        or 0x20000 <= value <= 0x2A6DF
        or 0x2A700 <= value <= 0x2B73F
        or 0x2B740 <= value <= 0x2B81F
        or 0x2B820 <= value <= 0x2CEAF
    )


if __name__ == "__main__":
    raise SystemExit(main())
