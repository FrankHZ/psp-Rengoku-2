from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_REVIEW_ROOT = Path("translation_reviewed")
DEFAULT_CODE_ROWS = Path("local/work/full_jp_text_decode_v1/full_jp_texts.json")
DEFAULT_GLYPH_MAP = Path("local/work/full_jp_text_decode_v1/reviewed_jp_glyph_map.csv")
DEFAULT_OUTPUT_DIR = Path("local/work/translation_review_reviewedjp_spacecodes_v44")

SPECIAL_RAW_CODE_ROWS = {
    "DATA002/0065#0085:0": "symbol/low-code row is not reliably decoded by reviewed_jp_glyph_map",
}

GRAM_CODES = [ord(char) for char in "#GRAM#"]

BUTTON_ICON_TOKENS = {
    0x0283: "<icon:L>",
    0x0284: "<icon:L>",
    0x0285: "<icon:R>",
    0x0286: "<icon:R>",
    0x0287: "<icon:○>",
    0x0288: "<icon:×>",
    0x0289: "<icon:△>",
    0x028A: "<icon:□>",
}

REVIEW_FILES = (
    "boot_ui.json",
    "tutorial.json",
    "story_data001_0012.json",
    "ui.json",
    "help_manual.json",
    "data002_ui.json",
    "story_data003_1089.json",
    "equipment.json",
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export reviewer JSON with chs from translation_reviewed and jp rendered from source codes."
    )
    parser.add_argument("--review-root", type=Path, default=DEFAULT_REVIEW_ROOT)
    parser.add_argument("--source-code-rows", type=Path, default=DEFAULT_CODE_ROWS)
    parser.add_argument("--glyph-map", type=Path, default=DEFAULT_GLYPH_MAP)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    code_rows = load_code_rows(args.source_code_rows)
    glyphs = load_glyph_map(args.glyph_map)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    files_summary: dict[str, Any] = {}
    totals = {
        "matched_code_rows": 0,
        "fallback_rows": 0,
        "gram_token_rows": 0,
        "icon_token_rows": 0,
        "icon_token_count": 0,
    }

    for name in REVIEW_FILES:
        review_path = args.review_root / name
        if not review_path.exists():
            continue
        rows = load_review_rows(review_path)
        out_rows: list[dict[str, Any]] = []
        stats = {
            "rows": len(rows),
            "matched_code_rows": 0,
            "fallback_rows": 0,
            "gram_token_rows": 0,
            "icon_token_rows": 0,
            "icon_token_count": 0,
        }
        for row in rows:
            record_id = str(row["id"])
            source = code_rows.get(record_id)
            rendered = str(row.get("jp", ""))
            if source is None:
                stats["fallback_rows"] += 1
            else:
                codes = source["codes"]
                if record_id in SPECIAL_RAW_CODE_ROWS:
                    rendered = " ".join(f"0x{code:04x}" for code in codes)
                else:
                    rendered = render_code_aware_jp(codes, glyphs)
                stats["matched_code_rows"] += 1

            gram_tokens = rendered.count("#GRAM#")
            icon_tokens = rendered.count("<icon:")
            if gram_tokens:
                stats["gram_token_rows"] += 1
            if icon_tokens:
                stats["icon_token_rows"] += 1
                stats["icon_token_count"] += icon_tokens

            chs = review_chs_text(row)
            if "#GRAM#" in rendered:
                chs = normalize_hash_gram_for_review(chs)
            out_rows.append(
                {
                    "id": row.get("id", ""),
                    "category": row.get("category", ""),
                    "chs": chs,
                    "jp": rendered,
                }
            )

        write_json(args.output_dir / name, out_rows)
        files_summary[name] = stats
        for key in totals:
            totals[key] += stats[key]

    summary = {
        "source_review_dir": str(args.review_root),
        "source_code_rows": str(args.source_code_rows),
        "source_glyph_map": str(args.glyph_map),
        "output_dir": str(args.output_dir),
        "policy": {
            "chs": "current translation_reviewed chs",
            "jp": "source-code-aware reviewed JP view",
            "jp_0x0020": " ",
            "jp_0x0100": "\u3000",
            "jp_0x000A": "\\n",
            "jp_0x0023_0x0047_0x0052_0x0041_0x004d_0x0023": "#GRAM#",
            "jp_button_icons": {
                "0x0283_or_0x0284": "<icon:L>",
                "0x0285_or_0x0286": "<icon:R>",
                "0x0287": "<icon:○>",
                "0x0288": "<icon:×>",
                "0x0289": "<icon:△>",
                "0x028a": "<icon:□>",
            },
            "dropped_fields": ["en", "fit_note"],
        },
        "files": files_summary,
        **totals,
        "special_cases": {
            record_id: {
                "reason": reason,
                "jp": "raw source code sequence",
                "chs": "current translation_reviewed chs",
            }
            for record_id, reason in SPECIAL_RAW_CODE_ROWS.items()
        },
    }
    write_json(args.output_dir / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def load_review_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"expected a JSON list: {path}")
    return payload


def load_code_rows(path: Path) -> dict[str, dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows: dict[str, dict[str, Any]] = {}
    for row in payload.get("entries", []):
        record_path = str(row.get("record_path", ""))
        if not record_path:
            continue
        rows[record_path] = {"codes": parse_codes(row.get("codes"))}
    return rows


def load_glyph_map(path: Path) -> dict[int, str]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return {int(row["code"], 16): row["char"] for row in csv.DictReader(file) if row.get("code")}


def parse_codes(raw: Any) -> list[int]:
    if not isinstance(raw, list):
        return []
    codes: list[int] = []
    for item in raw:
        if isinstance(item, int):
            codes.append(item)
        elif isinstance(item, str):
            codes.append(int(item, 16 if item.lower().startswith("0x") else 10))
    return codes


def render_code_aware_jp(codes: list[int], glyphs: dict[int, str]) -> str:
    parts: list[str] = []
    index = 0
    while index < len(codes):
        if codes[index : index + len(GRAM_CODES)] == GRAM_CODES:
            parts.append("#GRAM#")
            index += len(GRAM_CODES)
            continue

        code = codes[index]
        if code in BUTTON_ICON_TOKENS:
            parts.append(BUTTON_ICON_TOKENS[code])
        elif code == 0x000A:
            parts.append("\n")
        elif code == 0x0020:
            parts.append(" ")
        elif code == 0x0100:
            parts.append("\u3000")
        elif 0x20 <= code < 0x7F:
            parts.append(chr(code))
        else:
            parts.append(glyphs.get(code, f"<code:{code:04x}>"))
        index += 1
    return "".join(parts)


def normalize_hash_gram_for_review(text: str) -> str:
    return text.replace("GRAM", "#GRAM#").replace("gram", "#GRAM#")


def review_chs_text(row: dict[str, Any]) -> str:
    for key in ("chs", "chs_unshrunk", "current_chs", "chs_shrunk"):
        value = row.get(key)
        if value is not None:
            return str(value)
    return ""


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
