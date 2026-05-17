from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import re
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
BITPLANE_SLOT_POOLS = (
    {"child": 1, "source": "codeJAP14x14_00_", "target_page": "local/work/tdl_DATA001_0002/0001_codeJAP14x14_00_.bin", "base": 0x0100, "layer": "low"},
    {"child": 1, "source": "codeJAP14x14_00_", "target_page": "local/work/tdl_DATA001_0002/0001_codeJAP14x14_00_.bin", "base": 0x0151, "layer": "high"},
    {"child": 2, "source": "codeJAP14x14_02_", "target_page": "local/work/tdl_DATA001_0002/0002_codeJAP14x14_02_.bin", "base": 0x01A2, "layer": "low"},
    {"child": 2, "source": "codeJAP14x14_02_", "target_page": "local/work/tdl_DATA001_0002/0002_codeJAP14x14_02_.bin", "base": 0x01F3, "layer": "high"},
    {"child": 3, "source": "codeJAP14x14_04_", "target_page": "local/work/tdl_DATA001_0002/0003_codeJAP14x14_04_.bin", "base": 0x0244, "layer": "low"},
    {"child": 3, "source": "codeJAP14x14_04_", "target_page": "local/work/tdl_DATA001_0002/0003_codeJAP14x14_04_.bin", "base": 0x0295, "layer": "high"},
    {"child": 4, "source": "codeJAP14x14_06_", "target_page": "local/work/tdl_DATA001_0002/0004_codeJAP14x14_06_.bin", "base": 0x02E6, "layer": "low"},
    {"child": 4, "source": "codeJAP14x14_06_", "target_page": "local/work/tdl_DATA001_0002/0004_codeJAP14x14_06_.bin", "base": 0x0337, "layer": "high"},
    {"child": 5, "source": "codeJAP14x14_08_", "target_page": "local/work/tdl_DATA001_0002/0005_codeJAP14x14_08_.bin", "base": 0x0388, "layer": "low"},
    {"child": 5, "source": "codeJAP14x14_08_", "target_page": "local/work/tdl_DATA001_0002/0005_codeJAP14x14_08_.bin", "base": 0x03D9, "layer": "high"},
    {"child": 6, "source": "codeJAP14x14_10_", "target_page": "local/work/tdl_DATA001_0002/0006_codeJAP14x14_10_.bin", "base": 0x042A, "layer": "low"},
    {"child": 6, "source": "codeJAP14x14_10_", "target_page": "local/work/tdl_DATA001_0002/0006_codeJAP14x14_10_.bin", "base": 0x047B, "layer": "high"},
    {"child": 7, "source": "codeJAP14x14_12_", "target_page": "local/work/tdl_DATA001_0002/0007_codeJAP14x14_12_.bin", "base": 0x04CC, "layer": "low"},
    {"child": 7, "source": "codeJAP14x14_12_", "target_page": "local/work/tdl_DATA001_0002/0007_codeJAP14x14_12_.bin", "base": 0x051D, "layer": "high"},
    {"child": 8, "source": "codeJAP14x14_14_", "target_page": "local/work/tdl_DATA001_0002/0008_codeJAP14x14_14_.bin", "base": 0x056E, "layer": "low"},
    {"child": 8, "source": "codeJAP14x14_14_", "target_page": "local/work/tdl_DATA001_0002/0008_codeJAP14x14_14_.bin", "base": 0x05BF, "layer": "high"},
    {"child": 9, "source": "codeJAP14x14_16_", "target_page": "local/work/tdl_DATA001_0002/0009_codeJAP14x14_16_.bin", "base": 0x0610, "layer": "low"},
    {"child": 9, "source": "codeJAP14x14_16_", "target_page": "local/work/tdl_DATA001_0002/0009_codeJAP14x14_16_.bin", "base": 0x0661, "layer": "high"},
    {"child": 10, "source": "codeJAP14x14_18_", "target_page": "local/work/tdl_DATA001_0002/0010_codeJAP14x14_18_.bin", "base": 0x06B2, "layer": "low"},
    {"child": 10, "source": "codeJAP14x14_18_", "target_page": "local/work/tdl_DATA001_0002/0010_codeJAP14x14_18_.bin", "base": 0x0703, "layer": "high"},
    {"child": 11, "source": "codeJAP14x14_20_", "target_page": "local/work/tdl_DATA001_0002/0011_codeJAP14x14_20_.bin", "base": 0x0754, "layer": "low"},
    {"child": 11, "source": "codeJAP14x14_20_", "target_page": "local/work/tdl_DATA001_0002/0011_codeJAP14x14_20_.bin", "base": 0x07A5, "layer": "high"},
)
RESERVED_SOURCE_ICON_CELLS = {
    (1, 9),   # 0x015a / confirm-style key icon
    (1, 14),  # 0x015f / square-style attack key icon
    (1, 16),  # 0x0161 / triangle-style attack key icon
    (1, 26),  # 0x011a via alternate child-1 code window
    (1, 62),  # 0x013e via alternate child-1 code window
    (2, 6),   # 0x01a8 / L button icon
    (2, 12),  # 0x01ae / R button icon
}

PINNED_ASSIGNMENTS = {
    "移": {"child": 6, "source": "codeJAP14x14_10_", "target_page": "local/work/tdl_DATA001_0002/0006_codeJAP14x14_10_.bin", "base": 0x042A, "cell": 59},
    "动": {"child": 4, "source": "codeJAP14x14_06_", "target_page": "local/work/tdl_DATA001_0002/0004_codeJAP14x14_06_.bin", "base": 0x0337, "cell": 8},
    "方": {"child": 6, "source": "codeJAP14x14_10_", "target_page": "local/work/tdl_DATA001_0002/0006_codeJAP14x14_10_.bin", "base": 0x042A, "cell": 4},
    "式": {"child": 8, "source": "codeJAP14x14_14_", "target_page": "local/work/tdl_DATA001_0002/0008_codeJAP14x14_14_.bin", "base": 0x05BF, "cell": 11},
}
INLINE_CODE_RE = re.compile(r"<(?:icon|code):0x?([0-9a-fA-F]{1,4})>")
PRESERVED_SOURCE_CODES = {
    "、": 0x0101,
    "。": 0x0102,
    "，": 0x0103,
    "．": 0x0104,
    "·": 0x0105,  # Reuse the original JP middle-dot glyph for CHS bullet dots.
    "・": 0x0105,
    "：": 0x0106,
    "；": 0x0107,
    "？": 0x0108,
    "！": 0x0109,
    "＿": 0x0111,
    "々": 0x0118,
    "０": 0x0193,
    "１": 0x0194,
    "２": 0x0195,
    "３": 0x0196,
    "４": 0x0197,
    "５": 0x0198,
    "６": 0x0199,
    "７": 0x019A,
    "８": 0x019B,
    "９": 0x019C,
    "Ａ": 0x019D,
    "Ｂ": 0x019E,
    "Ｃ": 0x019F,
    "Ｄ": 0x01A0,
    "Ｅ": 0x01A1,
    "Ｆ": 0x01A2,
    "Ｇ": 0x01A3,
    "Ｈ": 0x01A4,
    "Ｉ": 0x01A5,
    "Ｊ": 0x01A6,
    "Ｋ": 0x01A7,
    "Ｌ": 0x01A8,
    "Ｍ": 0x01A9,
    "Ｎ": 0x01AA,
    "Ｏ": 0x01AB,
    "Ｐ": 0x01AC,
    "Ｑ": 0x01AD,
    "Ｒ": 0x01AE,
    "Ｓ": 0x01AF,
    "Ｔ": 0x01B0,
    "Ｕ": 0x01B1,
    "Ｖ": 0x01B2,
    "Ｗ": 0x01B3,
    "Ｘ": 0x01B4,
    "Ｙ": 0x01B5,
    "Ｚ": 0x01B6,
    "ａ": 0x01B7,
    "ｂ": 0x01B8,
    "ｃ": 0x01B9,
    "ｄ": 0x01BA,
    "ｅ": 0x01BB,
    "ｆ": 0x01BC,
    "ｇ": 0x01BD,
    "ｈ": 0x01BE,
    "ｉ": 0x01BF,
    "ｊ": 0x01C0,
    "ｋ": 0x01C1,
    "ｌ": 0x01C2,
    "ｍ": 0x01C3,
    "ｎ": 0x01C4,
    "ｏ": 0x01C5,
    "ｐ": 0x01C6,
    "ｑ": 0x01C7,
    "ｒ": 0x01C8,
    "ｓ": 0x01C9,
    "ｔ": 0x01CA,
    "ｕ": 0x01CB,
    "ｖ": 0x01CC,
    "ｗ": 0x01CD,
    "ｘ": 0x01CE,
    "ｙ": 0x01CF,
    "ｚ": 0x01D0,
    "〇": 0x011A,
    "○": 0x015A,
    "☆": 0x0158,
    "★": 0x0159,
    "ー": 0x011B,
    "―": 0x011C,
    "‐": 0x011D,
    "／": 0x011E,
    "＼": 0x011F,
    "〜": 0x0120,
    "｜": 0x0122,
    "…": 0x0123,
    "‥": 0x0124,
    "‘": 0x0125,
    "’": 0x0126,
    "“": 0x0127,
    "”": 0x0128,
    "（": 0x0129,
    "）": 0x012A,
    "［": 0x012D,
    "］": 0x012E,
    "｛": 0x012F,
    "｝": 0x0130,
    "〈": 0x0131,
    "〉": 0x0132,
    "《": 0x0133,
    "》": 0x0134,
    "「": 0x0135,
    "」": 0x0136,
    "『": 0x0137,
    "』": 0x0138,
    "【": 0x0139,
    "】": 0x013A,
    "＋": 0x013B,
    "−": 0x013C,
    "±": 0x013D,
    "×": 0x013E,
    "÷": 0x013F,
    "＝": 0x0140,
    "≠": 0x0141,
    "＜": 0x0142,
    "＞": 0x0143,
    "≦": 0x0144,
    "≧": 0x0145,
    "∞": 0x0146,
    "∴": 0x0147,
    "♂": 0x0148,
    "♀": 0x0149,
    "°": 0x014A,
    "℃": 0x014D,
    "￥": 0x014E,
    "□": 0x015F,
    "△": 0x0161,
    "→": 0x0167,
    "←": 0x0168,
    "↑": 0x0169,
    "↓": 0x016A,
    "Ω": 0x02AC,
    "α": 0x02AD,
    "β": 0x02AE,
    "γ": 0x02AF,
    "™": 0x027A,
    "€": 0x0282,
    "Ⅰ": 0x0326,
    "Ⅱ": 0x0327,
    "Ⅲ": 0x0328,
    "Ⅳ": 0x0329,
    "Ⅴ": 0x032A,
    "Ⅵ": 0x032B,
    "Ⅶ": 0x032C,
    "Ⅷ": 0x032D,
    "Ⅸ": 0x032E,
    "Ⅹ": 0x032F,
    "㎜": 0x03B6,
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
    return assign_chars_from_pools(translations, DEFAULT_SLOT_POOLS, use_bitplanes=False)


def assign_chars_bitplane(translations: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return assign_chars_from_pools(translations, BITPLANE_SLOT_POOLS, use_bitplanes=True)


def assign_chars_from_pools(
    translations: list[dict[str, Any]],
    slot_pools: tuple[dict[str, Any], ...],
    use_bitplanes: bool,
) -> dict[str, dict[str, Any]]:
    chars = sorted(
        {
            char
            for entry in translations
            for char in visible_translation_chars(str(entry["chs_translation"]))
            if needs_glyph_assignment(char)
        }
    )
    assignments = {
        char: normalize_assignment_for_pools(value, slot_pools)
        for char, value in PINNED_ASSIGNMENTS.items()
        if char in chars
    }
    reserved_logical_slots = preserved_source_logical_slots(slot_pools)
    if use_bitplanes:
        used_slots = {(value["child"], value["cell"], value.get("layer", "low")) for value in assignments.values()}
        slots = available_bitplane_slots(used_slots, reserved_logical_slots, RESERVED_SOURCE_ICON_CELLS, slot_pools)
    else:
        used_slots = (
            RESERVED_SOURCE_ICON_CELLS
            | {(child, cell) for child, cell, _layer in reserved_logical_slots}
            | {(value["child"], value["cell"]) for value in assignments.values()}
        )
        slots = available_slots(used_slots, slot_pools)

    for char in chars:
        if char in assignments:
            continue
        try:
            assignments[char] = next(slots)
        except StopIteration as error:
            raise ValueError(f"not enough runtime slots for {len(chars)} CHS glyphs") from error
    return assignments


def normalize_assignment_for_pools(slot: dict[str, Any], slot_pools: tuple[dict[str, Any], ...]) -> dict[str, Any]:
    for pool in slot_pools:
        if int(pool["child"]) == int(slot["child"]) and int(pool["base"]) == int(slot["base"]):
            normalized = dict(pool)
            normalized["cell"] = int(slot["cell"])
            return normalized
    return dict(slot)


def available_slots(used_slots: set[tuple[int, int]], slot_pools: tuple[dict[str, Any], ...] = DEFAULT_SLOT_POOLS):
    for pool in slot_pools:
        for cell in range(81):
            if (int(pool["child"]), cell) in used_slots:
                continue
            slot = dict(pool)
            slot["cell"] = cell
            yield slot


def available_bitplane_slots(
    used_slots: set[tuple[int, int, str]],
    reserved_logical_slots: set[tuple[int, int, str]],
    reserved_physical_cells: set[tuple[int, int]],
    slot_pools: tuple[dict[str, Any], ...] = BITPLANE_SLOT_POOLS,
):
    for pool in slot_pools:
        child = int(pool["child"])
        layer = str(pool.get("layer", "low"))
        for cell in range(81):
            if (child, cell) in reserved_physical_cells:
                continue
            if (child, cell, layer) in reserved_logical_slots:
                continue
            if (child, cell, layer) in used_slots:
                continue
            slot = dict(pool)
            slot["cell"] = cell
            yield slot


def preserved_source_logical_slots(
    slot_pools: tuple[dict[str, Any], ...] = BITPLANE_SLOT_POOLS,
) -> set[tuple[int, int, str]]:
    slots: set[tuple[int, int, str]] = set()
    for code in set(PRESERVED_SOURCE_CODES.values()):
        for pool in slot_pools:
            base = int(pool["base"])
            cell = int(code) - base
            if 0 <= cell < 81:
                slots.add((int(pool["child"]), cell, str(pool.get("layer", "low"))))
                break
    return slots


def reserved_runtime_logical_slots(
    slot_pools: tuple[dict[str, Any], ...] = BITPLANE_SLOT_POOLS,
) -> set[tuple[int, int, str]]:
    slots = preserved_source_logical_slots(slot_pools)
    for pool in slot_pools:
        child = int(pool["child"])
        layer = str(pool.get("layer", "low"))
        for reserved_child, reserved_cell in RESERVED_SOURCE_ICON_CELLS:
            if child == reserved_child:
                slots.add((child, reserved_cell, layer))
    return slots


def needs_glyph_assignment(char: str) -> bool:
    if char == "\n":
        return False
    return is_cjk_font_char(char)


def is_cjk_font_char(char: str) -> bool:
    value = ord(char)
    return (
        0x3400 <= value <= 0x4DBF
        or 0x4E00 <= value <= 0x9FFF
        or 0xF900 <= value <= 0xFAFF
        or 0x20000 <= value <= 0x2EBEF
    )


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
        source_codes = source.get("codes", [])
        laid_out = apply_source_hard_breaks(str(translation["chs_translation"]), source_codes)
        codes = encode_translation(laid_out, assignments)
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
                "translation": laid_out,
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
    for token in iter_translation_tokens(text):
        if isinstance(token, int):
            codes.append(token)
            continue
        char = token
        if char == "\n":
            codes.append(0x000A)
        elif char in PRESERVED_SOURCE_CODES:
            codes.append(PRESERVED_SOURCE_CODES[char])
        elif not needs_glyph_assignment(char):
            if ord(char) > 0x7E:
                raise ValueError(f"no preserved source glyph code for non-CJK character {char!r}")
            codes.append(ord(char))
        else:
            slot = assignments[char]
            codes.append(int(slot["base"]) + int(slot["cell"]))
    return codes


def apply_source_hard_breaks(text: str, source_codes: list[Any]) -> str:
    source_breaks = count_source_hard_breaks(source_codes)
    text = normalize_source_control_tokens(text, source_codes)
    if source_breaks <= 0:
        return text
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if "*" in normalized:
        normalized = normalized.replace("*", "\n")
    if "\n" not in normalized:
        return distribute_hard_breaks(normalized, source_breaks)
    return add_soft_line_breaks(normalized, source_codes)


def normalize_source_control_tokens(text: str, source_codes: list[Any]) -> str:
    codes = normalize_source_codes(source_codes)
    if len(codes) >= 2 and codes[0] == 0x003F and codes[1] == 0x0040 and text.startswith("_`"):
        return "?@" + text[2:]
    return text


def count_source_hard_breaks(source_codes: list[Any]) -> int:
    return sum(1 for code in normalize_source_codes(source_codes) if code == 0x000A)


def normalize_source_codes(source_codes: list[Any]) -> list[int]:
    codes: list[int] = []
    for code in source_codes:
        try:
            codes.append(parse_code_value(code))
        except (TypeError, ValueError):
            continue
    return codes


def parse_code_value(code: Any) -> int:
    return int(code, 16 if isinstance(code, str) and code.lower().startswith("0x") else 10)


def source_line_lengths(source_codes: list[Any]) -> list[int]:
    lengths: list[int] = []
    current = 0
    for code in normalize_source_codes(source_codes):
        if code == 0x000A:
            lengths.append(current)
            current = 0
        else:
            current += 1
    lengths.append(current)
    return lengths


def add_soft_line_breaks(text: str, source_codes: list[Any]) -> str:
    break_budget = count_source_hard_breaks(source_codes) - text.count("\n")
    if break_budget <= 0:
        return text
    source_lengths = [length for length in source_line_lengths(source_codes) if length > 0]
    if not source_lengths:
        return text
    max_width = max(source_lengths)
    if max_width <= 0:
        return text

    output_lines: list[str] = []
    for line in text.split("\n"):
        if break_budget <= 0 or display_width(line) <= max_width:
            output_lines.append(line)
            continue
        wrapped, used = wrap_line_to_width(line, max_width, break_budget)
        output_lines.extend(wrapped)
        break_budget -= used
    return "\n".join(output_lines)


def wrap_line_to_width(line: str, max_width: float, break_budget: int) -> tuple[list[str], int]:
    lines: list[str] = []
    remaining = line
    used = 0
    while break_budget > 0 and display_width(remaining) > max_width:
        split_at = choose_soft_break(remaining, max_width)
        if split_at <= 0 or split_at >= len(remaining):
            break
        lines.append(remaining[:split_at].rstrip())
        remaining = remaining[split_at:].lstrip()
        break_budget -= 1
        used += 1
    lines.append(remaining)
    return lines, used


def choose_soft_break(text: str, max_width: float) -> int:
    width = 0.0
    last_natural = -1
    for index, char in enumerate(text):
        width += char_display_width(char)
        if char in "，。、；：！？,.!?:;)]）】」』":
            last_natural = index + 1
        elif char.isspace():
            last_natural = index + 1
        if width > max_width:
            if last_natural > 0:
                return last_natural
            return max(1, index)
    return len(text)


def display_width(text: str) -> float:
    return sum(char_display_width(char) for char in text)


def char_display_width(char: str) -> float:
    value = ord(char)
    if char == "\n":
        return 0.0
    if value <= 0x007E:
        return 0.65
    if 0xFF61 <= value <= 0xFF9F:
        return 0.65
    return 1.0


def distribute_hard_breaks(text: str, break_count: int) -> str:
    tokens = layout_tokens(text)
    if len(tokens) <= 1:
        return text
    line_count = min(break_count + 1, len(tokens))
    lines: list[str] = []
    start = 0
    for line_index in range(line_count - 1):
        remaining_lines = line_count - line_index
        remaining_units = token_units(tokens[start:])
        target_units = max(1, round(remaining_units / remaining_lines))
        break_index = choose_break_index(tokens, start, target_units)
        lines.append("".join(tokens[start:break_index]).strip())
        start = break_index
    lines.append("".join(tokens[start:]).strip())
    return "\n".join(line for line in lines if line)


def layout_tokens(text: str) -> list[str]:
    tokens: list[str] = []
    cursor = 0
    for match in INLINE_CODE_RE.finditer(text):
        tokens.extend(text[cursor : match.start()])
        tokens.append(match.group(0))
        cursor = match.end()
    tokens.extend(text[cursor:])
    return [token for token in tokens if token]


def token_units(tokens: list[str]) -> int:
    return sum(1 for _token in tokens)


def choose_break_index(tokens: list[str], start: int, target_units: int) -> int:
    ideal = min(len(tokens) - 1, start + max(1, target_units))
    punctuation = "，、。；：;:,.!?！？）】」』"
    for index in range(ideal, start, -1):
        if tokens[index - 1] in punctuation:
            return index
    for index in range(ideal + 1, len(tokens)):
        if tokens[index - 1] in punctuation:
            return index
    return ideal


def iter_translation_tokens(text: str):
    cursor = 0
    for match in INLINE_CODE_RE.finditer(text):
        yield from text[cursor : match.start()]
        yield int(match.group(1), 16)
        cursor = match.end()
    yield from text[cursor:]


def visible_translation_chars(text: str) -> list[str]:
    return [token for token in iter_translation_tokens(text) if isinstance(token, str)]


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
        mode = "render_bitplane" if "layer" in slot else "render"
        patches.append(
            {
                "mode": mode,
                "target_page": slot["target_page"],
                "target_child": slot["child"],
                "target_cell": slot["cell"],
                **({"layer": slot["layer"]} if "layer" in slot else {}),
                "char": char,
                "font": str(font_path),
                "font_index": font_index,
                "font_size": font_size,
                "render_mode": "palette3" if mode == "render_bitplane" and render_mode == "grayscale" else render_mode,
                "threshold": threshold,
                "gray_threshold": gray_threshold,
                "stroke_radius": stroke_radius,
                "preview": str(
                    preview_dir
                    / f"child{slot['child']}_cell{slot['cell']:02d}_{slot.get('layer', 'full')}_{ord(char):04x}.png"
                ),
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
                    "notes": f"generated CHS tutorial assignment; layer={slot.get('layer', 'full')}",
                }
            )


def runtime_texture_for_child(child: int) -> str:
    return f"0x{0x040DC200 + child * 0x2100:08x}"


if __name__ == "__main__":
    raise SystemExit(main())
