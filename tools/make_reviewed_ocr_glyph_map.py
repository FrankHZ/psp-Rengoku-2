from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path("local/work/jp_glyph_clear_pages_v1")

# These OCR blocks have exactly one recognized glyph per logical cell and pass
# a visual spot-check on the 2bpp combined sheet.
RELIABLE_FULL_BLOCKS = {6, 7, 9, 13, 14, 17, 18, 19, 22}

# These are 81-cell pages where Google returned one or two extra characters at
# the end. The first 81 cells are useful candidates, but keep them review-marked.
PREFIX_CANDIDATE_BLOCKS = {10, 11, 12, 16, 20}

# Page 24 is the partially populated child 11 low page: first 33 cells have ink.
PARTIAL_PREFIX_BLOCKS = {24: 33}

# Blocks where omitted symbols/kana make raw sequential OCR alignment unsafe.
UNSAFE_SHIFTED_BLOCKS = {1, 2, 3, 4, 5, 8, 15, 21}


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a reviewed glyph map from seeded labels and OCR block output.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--joined", type=Path, default=DEFAULT_ROOT / "ocr_joined_map.csv")
    parser.add_argument("--output", type=Path, default=DEFAULT_ROOT / "ocr_reviewed_map.csv")
    parser.add_argument("--summary", type=Path, default=DEFAULT_ROOT / "ocr_reviewed_summary.json")
    args = parser.parse_args()

    rows = read_csv(args.joined)
    reviewed = [review_row(row) for row in rows]
    summary = summarize(reviewed)
    write_csv(args.output, reviewed)
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=True, indent=2))
    return 0


def review_row(row: dict[str, str]) -> dict[str, Any]:
    block = int(row["block"])
    cell = int(row["cell"])
    seed_char = row.get("seed_char", "")
    seed_status = row.get("seed_status", "")
    ocr_char = row.get("ocr_char", "")

    reviewed_char = ""
    review_status = "unresolved"
    review_source = ""
    review_notes = ""

    if seed_char and seed_status == "seeded":
        reviewed_char = seed_char
        review_status = "confirmed_seed"
        review_source = "seed"
    elif block in RELIABLE_FULL_BLOCKS and ocr_char:
        reviewed_char = ocr_char
        review_status = "reviewed_ocr_full_block"
        review_source = "ocr"
    elif block in PREFIX_CANDIDATE_BLOCKS and ocr_char:
        reviewed_char = ocr_char
        review_status = "ocr_prefix_candidate"
        review_source = "ocr"
        review_notes = "block has extra OCR tail; first 81 glyphs look structurally usable but need review"
    elif block in PARTIAL_PREFIX_BLOCKS and cell < PARTIAL_PREFIX_BLOCKS[block] and ocr_char:
        reviewed_char = ocr_char
        review_status = "reviewed_ocr_partial_block"
        review_source = "ocr"
    elif seed_char and seed_status == "inferred_sequence":
        reviewed_char = seed_char
        review_status = "inferred_sequence"
        review_source = "sequence"
        review_notes = "not PPSSPP-confirmed; keep separate from confirmed seed"
    elif block in UNSAFE_SHIFTED_BLOCKS:
        review_status = "needs_alignment_review"
        review_source = "ocr" if ocr_char else ""
        review_notes = "OCR block has missing/shifted cells; do not promote raw sequential char"
    elif not ocr_char:
        review_status = "blank_or_missing_ocr"

    return {
        **row,
        "reviewed_char": reviewed_char,
        "review_status": review_status,
        "review_source": review_source,
        "review_notes": review_notes,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["review_status"]] = counts.get(row["review_status"], 0) + 1
    coded_rows = [row for row in rows if row.get("code")]
    filled = [row for row in coded_rows if row.get("reviewed_char")]
    return {
        "artifact": "local/work/jp_glyph_clear_pages_v1/ocr_reviewed_map.csv",
        "rows_total": len(rows),
        "coded_rows": len(coded_rows),
        "reviewed_chars": len(filled),
        "counts": dict(sorted(counts.items())),
        "reliable_full_blocks": sorted(RELIABLE_FULL_BLOCKS),
        "prefix_candidate_blocks": sorted(PREFIX_CANDIDATE_BLOCKS),
        "partial_prefix_blocks": PARTIAL_PREFIX_BLOCKS,
        "unsafe_shifted_blocks": sorted(UNSAFE_SHIFTED_BLOCKS),
    }


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
