from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from build_chs_tutorial import needs_glyph_assignment, visible_translation_chars


DEFAULT_ACTUAL_ROWS = Path("local/work/actual_cjk_requirement_v1/actual_rows.csv")
DEFAULT_BUILD_ROOT = Path("local/work/combined_chs_v23_tutorial_usa_aligned_bitplane")
DEFAULT_OUTPUT = Path("local/work/chs_font_corpus_v1")


def main() -> int:
    parser = argparse.ArgumentParser(description="Export CHS translated text corpora for external font generation.")
    parser.add_argument("--actual-rows", type=Path, default=DEFAULT_ACTUAL_ROWS)
    parser.add_argument("--build-root", type=Path, default=DEFAULT_BUILD_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    actual_rows = read_csv(args.actual_rows)
    build_rows = read_build_rows(args.build_root)
    args.output.mkdir(parents=True, exist_ok=True)

    actual_translations = [
        str(row.get("actual_translation", ""))
        for row in actual_rows
        if row.get("actual_status") not in {"", "missing"} and row.get("actual_translation")
    ]
    build_translations = [
        str(row.get("translation", ""))
        for row in build_rows
        if row.get("translation")
    ]

    actual_chars = collect_chars(actual_translations)
    build_chars = collect_chars(build_translations)

    write_text(args.output / "translated_chs_all_lines.txt", actual_translations)
    write_text(args.output / "current_build_chs_all_lines.txt", build_translations)
    write_text(args.output / "translated_chs_unique_font_chars.txt", ["".join(sorted(actual_chars["font"], key=ord))])
    write_text(args.output / "translated_chs_unique_cjk.txt", ["".join(sorted(actual_chars["cjk"], key=ord))])
    write_text(args.output / "translated_chs_unique_all_visible.txt", ["".join(sorted(actual_chars["visible"], key=ord))])
    write_text(args.output / "current_build_unique_font_chars.txt", ["".join(sorted(build_chars["font"], key=ord))])

    summary = {
        "actual_rows": str(args.actual_rows),
        "build_root": str(args.build_root),
        "translated_lines": len(actual_translations),
        "current_build_lines": len(build_translations),
        "translated_unique_visible": len(actual_chars["visible"]),
        "translated_unique_font_chars": len(actual_chars["font"]),
        "translated_unique_cjk": len(actual_chars["cjk"]),
        "current_build_unique_font_chars": len(build_chars["font"]),
        "notes": [
            "translated_chs_unique_font_chars.txt is the main input for external font generation.",
            "The current build path assigns generated font cells only to CJK ideographs.",
            "Latin, digits, punctuation, button icons, and reviewed symbols should reuse original source glyph codes.",
            "translated_chs_unique_font_chars.txt should therefore match the CJK-only set unless the assignment policy changes.",
        ],
    }
    (args.output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_readme(args.output / "README.md", summary)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_build_rows(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(root.glob("DATA???_????_chs.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for entry in payload.get("entries", []):
            row = dict(entry)
            row["file"] = path.name
            rows.append(row)
    return rows


def collect_chars(translations: list[str]) -> dict[str, set[str]]:
    visible: set[str] = set()
    font: set[str] = set()
    cjk: set[str] = set()
    for text in translations:
        for char in visible_translation_chars(text):
            if char in {"\r", "\n", "\t", " "}:
                continue
            visible.add(char)
            if needs_glyph_assignment(char):
                font.add(char)
            if is_cjk(char):
                cjk.add(char)
    return {"visible": visible, "font": font, "cjk": cjk}


def is_cjk(char: str) -> bool:
    codepoint = ord(char)
    return (
        0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xF900 <= codepoint <= 0xFAFF
        or 0x20000 <= codepoint <= 0x2EBEF
    )


def write_text(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_readme(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# CHS Font Corpus",
        "",
        "Text exports for generating an external CHS font atlas.",
        "",
        "Main file:",
        "",
        "- `translated_chs_unique_font_chars.txt`: all unique translated CJK chars that need generated CHS font glyphs.",
        "",
        "Reference files:",
        "",
        "- `translated_chs_unique_cjk.txt`: CJK-only subset; should match the font-char file under the current policy.",
        "- `translated_chs_unique_all_visible.txt`: all visible translated chars, including ASCII.",
        "- `translated_chs_all_lines.txt`: all translated/passthrough lines from `actual_rows.csv`.",
        "- `current_build_unique_font_chars.txt`: current v23 build assigned-char corpus only.",
        "- `current_build_chs_all_lines.txt`: current v23 build translated lines only.",
        "",
        "Counts:",
        "",
        f"- translated unique font chars: {summary['translated_unique_font_chars']}",
        f"- translated unique CJK chars: {summary['translated_unique_cjk']}",
        f"- current build unique font chars: {summary['current_build_unique_font_chars']}",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
