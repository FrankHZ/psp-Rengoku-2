from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path("local/work/jp_glyph_clear_pages_v1")
DEFAULT_TABLE = Path("local/work/jp_glyph_table_v1/jp_glyph_map.csv")


def main() -> int:
    parser = argparse.ArgumentParser(description="Join block OCR output back to glyph page/cell/code mapping.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--ocr", type=Path, default=DEFAULT_ROOT / "ocr.csv")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_ROOT / "manifest.csv")
    parser.add_argument("--seed-table", type=Path, default=DEFAULT_TABLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_ROOT / "ocr_joined_map.csv")
    parser.add_argument("--summary", type=Path, default=DEFAULT_ROOT / "ocr_summary.json")
    args = parser.parse_args()

    joined, summary = join_ocr(args.root, args.ocr, args.manifest, args.seed_table)
    write_csv(args.output, joined)
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=True, indent=2))
    return 0


def join_ocr(
    root: Path,
    ocr_path: Path,
    manifest_path: Path,
    seed_table_path: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ocr_rows = read_ocr_rows(ocr_path)
    manifest_rows = read_csv(manifest_path)
    seed_by_code = load_seed_table(seed_table_path)
    ordered_pages = sorted((root / "original_pages_scaled").glob("*.png"))
    if len(ocr_rows) != len(ordered_pages):
        raise ValueError(f"OCR rows ({len(ocr_rows)}) do not match scaled pages ({len(ordered_pages)})")

    manifest_by_page: dict[str, list[dict[str, str]]] = {}
    for row in manifest_rows:
        manifest_by_page.setdefault(str(row["original_scaled_page_png"]), []).append(row)
    for rows in manifest_by_page.values():
        rows.sort(key=lambda row: int(row["cell"]))

    joined: list[dict[str, Any]] = []
    block_summaries = []
    for block_index, (ocr_row, page_path) in enumerate(zip(ocr_rows, ordered_pages, strict=True), start=1):
        page_key = f"original_pages_scaled/{page_path.name}"
        cells = manifest_by_page.get(page_key)
        if cells is None:
            raise ValueError(f"manifest does not contain page {page_key}")
        glyphs = list(str(ocr_row.get("Glyphs") or ""))
        expected = len(cells)
        assigned = min(len(glyphs), expected)
        block_summaries.append(
            {
                "block": block_index,
                "page": page_key,
                "type": ocr_row.get("Type", ""),
                "expected_cells": expected,
                "glyphs": len(glyphs),
                "assigned": assigned,
                "missing": max(expected - len(glyphs), 0),
                "extra": max(len(glyphs) - expected, 0),
                "extra_text": "".join(glyphs[expected:]),
            }
        )
        for index, cell in enumerate(cells):
            ocr_char = glyphs[index] if index < len(glyphs) else ""
            code = str(cell.get("code") or "")
            seed = seed_by_code.get(code, {})
            seed_char = str(seed.get("char") or "")
            seed_status = str(seed.get("status") or "")
            joined.append(
                {
                    "block": block_index,
                    "block_row": ocr_row.get("Row", ""),
                    "block_col": ocr_row.get("Col", ""),
                    "block_type": ocr_row.get("Type", ""),
                    "page": page_key,
                    "block_glyph_count": len(glyphs),
                    "expected_cells": expected,
                    "ocr_index": index,
                    "ocr_char": ocr_char,
                    "ocr_status": "assigned" if ocr_char else "missing",
                    "seed_char": seed_char,
                    "seed_status": seed_status,
                    "seed_match": seed_match(seed_char, ocr_char),
                    "code": code,
                    "child": cell.get("child", ""),
                    "source": cell.get("source", ""),
                    "layer": cell.get("layer", ""),
                    "base": cell.get("base", ""),
                    "cell": cell.get("cell", ""),
                    "row": cell.get("row", ""),
                    "col": cell.get("col", ""),
                    "cell_png": cell.get("cell_png", ""),
                }
            )

    summary = summarize(joined, block_summaries, ocr_path, manifest_path, seed_table_path)
    return joined, summary


def read_ocr_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(line for line in file if line.strip()))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def load_seed_table(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    rows = read_csv(path)
    return {str(row["code"]): row for row in rows if row.get("code")}


def seed_match(seed_char: str, ocr_char: str) -> str:
    if not seed_char:
        return ""
    if not ocr_char:
        return "missing_ocr"
    return "match" if seed_char == ocr_char else "mismatch"


def summarize(
    joined: list[dict[str, Any]],
    blocks: list[dict[str, Any]],
    ocr_path: Path,
    manifest_path: Path,
    seed_table_path: Path,
) -> dict[str, Any]:
    nonempty_codes = [row for row in joined if row["code"]]
    assigned = [row for row in nonempty_codes if row["ocr_char"]]
    seed_rows = [row for row in nonempty_codes if row["seed_char"]]
    seed_matches = [row for row in seed_rows if row["seed_match"] == "match"]
    seed_mismatches = [row for row in seed_rows if row["seed_match"] == "mismatch"]
    missing_by_block = [block for block in blocks if block["missing"] or block["extra"]]
    return {
        "artifact": "local/work/jp_glyph_clear_pages_v1",
        "ocr_source": str(ocr_path),
        "manifest_source": str(manifest_path),
        "seed_table_source": str(seed_table_path),
        "blocks": len(blocks),
        "cells_total": len(joined),
        "coded_cells": len(nonempty_codes),
        "ocr_assigned_coded_cells": len(assigned),
        "ocr_missing_coded_cells": len(nonempty_codes) - len(assigned),
        "seed_rows_compared": len(seed_rows),
        "seed_matches": len(seed_matches),
        "seed_mismatches": len(seed_mismatches),
        "blocks_with_length_issues": len(missing_by_block),
        "block_summaries": blocks,
        "seed_mismatch_examples": [
            {
                "code": row["code"],
                "seed": row["seed_char"],
                "ocr": row["ocr_char"],
                "block": row["block"],
                "cell": row["cell"],
                "page": row["page"],
            }
            for row in seed_mismatches[:50]
        ],
    }


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
