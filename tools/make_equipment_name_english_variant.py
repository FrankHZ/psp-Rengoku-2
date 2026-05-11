from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any

from build_chs_tutorial import needs_glyph_assignment


DEFAULT_INPUT = Path("local/work/equipment_chs_full_buildfit/DATA001_0015_equipment_chs_full_buildfit.json")
DEFAULT_OUTPUT_DIR = Path("local/work/equipment_chs_name_english_v1")
DEFAULT_OUTPUT_JSON = DEFAULT_OUTPUT_DIR / "DATA001_0015_equipment_name_english.json"
DEFAULT_OUTPUT_CSV = DEFAULT_OUTPUT_DIR / "DATA001_0015_equipment_name_english.csv"

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a readable DATA001/0015 variant with actual English names only when they fit."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    args = parser.parse_args()

    payload, summary = make_equipment_name_english_variant(args.input)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(args.output_csv, payload["entries"])
    summary.update(
        {
            "source_sheet": str(args.input).replace("\\", "/"),
            "output_json": str(args.output_json).replace("\\", "/"),
            "output_csv": str(args.output_csv).replace("\\", "/"),
        }
    )
    summary_path = args.output_json.parent / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def make_equipment_name_english_variant(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload["entries"]
    changed = 0
    ascii_name_rows = 0
    chinese_fallback_rows = 0
    before_chars = assigned_chars(entries)

    for row in entries:
        if row.get("role") != "name":
            continue
        max_units = int(row.get("source_max_units", 0))
        original = str(row.get("chs_draft", ""))
        candidate, used_chinese_fallback = readable_name_for_row(row, max_units)
        if candidate == "":
            continue
        if len(candidate) > max_units:
            raise ValueError(f"record {row.get('record')} generated {candidate!r} over budget {max_units}")
        row["chs_draft"] = candidate
        row["chs_units"] = len(candidate)
        row["chs_fits_source_budget"] = True
        note = "equipment_name_readable: actual English kept only when it fits; otherwise CHS name retained."
        row["notes"] = f"{row.get('notes', '')} {note}".strip()
        if candidate != original:
            changed += 1
        if is_ascii_text(candidate):
            ascii_name_rows += 1
        if used_chinese_fallback:
            chinese_fallback_rows += 1

    after_chars = assigned_chars(entries)
    payload["role"] = "equipment/catalog CHS draft with readable equipment names"
    payload["source_sheet"] = str(path).replace("\\", "/")
    return payload, {
        "rows": len(entries),
        "name_rows": sum(1 for row in entries if row.get("role") == "name"),
        "ascii_name_rows": ascii_name_rows,
        "changed_name_rows": changed,
        "chinese_fallback_name_rows": chinese_fallback_rows,
        "assigned_chars_before": len(before_chars),
        "assigned_chars_after": len(after_chars),
        "assigned_chars_saved": len(before_chars) - len(after_chars),
    }


def readable_name_for_row(row: dict[str, Any], max_units: int) -> tuple[str, bool]:
    current = str(row.get("chs_draft", "")).strip()
    usa_text = str(row.get("usa_text", "")).strip()
    if row.get("usa_kind") == "text" and usa_text and usa_text != "0":
        actual = actual_ascii_name(usa_text, max_units)
        if actual:
            return actual, False
        if current and len(current) <= max_units:
            return current, not is_ascii_text(current)
    if current and is_ascii_text(current) and len(current) <= max_units:
        return current, False
    if current and len(current) <= max_units:
        return current, not is_ascii_text(current)
    return "", False


def actual_ascii_name(text: str, max_units: int) -> str:
    cleaned = normalize_ascii(text)
    if len(cleaned) <= max_units:
        return cleaned

    nospace = cleaned.replace(" ", "")
    if len(nospace) <= max_units:
        return nospace

    return ""


def normalize_ascii(text: str) -> str:
    text = text.replace("\u2019", "'").replace("\u2013", "-").replace("\u2014", "-")
    text = re.sub(r"[^A-Za-z0-9+_. -]+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.upper()


def assigned_chars(entries: list[dict[str, Any]]) -> set[str]:
    return {
        char
        for row in entries
        for char in str(row.get("chs_draft", ""))
        if needs_glyph_assignment(char)
    }


def is_ascii_text(text: str) -> bool:
    return all(char == "\n" or 0x20 <= ord(char) <= 0x7E for char in text)


def write_csv(path: Path, entries: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in entries:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)


if __name__ == "__main__":
    raise SystemExit(main())
