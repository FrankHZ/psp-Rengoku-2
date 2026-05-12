from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_chs_tutorial import BITPLANE_SLOT_POOLS


DEFAULT_REVIEW_ROOT = Path("local/ocr_reviewed")
DEFAULT_WORK_ROOT = Path("local/work")
DEFAULT_OUTPUT_ROOT = Path("local/work/jp_glyph_usage_research_v1")

FILENAME_RE = re.compile(
    r"block(?P<block>\d+)_child(?P<child>\d+)_(?P<source>.+)_(?P<layer>high|low)\.txt$"
)

GEOMETRY = {
    "codeANK9x14_00_0": (14, 9),
    "codeJAP14x14_00_": (9, 9),
    "codeJAP14x14_02_": (9, 9),
    "codeJAP14x14_04_": (9, 9),
    "codeJAP14x14_06_": (9, 9),
    "codeJAP14x14_08_": (9, 9),
    "codeJAP14x14_10_": (9, 9),
    "codeJAP14x14_12_": (9, 9),
    "codeJAP14x14_14_": (9, 9),
    "codeJAP14x14_16_": (9, 9),
    "codeJAP14x14_18_": (9, 9),
    "codeJAP14x14_20_": (9, 9),
}

WATCH_BLOCKS = {
    "block01_child00_codeANK9x14_00_0_high",
    "block02_child00_codeANK9x14_00_0_low",
    "block03_child01_codeJAP14x14_00__high",
    "block08_child03_codeJAP14x14_04__low",
    "block12_child05_codeJAP14x14_08__low",
}

CONFIRMED_BLANK_OR_UNUSED_PAGES = {
    "block23_child11_codeJAP14x14_20__high": "unused block",
    "block24_child11_codeJAP14x14_20__low": "unused blank tail",
}

CONFIRMED_BLANK_OR_CONTROL_CELLS = {
    ("block02_child00_codeANK9x14_00_0_low", 0): "blank/control",
    ("block02_child00_codeANK9x14_00_0_low", 96): "blank/control",
    ("block02_child00_codeANK9x14_00_0_low", 97): "blank/control",
    ("block02_child00_codeANK9x14_00_0_low", 109): "blank/control",
    ("block02_child00_codeANK9x14_00_0_low", 110): "blank/control",
    ("block02_child00_codeANK9x14_00_0_low", 111): "blank/control",
    ("block02_child00_codeANK9x14_00_0_low", 112): "blank/control",
    ("block02_child00_codeANK9x14_00_0_low", 125): "blank/control",
    ("block03_child01_codeJAP14x14_00__high", 21): "blank/reserved",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Research reviewed JP glyph-cell usage in extracted records and raw bins.")
    parser.add_argument("--review-root", type=Path, default=DEFAULT_REVIEW_ROOT)
    parser.add_argument("--work-root", type=Path, default=DEFAULT_WORK_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()

    cells = read_reviewed_cells(args.review_root)
    extracted_usage = collect_extracted_usage(args.work_root)
    raw_usage = collect_raw_u16_usage(args.work_root, cells)
    rows = build_usage_rows(cells, extracted_usage, raw_usage)
    summary = summarize(rows, args.review_root, args.work_root, args.output_root)

    args.output_root.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_root / "reviewed_glyph_usage.csv", rows)
    write_csv(args.output_root / "watch_cells_usage.csv", [row for row in rows if row["watch_group"]])
    write_csv(args.output_root / "unknown_or_blank_used_cells.csv", unknown_or_blank_used_rows(rows))
    write_json(args.output_root / "summary.json", summary)
    write_markdown(args.output_root / "README.md", summary)
    print(json.dumps(summary, ensure_ascii=True, indent=2))
    return 0


def read_reviewed_cells(root: Path) -> list[dict[str, Any]]:
    bases = {
        (int(pool["child"]), str(pool["source"]), str(pool["layer"])): int(pool["base"])
        for pool in BITPLANE_SLOT_POOLS
    }
    rows: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.txt")):
        match = FILENAME_RE.match(path.name)
        if not match:
            continue
        block = int(match.group("block"))
        child = int(match.group("child"))
        source = match.group("source")
        layer = match.group("layer")
        cols, expected_rows = GEOMETRY[source]
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        if len(lines) != expected_rows:
            raise ValueError(f"{path} has {len(lines)} rows, expected {expected_rows}")
        base = bases.get((child, source, layer))
        page_key = path.stem
        for row_index, line in enumerate(lines):
            chars = normalize_review_line(page_key, row_index, list(line))
            if len(chars) != cols:
                raise ValueError(f"{path} row {row_index} has {len(chars)} cells, expected {cols}: {line!r}")
            for col_index, char in enumerate(chars):
                cell = row_index * cols + col_index
                code = code_for_cell(base, source, layer, cell)
                reviewed_char = "" if char == "□" and not is_literal_square_key(page_key, row_index, col_index) else char
                confirmed_blank = confirmed_blank_reason(page_key, cell)
                rows.append(
                    {
                        "page": page_key,
                        "block": block,
                        "child": child,
                        "source": source,
                        "layer": layer,
                        "base": f"0x{base:04x}" if base is not None else "",
                        "cell": cell,
                        "row": row_index,
                        "col": col_index,
                        "code_int": code,
                        "code": f"0x{code:04x}" if code is not None else "",
                        "reviewed_char": reviewed_char,
                        "is_blank_marker": char == "□" and not is_literal_square_key(page_key, row_index, col_index),
                        "confirmed_blank_reason": confirmed_blank,
                        "watch_group": page_key if page_key in WATCH_BLOCKS else "",
                    }
                )
    return rows


def normalize_review_line(page_key: str, row_index: int, chars: list[str]) -> list[str]:
    # The reviewer intentionally marked the two-cell L/R button glyphs compactly
    # as `LR` on block08 row 8. Expand them back to their physical cells:
    # L-left, L-right, R-left, R-right, circle, cross, triangle, square, close.
    if page_key == "block08_child03_codeJAP14x14_04__low" and row_index == 7 and len(chars) == 7:
        return [chars[0], chars[0], chars[1], chars[1], *chars[2:]]
    return chars


def is_literal_square_key(page_key: str, row_index: int, col_index: int) -> bool:
    return (
        page_key == "block08_child03_codeJAP14x14_04__low" and row_index == 7 and col_index == 7
    ) or (
        page_key == "block03_child01_codeJAP14x14_00__high" and row_index == 1 and col_index == 5
    )


def confirmed_blank_reason(page_key: str, cell: int) -> str:
    if page_key in CONFIRMED_BLANK_OR_UNUSED_PAGES:
        return CONFIRMED_BLANK_OR_UNUSED_PAGES[page_key]
    return CONFIRMED_BLANK_OR_CONTROL_CELLS.get((page_key, cell), "")


def code_for_cell(base: int | None, source: str, layer: str, cell: int) -> int | None:
    if source == "codeANK9x14_00_0":
        return cell if layer == "low" else None
    if base is None:
        return None
    return base + cell


def collect_extracted_usage(work_root: Path) -> dict[int, list[dict[str, Any]]]:
    usage: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for path in sorted(work_root.glob("*.json")):
        if not should_scan_json(path):
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        for context in iter_code_contexts(data):
            if context.get("kind") != "glyph_codes":
                continue
            for code in context.pop("codes"):
                usage[code].append({"file": path.as_posix(), **context})
    return usage


def should_scan_json(path: Path) -> bool:
    name = path.name
    return (
        name.startswith("extract_text_")
        or name.startswith("script_")
        or name.startswith("offset_table_runs_")
        or name.startswith("verify_")
    )


def iter_code_contexts(value: Any, trail: tuple[str, ...] = ()) -> list[dict[str, Any]]:
    contexts: list[dict[str, Any]] = []
    if isinstance(value, dict):
        codes = parse_codes(value.get("codes"))
        if codes:
            contexts.append(
                {
                    "codes": codes,
                    "json_path": ".".join(trail),
                    "id": value.get("id", ""),
                    "record": value.get("record", ""),
                    "run": value.get("run", ""),
                    "kind": value.get("kind", ""),
                    "text": value.get("text", ""),
                    "translation": value.get("translation", ""),
                }
            )
        for key, child in value.items():
            contexts.extend(iter_code_contexts(child, (*trail, str(key))))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            contexts.extend(iter_code_contexts(child, (*trail, str(index))))
    return contexts


def parse_codes(raw: Any) -> list[int]:
    if not isinstance(raw, list):
        return []
    codes = []
    for item in raw:
        if isinstance(item, int):
            codes.append(item)
        elif isinstance(item, str):
            try:
                codes.append(int(item, 16 if item.lower().startswith("0x") else 10))
            except ValueError:
                pass
    return codes


def collect_raw_u16_usage(work_root: Path, cells: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    codes = sorted({int(row["code_int"]) for row in cells if row["code_int"] is not None})
    bins = sorted((work_root / "mcd3_entries").glob("DATA*/*.bin"))
    usage: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for path in bins:
        data = path.read_bytes()
        for code in codes:
            needle = code.to_bytes(2, "little")
            offsets = find_offsets(data, needle, limit=20)
            if offsets:
                usage[code].append(
                    {
                        "file": path.as_posix(),
                        "hits": len(offsets),
                        "first_offsets": " ".join(f"0x{offset:x}" for offset in offsets[:10]),
                    }
                )
    return usage


def find_offsets(data: bytes, needle: bytes, limit: int) -> list[int]:
    offsets = []
    start = 0
    while len(offsets) < limit:
        found = data.find(needle, start)
        if found < 0:
            break
        if found % 2 == 0:
            offsets.append(found)
        start = found + 1
    return offsets


def build_usage_rows(
    cells: list[dict[str, Any]],
    extracted_usage: dict[int, list[dict[str, Any]]],
    raw_usage: dict[int, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    rows = []
    for cell in cells:
        code = cell["code_int"]
        extracted = extracted_usage.get(code, []) if code is not None else []
        raw = raw_usage.get(code, []) if code is not None else []
        rows.append(
            {
                **{key: value for key, value in cell.items() if key != "code_int"},
                "extracted_usage_count": len(extracted),
                "raw_bin_file_count": len(raw),
                "raw_bin_hit_count": sum(int(item["hits"]) for item in raw),
                "used_in_extracted_records": "yes" if extracted else "no",
                "seen_in_raw_bins": "yes" if raw else "no",
                "sample_extracted_contexts": json.dumps(extracted[:5], ensure_ascii=False),
                "sample_raw_contexts": json.dumps(raw[:5], ensure_ascii=False),
            }
        )
    rows.sort(key=lambda row: (int(row["block"]), int(row["cell"])))
    return rows


def unknown_or_blank_used_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row
        for row in rows
        if (not row["reviewed_char"] or row["is_blank_marker"])
        and not row.get("confirmed_blank_reason")
        and (row["used_in_extracted_records"] == "yes" or row["seen_in_raw_bins"] == "yes")
    ]


def summarize(rows: list[dict[str, Any]], review_root: Path, work_root: Path, output_root: Path) -> dict[str, Any]:
    watch: dict[str, Any] = {}
    for group in sorted(WATCH_BLOCKS):
        group_rows = [row for row in rows if row["watch_group"] == group]
        watch[group] = {
            "cells": len(group_rows),
            "addressable_cells": sum(1 for row in group_rows if row["code"]),
            "reviewed_chars": sum(1 for row in group_rows if row["reviewed_char"]),
            "extracted_used_cells": sum(1 for row in group_rows if row["used_in_extracted_records"] == "yes"),
            "raw_seen_cells": sum(1 for row in group_rows if row["seen_in_raw_bins"] == "yes"),
            "blank_or_unknown_used_cells": [
                {
                    "code": row["code"],
                    "cell": row["cell"],
                    "row": row["row"],
                    "col": row["col"],
                    "raw_bin_hit_count": row["raw_bin_hit_count"],
                    "extracted_usage_count": row["extracted_usage_count"],
                }
                for row in unknown_or_blank_used_rows(group_rows)
            ],
            "reviewed_specials_used": [
                {
                    "code": row["code"],
                    "char": row["reviewed_char"],
                    "cell": row["cell"],
                    "row": row["row"],
                    "col": row["col"],
                    "raw_bin_hit_count": row["raw_bin_hit_count"],
                    "extracted_usage_count": row["extracted_usage_count"],
                }
                for row in group_rows
                if row["reviewed_char"] and (row["used_in_extracted_records"] == "yes" or row["seen_in_raw_bins"] == "yes")
            ],
        }
    return {
        "artifact": output_root.as_posix(),
        "review_root": review_root.as_posix(),
        "work_root": work_root.as_posix(),
        "cells_total": len(rows),
        "addressable_cells": sum(1 for row in rows if row["code"]),
        "reviewed_chars": sum(1 for row in rows if row["reviewed_char"]),
        "extracted_used_cells": sum(1 for row in rows if row["used_in_extracted_records"] == "yes"),
        "raw_seen_cells": sum(1 for row in rows if row["seen_in_raw_bins"] == "yes"),
        "unknown_or_blank_used_cells": len(unknown_or_blank_used_rows(rows)),
        "watch_blocks": watch,
        "reviewed_char_counts": dict(Counter(row["reviewed_char"] for row in rows if row["reviewed_char"]).most_common()),
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# JP Glyph Usage Research v1",
        "",
        "Inputs:",
        f"- reviewed text grids: `{summary['review_root']}`",
        f"- scanned work root: `{summary['work_root']}`",
        "",
        "Outputs:",
        "- `reviewed_glyph_usage.csv`: one row per reviewed cell with extracted-record and raw-bin usage samples.",
        "- `watch_cells_usage.csv`: only the requested watch blocks.",
        "- `unknown_or_blank_used_cells.csv`: blank/unknown cells that appear in extracted records or raw bins.",
        "- `summary.json`: machine-readable summary.",
        "",
        "Notes:",
        "- ANK low cells are addressable as codes `0x0000..0x007d`.",
        "- ANK high cells are not assigned a confirmed runtime code window here, so they are reported as non-addressable.",
        "- Raw-bin hits are little-endian aligned u16 sightings and may include false positives; extracted-record hits are higher confidence.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
