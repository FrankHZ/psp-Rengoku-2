from __future__ import annotations

import argparse
from pathlib import Path

from build_chs_offset_table import (
    apply_translation_codes,
    build_chs_offset_table,
    build_offset_table_payload as build_equipment_text_payload,
    load_translator_sheet,
)


DEFAULT_SHEET = Path("local/work/equipment_chs_v1/DATA001_0015_equipment_slice_70-81_94-97.json")
DEFAULT_SOURCE_EXPORT = Path("local/work/extract_text_DATA001_0015_seeded.json")
DEFAULT_SOURCE_ENTRY = Path("local/work/mcd3_entries/DATA001/0015_bin.bin")
DEFAULT_WORK_ROOT = Path("local/work/equipment_chs_v1/build")
DEFAULT_OUTPUT_ROOT = Path("local/rebuilt/equipment_chs_v1_extracted")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the current bounded DATA001/0015 equipment CHS slice.")
    parser.add_argument("--sheet", type=Path, default=DEFAULT_SHEET, help="Translator sheet with record/run/chs_draft rows.")
    parser.add_argument("--source-export", type=Path, default=DEFAULT_SOURCE_EXPORT)
    parser.add_argument("--source-entry", type=Path, default=DEFAULT_SOURCE_ENTRY)
    parser.add_argument("--work-root", type=Path, default=DEFAULT_WORK_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--font", type=Path, default=Path("C:/Windows/Fonts/simsun.ttc"))
    parser.add_argument("--font-index", type=int, default=0)
    parser.add_argument("--font-size", type=int, default=13)
    parser.add_argument("--render-mode", choices=("grayscale", "binary", "palette3"), default="palette3")
    parser.add_argument("--threshold", type=int, default=64)
    parser.add_argument("--gray-threshold", type=int, default=176)
    parser.add_argument("--stroke-radius", type=int, default=0)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    build_chs_equipment_slice(
        sheet_path=args.sheet,
        source_export_path=args.source_export,
        source_entry_path=args.source_entry,
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


def build_chs_equipment_slice(
    sheet_path: Path,
    source_export_path: Path,
    source_entry_path: Path,
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
    build_chs_offset_table(
        sheet_path=sheet_path,
        table=("DATA001", 15),
        source_export_path=source_export_path,
        source_entry_path=source_entry_path,
        work_root=work_root,
        output_root=output_root,
        font_path=font_path,
        font_index=font_index,
        font_size=font_size,
        render_mode=render_mode,
        threshold=threshold,
        gray_threshold=gray_threshold,
        stroke_radius=stroke_radius,
        overwrite=overwrite,
    )


if __name__ == "__main__":
    raise SystemExit(main())
