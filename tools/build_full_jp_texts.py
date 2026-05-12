from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from glyph_map import decode_glyph_values
from research_jp_glyph_usage import read_reviewed_cells


DEFAULT_INVENTORY = Path("local/work/global_text_inventory/global_table_inventory.csv")
DEFAULT_REVIEW_ROOT = Path("local/ocr_reviewed")
DEFAULT_OUTPUT_ROOT = Path("local/work/full_jp_text_decode_v1")


def main() -> int:
    parser = argparse.ArgumentParser(description="Decode all known JP text extracts using the reviewed JP glyph table.")
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--review-root", type=Path, default=DEFAULT_REVIEW_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--sample-limit", type=int, default=8)
    args = parser.parse_args()

    output_root = args.output_root
    output_root.mkdir(parents=True, exist_ok=True)

    glyph_rows, glyphs = build_reviewed_glyph_map(args.review_root)
    write_csv(output_root / "reviewed_jp_glyph_map.csv", glyph_rows)

    table_rows = read_inventory(args.inventory)
    decoded_rows: list[dict[str, Any]] = []
    for table in table_rows:
        extract_path = Path(table["jp_extract"])
        if not extract_path.exists():
            continue
        decoded_rows.extend(decode_extract(table, extract_path, glyphs))

    write_csv(output_root / "full_jp_texts.csv", csv_ready_rows(decoded_rows))
    write_json(output_root / "full_jp_texts.json", {"entries": decoded_rows})
    samples = build_samples(decoded_rows, args.sample_limit)
    write_json(output_root / "samples.json", samples)
    write_samples_text(output_root / "samples.txt", samples)
    summary = summarize(decoded_rows, glyph_rows, args)
    write_json(output_root / "summary.json", summary)
    write_readme(output_root / "README.md", summary)
    print(json.dumps(summary, ensure_ascii=True, indent=2))
    return 0


def build_reviewed_glyph_map(review_root: Path) -> tuple[list[dict[str, Any]], dict[int, str]]:
    glyph_rows: list[dict[str, Any]] = []
    glyphs: dict[int, str] = {}
    for row in read_reviewed_cells(review_root):
        code = row.get("code_int")
        char = row.get("reviewed_char") or ""
        if code is None or not char:
            continue
        code_int = int(code)
        glyphs[code_int] = char
        glyph_rows.append(
            {
                "code": f"0x{code_int:04x}",
                "char": char,
                "page": row["page"],
                "cell": row["cell"],
                "row": row["row"],
                "col": row["col"],
            }
        )
    return glyph_rows, glyphs


def read_inventory(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return [row for row in csv.DictReader(file) if row.get("jp_extract")]


def decode_extract(table: dict[str, str], path: Path, glyphs: dict[int, str]) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        return []
    rows: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        codes = parse_codes(entry.get("codes"))
        kind = str(entry.get("kind") or "")
        if codes:
            text, known = decode_glyph_values(codes, glyphs)
            unknown = sum(1 for code in codes if is_unknown_code(code, glyphs))
            length = len(codes)
        else:
            text = str(entry.get("text") or "")
            known = len(text)
            unknown = 0
            length = int(entry.get("length") or len(text))
        record = entry.get("record", "")
        run = entry.get("run", "")
        rows.append(
            {
                "table": table["jp_table"],
                "role": table.get("role", ""),
                "source_extract": path.as_posix(),
                "record": record,
                "run": run,
                "record_path": f"{table['jp_table']}#{int(record):04d}:{run}" if str(record).isdigit() else "",
                "kind": kind,
                "length": length,
                "decoded_known": known,
                "unknown_count": unknown,
                "coverage": known / length if length else 1.0,
                "text": text,
                "codes": [f"0x{code:04x}" for code in codes],
            }
        )
    return rows


def parse_codes(raw: Any) -> list[int]:
    if not isinstance(raw, list):
        return []
    codes: list[int] = []
    for item in raw:
        if isinstance(item, int):
            codes.append(item)
        elif isinstance(item, str):
            try:
                codes.append(int(item, 16 if item.lower().startswith("0x") else 10))
            except ValueError:
                pass
    return codes


def is_unknown_code(code: int, glyphs: dict[int, str]) -> bool:
    if code in glyphs:
        return False
    if code in {0, 0x000A, 0x000C, 0x0010, 0x0014}:
        return False
    if 0x20 <= code < 0x7F:
        return False
    return True


def build_samples(rows: list[dict[str, Any]], limit: int) -> dict[str, Any]:
    by_table: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_table.setdefault(str(row["table"]), []).append(row)

    samples: dict[str, Any] = {"tables": {}}
    for table, table_rows in sorted(by_table.items()):
        good = [row for row in table_rows if row["length"] >= 4 and row["coverage"] >= 0.95 and row["text"]]
        partial = [row for row in table_rows if row["length"] >= 4 and 0 < row["coverage"] < 0.95 and row["text"]]
        long_rows = [row for row in good if row["length"] >= 16]
        samples["tables"][table] = {
            "high_coverage": sample_evenly(good, limit),
            "long_high_coverage": sample_evenly(long_rows, max(3, limit // 2)),
            "partial_coverage": sample_evenly(partial, max(3, limit // 2)),
        }
    return samples


def sample_evenly(rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    if len(rows) <= limit:
        chosen = rows
    else:
        step = (len(rows) - 1) / max(1, limit - 1)
        chosen = [rows[round(index * step)] for index in range(limit)]
    fields = ("record_path", "kind", "length", "decoded_known", "unknown_count", "coverage", "text")
    return [{field: row[field] for field in fields} for row in chosen]


def summarize(rows: list[dict[str, Any]], glyph_rows: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    by_table: dict[str, dict[str, Any]] = {}
    for row in rows:
        stats = by_table.setdefault(
            str(row["table"]),
            {
                "rows": 0,
                "glyph_or_text_units": 0,
                "decoded_known": 0,
                "unknown_count": 0,
                "full_coverage_rows": 0,
                "partial_rows": 0,
            },
        )
        stats["rows"] += 1
        stats["glyph_or_text_units"] += int(row["length"])
        stats["decoded_known"] += int(row["decoded_known"])
        stats["unknown_count"] += int(row["unknown_count"])
        if float(row["coverage"]) >= 1.0:
            stats["full_coverage_rows"] += 1
        elif int(row["decoded_known"]) > 0:
            stats["partial_rows"] += 1
    for stats in by_table.values():
        units = stats["glyph_or_text_units"]
        stats["coverage"] = stats["decoded_known"] / units if units else 1.0
    total_units = sum(int(row["length"]) for row in rows)
    total_known = sum(int(row["decoded_known"]) for row in rows)
    return {
        "artifact": args.output_root.as_posix(),
        "review_root": args.review_root.as_posix(),
        "inventory": args.inventory.as_posix(),
        "reviewed_glyphs": len(glyph_rows),
        "rows": len(rows),
        "glyph_or_text_units": total_units,
        "decoded_known": total_known,
        "unknown_count": sum(int(row["unknown_count"]) for row in rows),
        "coverage": total_known / total_units if total_units else 1.0,
        "tables": by_table,
    }


def csv_ready_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ready = []
    for row in rows:
        copy = dict(row)
        copy["coverage"] = f"{float(copy['coverage']):.4f}"
        copy["codes"] = " ".join(copy["codes"])
        ready.append(copy)
    return ready


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_samples_text(path: Path, samples: dict[str, Any]) -> None:
    lines: list[str] = ["# Full JP Text Decode Samples", ""]
    for table, groups in samples["tables"].items():
        lines.extend([f"## {table}", ""])
        for group, rows in groups.items():
            lines.extend([f"### {group}", ""])
            if not rows:
                lines.extend(["(none)", ""])
                continue
            for row in rows:
                lines.append(
                    f"- {row['record_path']} cov={row['coverage']:.2%} "
                    f"known={row['decoded_known']}/{row['length']}: {row['text']}"
                )
            lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_readme(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Full JP Text Decode",
        "",
        "Fresh decode of known Japanese text extracts using `local/ocr_reviewed/`.",
        "",
        "- `reviewed_jp_glyph_map.csv`: generated `code,char` glyph table.",
        "- `full_jp_texts.csv`: flat decoded rows for review/filtering.",
        "- `full_jp_texts.json`: same data with code arrays preserved.",
        "- `samples.txt`: stratified samples by table and coverage.",
        "",
        f"Reviewed glyphs: {summary['reviewed_glyphs']}",
        f"Rows: {summary['rows']}",
        f"Overall coverage: {summary['coverage']:.2%}",
        f"Unknown code units: {summary['unknown_count']}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
