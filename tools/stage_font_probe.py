from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
from typing import Any

from copy_mig_font_cell import copy_font_cell
from import_text import import_text
from patch_mig_font_cell import patch_font_cells, parse_cell_range
from replace_mcd3_entry import replace_mcd3_entry
from tdl import replace_tdl_children


def stage_font_probe(config: dict[str, Any]) -> None:
    extracted_root = Path(config["extracted_root"])
    entries_root = Path(config["entries_root"])
    output_root = Path(config["output_root"])
    work_root = Path(config.get("work_root", output_root.parent / "_probe_work"))
    data_root = extracted_root / "PSP_GAME" / "USRDIR"
    index_path = data_root / "DATA000.BIN"

    if output_root.exists():
        if not config.get("overwrite", False):
            raise FileExistsError(f"{output_root} already exists; pass --overwrite to replace it")
        if not (output_root / "PSP_GAME" / "USRDIR").is_dir():
            remove_tree(output_root)

    work_root.mkdir(parents=True, exist_ok=True)
    patched_font_pages_dir = work_root / "patched_font_pages"
    patched_font_pages_dir.mkdir(parents=True, exist_ok=True)
    patched_font_tdl = work_root / "patched_font.tdl"
    patched_font_archive = work_root / "DATA001_font_patched.BIN"

    font_patches = list(config.get("font_patches") or [config["font_patch"]])
    child_sources: dict[int, Path] = {}
    for font in font_patches:
        target_child = int(font["target_child"])
        child_sources.setdefault(target_child, Path(font["target_page"]))

    replacements: dict[int, Path] = {}
    for patch_index, font in enumerate(font_patches):
        target_child = int(font["target_child"])
        target_page = replacements.get(target_child, child_sources[target_child])
        source_stem = child_sources[target_child].stem
        patched_font_page = patched_font_pages_dir / f"{source_stem}_child_{target_child:02d}_patch_{patch_index:03d}.bin"
        apply_font_patch(font, target_page, patched_font_page)
        replacements[target_child] = patched_font_page

    font_tdl_source = entries_root / "DATA001" / "0002_tdl.bin"
    replace_tdl_children(font_tdl_source, replacements, patched_font_tdl)
    replace_mcd3_entry(index_path, data_root, 2, patched_font_tdl, patched_font_archive)

    archives_dir = work_root / "archives"
    archives_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(patched_font_archive, archives_dir / "DATA001.BIN")
    for archive_index in range(2, 6):
        name = f"DATA00{archive_index}.BIN"
        shutil.copy2(data_root / name, archives_dir / name)

    text_entry = config.get("text_patch")
    if text_entry:
        source_entry = Path(text_entry["source_entry"])
        text_json = Path(text_entry["json"])
        patched_text = work_root / "patched_text_entry.bin"
        patched_combined_archive = work_root / "DATA001_font_and_text_patched.BIN"
        import_text(source_entry, text_json, patched_text)
        replace_mcd3_entry(index_path, archives_dir, int(text_entry["entry_id"]), patched_text, patched_combined_archive)
        final_archive = patched_combined_archive
    else:
        final_archive = patched_font_archive

    if not output_root.exists():
        shutil.copytree(extracted_root, output_root)
    shutil.copy2(final_archive, output_root / "PSP_GAME" / "USRDIR" / "DATA001.BIN")


def remove_tree(path: Path) -> None:
    def on_error(function: Any, value: str, exc_info: Any) -> None:
        os.chmod(value, 0o700)
        function(value)

    shutil.rmtree(path, onerror=on_error)


def parse_cells(font: dict[str, Any]) -> list[int]:
    if "target_cells" in font:
        return sorted(set(parse_cell_range(str(font["target_cells"]))))
    if "target_cell" in font:
        return [int(font["target_cell"])]
    raise ValueError("font_patch requires target_cell or target_cells")


def apply_font_patch(font: dict[str, Any], target_page: Path, output_path: Path) -> None:
    target_cells = parse_cells(font)
    mode = font["mode"]
    if mode == "box":
        patch_font_cells(
            target_page,
            output_path,
            cell_indices=target_cells,
            pattern=str(font.get("pattern", "box")),
            ink_index=int(font.get("ink_index", 15)),
        )
        return

    if mode == "copy":
        if len(target_cells) != 1:
            raise ValueError("copy mode requires exactly one target cell")
        copy_font_cell(
            Path(font["source_page"]),
            int(font["source_cell"]),
            target_page,
            target_cells[0],
            output_path,
        )
        return

    raise ValueError(f"unsupported font patch mode: {mode!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage a local extracted-folder font probe build.")
    parser.add_argument("config", type=Path, help="JSON config describing local inputs and output folder.")
    parser.add_argument("--overwrite", action="store_true", help="Replace the output folder if it already exists.")
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    if args.overwrite:
        config["overwrite"] = True
    stage_font_probe(config)
    print(f"staged {config['output_root']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
