from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from stage_font_probe import stage_font_probe


DEFAULT_SLOT_POOLS = (
    {"child": 1, "source": "codeJAP14x14_00_", "target_page": "local/work/tdl_DATA001_0002/0001_codeJAP14x14_00_.bin", "base": 0x0151},
    {"child": 2, "source": "codeJAP14x14_02_", "target_page": "local/work/tdl_DATA001_0002/0002_codeJAP14x14_02_.bin", "base": 0x01A2},
    {"child": 3, "source": "codeJAP14x14_04_", "target_page": "local/work/tdl_DATA001_0002/0003_codeJAP14x14_04_.bin", "base": 0x0295},
    {"child": 4, "source": "codeJAP14x14_06_", "target_page": "local/work/tdl_DATA001_0002/0004_codeJAP14x14_06_.bin", "base": 0x0337},
    {"child": 5, "source": "codeJAP14x14_08_", "target_page": "local/work/tdl_DATA001_0002/0005_codeJAP14x14_08_.bin", "base": 0x03D9},
    {"child": 6, "source": "codeJAP14x14_10_", "target_page": "local/work/tdl_DATA001_0002/0006_codeJAP14x14_10_.bin", "base": 0x042A},
    {"child": 7, "source": "codeJAP14x14_12_", "target_page": "local/work/tdl_DATA001_0002/0007_codeJAP14x14_12_.bin", "base": 0x04CC},
    {"child": 8, "source": "codeJAP14x14_14_", "target_page": "local/work/tdl_DATA001_0002/0008_codeJAP14x14_14_.bin", "base": 0x05BF},
    {"child": 9, "source": "codeJAP14x14_16_", "target_page": "local/work/tdl_DATA001_0002/0009_codeJAP14x14_16_.bin", "base": 0x0610},
    {"child": 10, "source": "codeJAP14x14_18_", "target_page": "local/work/tdl_DATA001_0002/0010_codeJAP14x14_18_.bin", "base": 0x0703},
    {"child": 11, "source": "codeJAP14x14_20_", "target_page": "local/work/tdl_DATA001_0002/0011_codeJAP14x14_20_.bin", "base": 0x0754},
)

PINNED_ASSIGNMENTS = {
    "移": {"child": 6, "source": "codeJAP14x14_10_", "target_page": "local/work/tdl_DATA001_0002/0006_codeJAP14x14_10_.bin", "base": 0x042A, "cell": 59},
    "动": {"child": 4, "source": "codeJAP14x14_06_", "target_page": "local/work/tdl_DATA001_0002/0004_codeJAP14x14_06_.bin", "base": 0x0337, "cell": 8},
    "方": {"child": 6, "source": "codeJAP14x14_10_", "target_page": "local/work/tdl_DATA001_0002/0006_codeJAP14x14_10_.bin", "base": 0x042A, "cell": 4},
    "式": {"child": 8, "source": "codeJAP14x14_14_", "target_page": "local/work/tdl_DATA001_0002/0008_codeJAP14x14_14_.bin", "base": 0x05BF, "cell": 11},
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local DATA001/0008 Simplified Chinese tutorial artifact.")
    parser.add_argument("--draft", type=Path, default=Path("local/work/chs_tutorial_draft_DATA001_0008.json"))
    parser.add_argument("--source-export", type=Path, default=Path("local/work/extract_text_DATA001_0008_seeded_fresh.json"))
    parser.add_argument("--work-root", type=Path, default=Path("local/work/tutorial_chs_full_v1"))
    parser.add_argument("--output-root", type=Path, default=Path("local/rebuilt/tutorial_chs_full_v1_extracted"))
    parser.add_argument("--font", type=Path, default=Path("C:/Windows/Fonts/simsun.ttc"))
    parser.add_argument("--font-index", type=int, default=0)
    parser.add_argument("--font-size", type=int, default=13)
    parser.add_argument("--render-mode", choices=("grayscale", "binary", "palette3"), default="palette3")
    parser.add_argument("--threshold", type=int, default=64)
    parser.add_argument("--gray-threshold", type=int, default=176)
    parser.add_argument("--stroke-radius", type=int, default=0)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    build_chs_tutorial(
        draft_path=args.draft,
        source_export_path=args.source_export,
        work_root=args.work_root,
        output_root=args.output_root,
        font_path=args.font,
        font_index=args.font_index,
        font_size=args.font_size,
        render_mode=args.render_mode,
        threshold=args.threshold,
        gray_threshold=args.gray_threshold,
        stroke_radius=args.stroke_radius,
        overwrite=args.overwrite,
    )
    print(f"staged {args.output_root}")
    return 0


def build_chs_tutorial(
    draft_path: Path,
    source_export_path: Path,
    work_root: Path,
    output_root: Path,
    font_path: Path,
    font_index: int = 0,
    font_size: int = 13,
    render_mode: str = "palette3",
    threshold: int = 64,
    gray_threshold: int = 176,
    stroke_radius: int = 0,
    overwrite: bool = False,
) -> None:
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    source_export = json.loads(source_export_path.read_text(encoding="utf-8"))
    source_by_record = {(entry["record"], entry["run"]): entry for entry in source_export["entries"]}

    translations = list(draft["entries"])
    assignments = assign_chars(translations)
    text_payload = build_text_payload(translations, source_by_record, assignments)
    font_patches = build_font_patches(
        assignments,
        font_path,
        font_index,
        font_size,
        render_mode,
        threshold,
        gray_threshold,
        stroke_radius,
        work_root / "previews",
    )

    work_root.mkdir(parents=True, exist_ok=True)
    text_json = work_root / "DATA001_0008_chs_full.json"
    assignments_csv = work_root / "runtime_glyph_assignments.csv"
    stage_json = work_root / "stage_chs_full.json"

    text_json.write_text(json.dumps(text_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_assignments_csv(assignments_csv, assignments)

    stage_config = {
        "extracted_root": "local/extracted/Rengoku 2",
        "entries_root": "local/work/mcd3_entries",
        "work_root": str(work_root / "stage"),
        "output_root": str(output_root),
        "font_patches": font_patches,
        "text_patch": {
            "entry_id": 8,
            "source_entry": "local/work/mcd3_entries/DATA001/0008_bin.bin",
            "json": str(text_json),
        },
        "overwrite": overwrite,
    }
    stage_json.write_text(json.dumps(stage_config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    stage_font_probe(stage_config)


def assign_chars(translations: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    chars = sorted(
        {
            char
            for entry in translations
            for char in str(entry["chs_translation"])
            if needs_glyph_assignment(char)
        }
    )
    assignments = {char: dict(value) for char, value in PINNED_ASSIGNMENTS.items() if char in chars}
    used_slots = {(value["child"], value["cell"]) for value in assignments.values()}
    slots = available_slots(used_slots)

    for char in chars:
        if char in assignments:
            continue
        try:
            assignments[char] = next(slots)
        except StopIteration as error:
            raise ValueError(f"not enough runtime slots for {len(chars)} CHS glyphs") from error
    return assignments


def available_slots(used_slots: set[tuple[int, int]]):
    for pool in DEFAULT_SLOT_POOLS:
        for cell in range(81):
            if (int(pool["child"]), cell) in used_slots:
                continue
            slot = dict(pool)
            slot["cell"] = cell
            yield slot


def needs_glyph_assignment(char: str) -> bool:
    if char == "\n":
        return False
    value = ord(char)
    return value < 0x20 or value > 0x7E


def build_text_payload(
    translations: list[dict[str, Any]],
    source_by_record: dict[tuple[int, int], dict[str, Any]],
    assignments: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    entries = []
    for index, translation in enumerate(translations):
        record = int(translation["record"])
        run = int(translation["run"])
        source = source_by_record[(record, run)]
        codes = encode_translation(str(translation["chs_translation"]), assignments)
        max_units = int(source["length"])
        if len(codes) > max_units:
            raise ValueError(f"record {record} run {run} needs {len(codes)} units, max is {max_units}")
        entries.append(
            {
                "id": f"chs-tutorial-{index:03d}",
                "record": record,
                "run": run,
                "entry_offset": source.get("entry_offset"),
                "kind": "glyph_codes",
                "length": max_units,
                "codes": source.get("codes", []),
                "translation": translation["chs_translation"],
                "translation_codes": [f"0x{code:04x}" for code in codes],
                "notes": "generated by tools/build_chs_tutorial.py",
            }
        )
    return {
        "format": "offset-table-runs-v1",
        "source": "local/work/mcd3_entries/DATA001/0008_bin.bin",
        "entries": entries,
    }


def encode_translation(text: str, assignments: dict[str, dict[str, Any]]) -> list[int]:
    codes = []
    for char in text:
        if char == "\n":
            codes.append(0x000A)
        elif not needs_glyph_assignment(char):
            codes.append(ord(char))
        else:
            slot = assignments[char]
            codes.append(int(slot["base"]) + int(slot["cell"]))
    return codes


def build_font_patches(
    assignments: dict[str, dict[str, Any]],
    font_path: Path,
    font_index: int,
    font_size: int,
    render_mode: str,
    threshold: int,
    gray_threshold: int,
    stroke_radius: int,
    preview_dir: Path,
) -> list[dict[str, Any]]:
    patches = []
    for char, slot in sorted(assignments.items(), key=lambda item: (item[1]["child"], item[1]["cell"], item[0])):
        patches.append(
            {
                "mode": "render",
                "target_page": slot["target_page"],
                "target_child": slot["child"],
                "target_cell": slot["cell"],
                "char": char,
                "font": str(font_path),
                "font_index": font_index,
                "font_size": font_size,
                "render_mode": render_mode,
                "threshold": threshold,
                "gray_threshold": gray_threshold,
                "stroke_radius": stroke_radius,
                "preview": str(preview_dir / f"child{slot['child']}_cell{slot['cell']:02d}_{ord(char):04x}.png"),
            }
        )
    return patches


def write_assignments_csv(path: Path, assignments: dict[str, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["char", "code", "archive", "entry", "child", "source", "cell", "runtime_texture", "base", "notes"],
        )
        writer.writeheader()
        for char, slot in sorted(assignments.items(), key=lambda item: (item[1]["child"], item[1]["cell"], item[0])):
            code = int(slot["base"]) + int(slot["cell"])
            writer.writerow(
                {
                    "char": char,
                    "code": f"0x{code:04x}",
                    "archive": "DATA001",
                    "entry": "0002",
                    "child": slot["child"],
                    "source": slot["source"],
                    "cell": slot["cell"],
                    "runtime_texture": runtime_texture_for_child(int(slot["child"])),
                    "base": f"0x{int(slot['base']):04x}",
                    "notes": "generated CHS tutorial assignment",
                }
            )


def runtime_texture_for_child(child: int) -> str:
    return f"0x{0x040DC200 + child * 0x2100:08x}"


if __name__ == "__main__":
    raise SystemExit(main())
