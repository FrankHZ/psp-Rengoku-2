from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


DEFAULT_SOURCE_ROOT = Path("local/work/jp_glyph_clear_pages_v1")
DEFAULT_OUTPUT_ROOT = Path("local/work/jp_glyph_table_v2")


GEOMETRY = {
    "codeANK9x14_00_0": {"grid_cols": 14, "grid_rows": 9, "cell_w": 9, "cell_h": 14, "kind": "ANK"},
    "codeJAP14x14_00_": {"grid_cols": 9, "grid_rows": 9, "cell_w": 14, "cell_h": 14, "kind": "JAP"},
    "codeJAP14x14_02_": {"grid_cols": 9, "grid_rows": 9, "cell_w": 14, "cell_h": 14, "kind": "JAP"},
    "codeJAP14x14_04_": {"grid_cols": 9, "grid_rows": 9, "cell_w": 14, "cell_h": 14, "kind": "JAP"},
    "codeJAP14x14_06_": {"grid_cols": 9, "grid_rows": 9, "cell_w": 14, "cell_h": 14, "kind": "JAP"},
    "codeJAP14x14_08_": {"grid_cols": 9, "grid_rows": 9, "cell_w": 14, "cell_h": 14, "kind": "JAP"},
    "codeJAP14x14_10_": {"grid_cols": 9, "grid_rows": 9, "cell_w": 14, "cell_h": 14, "kind": "JAP"},
    "codeJAP14x14_12_": {"grid_cols": 9, "grid_rows": 9, "cell_w": 14, "cell_h": 14, "kind": "JAP"},
    "codeJAP14x14_14_": {"grid_cols": 9, "grid_rows": 9, "cell_w": 14, "cell_h": 14, "kind": "JAP"},
    "codeJAP14x14_16_": {"grid_cols": 9, "grid_rows": 9, "cell_w": 14, "cell_h": 14, "kind": "JAP"},
    "codeJAP14x14_18_": {"grid_cols": 9, "grid_rows": 9, "cell_w": 14, "cell_h": 14, "kind": "JAP"},
    "codeJAP14x14_20_": {"grid_cols": 9, "grid_rows": 9, "cell_w": 14, "cell_h": 14, "kind": "JAP"},
}

REVIEW_PRIORITY = {
    "needs_alignment_review": 1,
    "ocr_prefix_candidate": 2,
    "inferred_sequence": 3,
    "blank_or_missing_ocr": 4,
    "reviewed_ocr_full_block": 5,
    "reviewed_ocr_partial_block": 5,
    "confirmed_seed": 6,
}

FIELDNAMES = [
    "code",
    "final_char",
    "final_status",
    "reviewer_char",
    "reviewer_status",
    "reviewer_notes",
    "review_priority",
    "child",
    "source",
    "page_kind",
    "layer",
    "base",
    "cell",
    "row",
    "col",
    "grid_cols",
    "grid_rows",
    "cell_w",
    "cell_h",
    "block",
    "block_type",
    "ocr_char",
    "seed_char",
    "seed_status",
    "seed_match",
    "review_source",
    "review_notes",
    "page",
    "cell_png",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Build jp_glyph_table_v2 and human-review CSVs.")
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if args.output_root.exists() and not args.overwrite:
        raise FileExistsError(f"{args.output_root} already exists; pass --overwrite")

    build_v2(args.source_root, args.output_root)
    print(f"wrote {args.output_root}")
    return 0


def build_v2(source_root: Path, output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    human_dir = output_root / "human_review"
    page_dir = human_dir / "pages"
    text_grid_dir = human_dir / "text_grids"
    sheet_dir = output_root / "contact_sheets"
    human_dir.mkdir(parents=True, exist_ok=True)
    page_dir.mkdir(parents=True, exist_ok=True)
    text_grid_dir.mkdir(parents=True, exist_ok=True)
    sheet_dir.mkdir(parents=True, exist_ok=True)

    rows = read_csv(source_root / "ocr_reviewed_map.csv")
    v2_rows = [make_v2_row(row) for row in rows]
    v2_rows.sort(key=sort_key)

    write_csv(output_root / "jp_glyph_table_v2.csv", v2_rows, FIELDNAMES)
    write_json(output_root / "jp_glyph_table_v2.json", v2_rows)

    human_fields = ["cell", "row", "col", "code", "current", "status", "ocr", "seed", "reviewer_char", "reviewer_note"]
    write_csv(human_dir / "all_for_human_review.csv", v2_rows, human_fields)
    write_csv(human_dir / "01_needs_alignment_review.csv", filter_status(v2_rows, {"needs_alignment_review"}), human_fields)
    write_csv(human_dir / "02_ocr_prefix_candidates.csv", filter_status(v2_rows, {"ocr_prefix_candidate"}), human_fields)
    write_csv(human_dir / "03_inferred_sequences.csv", filter_status(v2_rows, {"inferred_sequence"}), human_fields)
    write_csv(human_dir / "04_blank_or_missing_ocr.csv", filter_status(v2_rows, {"blank_or_missing_ocr"}), human_fields)
    write_csv(
        human_dir / "90_safe_reference_no_edit_needed.csv",
        filter_status(v2_rows, {"confirmed_seed", "reviewed_ocr_full_block", "reviewed_ocr_partial_block"}),
        human_fields,
    )

    for key, page_rows in group_pages(v2_rows).items():
        block, child, source, layer = key
        safe_source = source.replace("/", "_")
        filename = f"block{int(block):02d}_child{int(child):02d}_{safe_source}_{layer}.csv"
        write_csv(page_dir / filename, page_rows, human_fields)
        text_name = f"block{int(block):02d}_child{int(child):02d}_{safe_source}_{layer}.txt"
        write_text_grid(text_grid_dir / text_name, page_rows)
        sheet_name = f"block{int(block):02d}_child{int(child):02d}_{safe_source}_{layer}.png"
        write_contact_sheet(sheet_dir / sheet_name, page_rows, source_root)

    summary = summarize(v2_rows, source_root, output_root)
    write_json(output_root / "summary.json", summary)
    write_readme(output_root / "README.md", summary)


def make_v2_row(row: dict[str, str]) -> dict[str, Any]:
    geometry = GEOMETRY.get(row["source"], {"grid_cols": "", "grid_rows": "", "cell_w": "", "cell_h": "", "kind": ""})
    final_status = row["review_status"]
    final_char = row["reviewed_char"]
    return {
        "code": row["code"],
        "final_char": final_char,
        "final_status": final_status,
        "reviewer_char": final_char if final_status in {"needs_alignment_review", "ocr_prefix_candidate", "inferred_sequence"} else "",
        "reviewer_note": "",
        "current": final_char,
        "status": final_status,
        "ocr": row["ocr_char"],
        "seed": row["seed_char"],
        "reviewer_status": "",
        "reviewer_notes": "",
        "review_priority": REVIEW_PRIORITY.get(final_status, 9),
        "child": row["child"],
        "source": row["source"],
        "page_kind": geometry["kind"],
        "layer": row["layer"],
        "base": row["base"],
        "cell": row["cell"],
        "row": row["row"],
        "col": row["col"],
        "grid_cols": geometry["grid_cols"],
        "grid_rows": geometry["grid_rows"],
        "cell_w": geometry["cell_w"],
        "cell_h": geometry["cell_h"],
        "block": row["block"],
        "block_type": row["block_type"],
        "ocr_char": row["ocr_char"],
        "seed_char": row["seed_char"],
        "seed_status": row["seed_status"],
        "seed_match": row["seed_match"],
        "review_source": row["review_source"],
        "review_notes": row["review_notes"],
        "page": row["page"],
        "cell_png": row["cell_png"],
    }


def filter_status(rows: list[dict[str, Any]], statuses: set[str]) -> list[dict[str, Any]]:
    return [row for row in rows if row["final_status"] in statuses]


def group_pages(rows: list[dict[str, Any]]) -> dict[tuple[str, str, str, str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((str(row["block"]), str(row["child"]), str(row["source"]), str(row["layer"])), []).append(row)
    return dict(sorted(grouped.items(), key=lambda item: (int(item[0][0]), int(item[0][1]), item[0][3])))


def summarize(rows: list[dict[str, Any]], source_root: Path, output_root: Path) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    kind_counts: dict[str, int] = {}
    for row in rows:
        status_counts[row["final_status"]] = status_counts.get(row["final_status"], 0) + 1
        kind_counts[row["page_kind"]] = kind_counts.get(row["page_kind"], 0) + 1
    coded = [row for row in rows if row["code"]]
    filled = [row for row in coded if row["final_char"]]
    return {
        "artifact": str(output_root),
        "source_root": str(source_root),
        "rows_total": len(rows),
        "coded_rows": len(coded),
        "coded_rows_with_final_char": len(filled),
        "status_counts": dict(sorted(status_counts.items())),
        "page_kind_counts": dict(sorted(kind_counts.items())),
        "geometry": GEOMETRY,
        "human_review_dir": str(output_root / "human_review"),
        "contact_sheets_dir": str(output_root / "contact_sheets"),
        "notes": [
            "ANK page is 14 columns x 9 rows with 9x14 cells; JP pages are 9x9 with 14x14 cells.",
            "Use contact_sheets PNGs as the visual source.",
            "Edit reviewer_char in human_review CSVs; current is the machine candidate.",
        ],
    }


def sort_key(row: dict[str, Any]) -> tuple[int, int, int]:
    return (int(row["block"]), int(row["child"]), int(row["cell"]))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_text_grid(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    first = rows[0]
    cols = int(first["grid_cols"])
    grid_rows = int(first["grid_rows"])
    cells = [["□" for _ in range(cols)] for _ in range(grid_rows)]
    for row in rows:
        candidate = str(row.get("current") or row.get("ocr") or row.get("seed") or "□")
        cells[int(row["row"])][int(row["col"])] = candidate[0] if candidate else "□"
    lines = ["".join(line) for line in cells]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_contact_sheet(path: Path, rows: list[dict[str, Any]], source_root: Path) -> None:
    if not rows:
        return
    first = rows[0]
    cols = int(first["grid_cols"])
    cell_w = int(first["cell_w"])
    cell_h = int(first["cell_h"])
    scale = 5 if cell_w == 14 else 6
    tile_w = max(cell_w * scale + 22, 82)
    tile_h = cell_h * scale + 54
    sheet_rows = (len(rows) + cols - 1) // cols
    image = Image.new("RGB", (cols * tile_w, sheet_rows * tile_h), "white")
    draw = ImageDraw.Draw(image)
    try:
        small = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", size=11)
        glyph_font = ImageFont.truetype("C:/Windows/Fonts/msgothic.ttc", size=18)
    except OSError:
        small = ImageFont.load_default()
        glyph_font = ImageFont.load_default()

    for row in rows:
        cell = int(row["cell"])
        x = int(row["col"]) * tile_w
        y = int(row["row"]) * tile_h
        draw.rectangle((x, y, x + tile_w - 1, y + tile_h - 1), outline=(190, 190, 190))
        glyph = read_2bpp_cell(source_root, row)
        if glyph is None:
            cell_path = source_root / str(row["cell_png"])
            if cell_path.exists():
                glyph = Image.open(cell_path).convert("L")
        if glyph is not None:
            glyph = glyph.resize((cell_w * scale, cell_h * scale), Image.Resampling.NEAREST).convert("RGB")
            image.paste(glyph, (x + (tile_w - glyph.width) // 2, y + 16))
        draw.text((x + 2, y + 2), f"{cell:03d} {row['code']}", fill=(0, 0, 0), font=small)
        current = str(row.get("current") or "")
        status = short_status(str(row.get("status") or ""))
        color = (0, 100, 0) if row.get("status") in {"confirmed_seed", "reviewed_ocr_full_block", "reviewed_ocr_partial_block"} else (160, 80, 0)
        draw.text((x + 2, y + cell_h * scale + 20), current, fill=color, font=glyph_font)
        draw.text((x + 2, y + cell_h * scale + 42), status, fill=(80, 80, 80), font=small)
    image.save(path)


def read_2bpp_cell(source_root: Path, row: dict[str, Any]) -> Image.Image | None:
    page = source_root / "original_pages_2bpp" / make_2bpp_page_name(row)
    if not page.exists():
        return None
    cell_w = int(row["cell_w"])
    cell_h = int(row["cell_h"])
    col = int(row["col"])
    row_index = int(row["row"])
    with Image.open(page) as image:
        gray = image.convert("L")
        return gray.crop((col * cell_w, row_index * cell_h, (col + 1) * cell_w, (row_index + 1) * cell_h))


def make_2bpp_page_name(row: dict[str, Any]) -> str:
    return f"child{int(row['child']):02d}_{row['source']}_{row['layer']}_2bpp.png"


def short_status(status: str) -> str:
    return {
        "needs_alignment_review": "align",
        "ocr_prefix_candidate": "prefix",
        "inferred_sequence": "infer",
        "blank_or_missing_ocr": "blank",
        "reviewed_ocr_full_block": "ocr-ok",
        "reviewed_ocr_partial_block": "ocr-part",
        "confirmed_seed": "seed",
    }.get(status, status[:10])


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_readme(path: Path, summary: dict[str, Any]) -> None:
    counts = summary["status_counts"]
    lines = [
        "# JP Glyph Table v2",
        "",
        "Reviewer-oriented glyph table built from confirmed seeds, Google OCR, and the reviewed OCR status layer.",
        "",
        "## Geometry Warning",
        "",
        "- `codeANK9x14_00_0` is `14 x 9` cells, each `9x14` pixels.",
        "- `codeJAP14x14_*` pages are `9 x 9` cells, each `14x14` pixels.",
        "- Do not reshape the ANK page as a 9x9 page.",
        "",
        "## Main Files",
        "",
        "- `jp_glyph_table_v2.csv`: machine map with current candidates and review metadata.",
        "- `jp_glyph_table_v2.json`: JSON mirror.",
        "- `contact_sheets/`: one PNG per OCR block/page for human review.",
        "- `human_review/pages/`: one short editable CSV per OCR block/page.",
        "- `human_review/text_grids/`: one plain text grid per OCR block/page; JP pages are 9x9, ANK pages are 14x9.",
        "- `human_review/01_needs_alignment_review.csv`: highest-priority short CSV.",
        "- `human_review/02_ocr_prefix_candidates.csv`: useful candidates that still need checking.",
        "- `human_review/90_safe_reference_no_edit_needed.csv`: reference rows.",
        "",
        "## Reviewer Instructions",
        "",
        "Use `contact_sheets/` as the visual source. Edit only `reviewer_char` and optional `reviewer_note` in the short CSVs.",
        "The contact sheets use `original_pages_2bpp/` as their default glyph source, preserving the low/high 2bpp layer values.",
        "Rows with `needs_alignment_review` should be corrected from the contact sheet, not from raw OCR order.",
        "",
        "## Counts",
        "",
    ]
    for status, count in counts.items():
        lines.append(f"- `{status}`: {count}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
