from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from build_chs_offset_table import (
    apply_translation_codes,
    build_offset_table_payload,
    infer_source_entry,
    infer_source_export,
    load_translator_sheet,
    parse_table_id,
)
from build_chs_tutorial import DEFAULT_SLOT_POOLS, assign_chars, build_font_patches, needs_glyph_assignment, write_assignments_csv
from build_chs_tutorial import BITPLANE_SLOT_POOLS, assign_chars_bitplane
from build_chs_tutorial import visible_translation_chars
from patch_title_credit import DEFAULT_CREDIT_TEXT, patch_title_credit
from stage_font_probe import stage_font_probe


DEFAULT_TARGETS = (
    ("DATA001/0008", "local/work/chs_tutorial_draft_DATA001_0008.json"),
    ("DATA001/0015", "local/work/equipment_chs_v1/DATA001_0015_equipment_slice_70-81_94-97.json"),
    ("DATA001/0016", "local/work/ui_help_chs_v1/DATA001_0016_ui_sheet.json"),
    ("DATA001/0017", "local/work/ui_help_chs_v1/DATA001_0017_help_sheet.json"),
)

DEFAULT_PATCHED_EBOOT = Path("local/work/eboot_width_patch/EBOOT_DEC_WIDTH7_SAVECHS.BIN")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a combined CHS artifact with one font patch pass.")
    parser.add_argument(
        "--target",
        action="append",
        nargs=2,
        metavar=("TABLE", "SHEET"),
        help="Target table and translator sheet. May be repeated. Defaults to tutorial/equipment/UI/help.",
    )
    parser.add_argument("--work-root", type=Path, default=Path("local/work/combined_chs_v1"))
    parser.add_argument("--output-root", type=Path, default=Path("local/rebuilt/combined_chs_v1_extracted"))
    parser.add_argument("--font", type=Path, default=Path("C:/Windows/Fonts/simsun.ttc"))
    parser.add_argument("--font-index", type=int, default=0)
    parser.add_argument("--font-size", type=int, default=13)
    parser.add_argument("--render-mode", choices=("grayscale", "binary", "palette3"), default="palette3")
    parser.add_argument("--threshold", type=int, default=64)
    parser.add_argument("--gray-threshold", type=int, default=176)
    parser.add_argument("--stroke-radius", type=int, default=0)
    parser.add_argument(
        "--patched-eboot",
        type=Path,
        default=DEFAULT_PATCHED_EBOOT,
        help="Optional decrypted/patched EBOOT to copy into the staged build when present.",
    )
    parser.add_argument(
        "--no-eboot-width-patch",
        action="store_true",
        help="Do not copy the local patched EBOOT into the staged build.",
    )
    parser.add_argument(
        "--assignment-model",
        choices=("single", "bitplane"),
        default="bitplane",
        help="Use the legacy one-glyph-per-physical-cell model or the confirmed low/high bitplane model.",
    )
    parser.add_argument("--title-credit", default=DEFAULT_CREDIT_TEXT, help="Small title-background credit text.")
    parser.add_argument("--no-title-credit", action="store_true", help="Do not patch the title-background credit.")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    target_specs = tuple((table, Path(sheet)) for table, sheet in (args.target or DEFAULT_TARGETS))
    build_combined_data001(
        target_specs=target_specs,
        work_root=args.work_root,
        output_root=args.output_root,
        font_path=args.font,
        font_index=args.font_index,
        font_size=args.font_size,
        render_mode=args.render_mode,
        threshold=args.threshold,
        gray_threshold=args.gray_threshold,
        stroke_radius=args.stroke_radius,
        assignment_model=args.assignment_model,
        patched_eboot=None if args.no_eboot_width_patch else args.patched_eboot,
        title_credit=None if args.no_title_credit else args.title_credit,
        overwrite=args.overwrite,
    )
    print(f"staged {args.output_root}")
    return 0


def build_combined_data001(
    target_specs: tuple[tuple[str, Path], ...],
    work_root: Path,
    output_root: Path,
    font_path: Path,
    font_index: int = 0,
    font_size: int = 13,
    render_mode: str = "palette3",
    threshold: int = 64,
    gray_threshold: int = 176,
    stroke_radius: int = 0,
    assignment_model: str = "bitplane",
    patched_eboot: Path | None = DEFAULT_PATCHED_EBOOT,
    title_credit: str | None = DEFAULT_CREDIT_TEXT,
    overwrite: bool = False,
) -> None:
    targets = load_targets(target_specs)
    all_rows = [row for target in targets for row in target["rows"]]
    required_chars = required_assigned_chars(all_rows)
    if assignment_model == "single":
        slot_capacity = sum(81 for _ in DEFAULT_SLOT_POOLS)
        assignments = assign_chars(all_rows)
    elif assignment_model == "bitplane":
        slot_capacity = sum(81 for _ in BITPLANE_SLOT_POOLS)
        assignments = assign_chars_bitplane(all_rows)
    else:
        raise ValueError(f"unsupported assignment model: {assignment_model!r}")
    if len(required_chars) > slot_capacity:
        raise ValueError(
            f"combined build needs {len(required_chars)} assigned glyphs, "
            f"but only {slot_capacity} confirmed runtime slots are available; "
            "reduce drafted rows or add another confirmed slot pool"
        )

    work_root.mkdir(parents=True, exist_ok=True)
    write_assignments_csv(work_root / "runtime_glyph_assignments.csv", assignments)
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

    text_patches = []
    for target in targets:
        archive, entry_id = target["table"]
        source_export = json.loads(target["source_export"].read_text(encoding="utf-8"))
        source_by_record = {(entry["record"], entry["run"]): entry for entry in source_export["entries"]}
        text_payload = build_offset_table_payload(
            target["rows"],
            source_by_record,
            source=str(target["source_entry"]).replace("\\", "/"),
            table=f"{archive}/{entry_id:04d}",
        )
        apply_translation_codes(text_payload["entries"], assignments)
        text_json = work_root / f"{archive}_{entry_id:04d}_chs.json"
        text_json.write_text(json.dumps(text_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        text_patches.append(
            {
                "entry_id": entry_id,
                "source_entry": str(target["source_entry"]),
                "json": str(text_json),
            }
        )

    stage_config = {
        "extracted_root": "local/extracted/Rengoku 2",
        "entries_root": "local/work/mcd3_entries",
        "work_root": str(work_root / "stage"),
        "output_root": str(output_root),
        "font_patches": font_patches,
        "text_patches": text_patches,
        "overwrite": overwrite,
    }
    (work_root / "stage_combined_chs.json").write_text(
        json.dumps(stage_config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    stage_font_probe(stage_config)
    apply_patched_eboot(output_root, patched_eboot)
    if title_credit:
        reset_title_art(Path(stage_config["extracted_root"]), output_root)
        patch_title_credit(output_root, title_credit)


def apply_patched_eboot(output_root: Path, patched_eboot: Path | None) -> None:
    if patched_eboot is None or not patched_eboot.exists():
        return
    target = output_root / "PSP_GAME" / "SYSDIR" / "EBOOT.BIN"
    if not target.exists():
        raise FileNotFoundError(f"staged EBOOT target does not exist: {target}")
    shutil.copyfile(patched_eboot, target)


def reset_title_art(extracted_root: Path, output_root: Path) -> None:
    source = extracted_root / "PSP_GAME" / "PIC1.PNG"
    target = output_root / "PSP_GAME" / "PIC1.PNG"
    if not source.exists():
        raise FileNotFoundError(f"source title art does not exist: {source}")
    if not target.exists():
        raise FileNotFoundError(f"staged title art target does not exist: {target}")
    shutil.copyfile(source, target)


def load_targets(target_specs: tuple[tuple[str, Path], ...]) -> list[dict[str, Any]]:
    targets: list[dict[str, Any]] = []
    for table_text, sheet_path in target_specs:
        table = parse_table_id(table_text)
        archive, entry_id = table
        rows = load_translator_sheet(sheet_path, table=f"{archive}/{entry_id:04d}")
        targets.append(
            {
                "table": table,
                "sheet": sheet_path,
                "rows": rows,
                "source_export": infer_source_export(table),
                "source_entry": infer_source_entry(table),
            }
        )
    if not targets:
        raise ValueError("combined build requires at least one target")
    return targets


def required_assigned_chars(rows: list[dict[str, Any]]) -> set[str]:
    return {
        char
        for row in rows
        for char in visible_translation_chars(str(row["chs_translation"]))
        if needs_glyph_assignment(char)
    }


if __name__ == "__main__":
    raise SystemExit(main())
