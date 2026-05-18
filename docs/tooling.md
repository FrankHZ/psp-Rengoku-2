# Tooling Index

This is the maintained script map after the cleanup pass. Historical one-off
probe builders and superseded sheet generators were removed; use git history if
an old experiment must be reconstructed.

## Current CHS Build Path

| Script | Purpose |
| --- | --- |
| `tools/build_chs_combined_data001.py` | Builds the broad PPSSPP-ready artifact with one shared font assignment pass. Despite the legacy filename, it can include DATA002 and DATA003 text patches. Current broad builds also recenter ANK low-layer cell 17 so the halfwidth `1` aligns visually with other halfwidth digits without changing stroke weight. |
| `tools/build_chs_tutorial.py` | Shared CHS assignment/layout helper module plus the older focused tutorial builder. Owns bitplane assignment, source-symbol reservation, and source-budget soft wrapping. |
| `tools/build_chs_offset_table.py` | Builds one translated offset-table target with font patches and source hard-break preservation. |
| `tools/stage_font_probe.py` | Stages extracted-folder builds by patching font pages and same-size MCD3 text entries. |
| `tools/build_psp_iso.py` | Builds a PSP ISO from a PPSSPP-ready extracted folder using UMDGen-like ISO9660 layout: blank volume id, unversioned file names, fixed path-table sectors, 2048-byte directory sectors, and matching the observed UMDGen file LBA order. v41 ISO was confirmed in PPSSPP; keep hardware/PPSSPP boot as the final validation gate for future builds. |
| `tools/report_chs_coverage.py` | Summarizes parsed-row coverage, not-in-build rows, and current glyph headroom. |
| `tools/report_actual_cjk_requirement.py` | Counts actual unique CJK/non-ASCII requirements from translated rows plus local override/classification sheets. |
| `tools/export_chs_font_corpus.py` | Exports CJK-only CHS corpora for external font generation. |
| `tools/build_full_jp_texts.py` | Builds the reviewed `code,char` map from `local/ocr_reviewed/` and re-decodes known JP extracts. |
| `tools/export_translation_review_pack.py` | Exports JSON review files with CHS text and alignment context when a fresh reviewer pack is needed. |
| `tools/format_chs_manual_layout.py` | Applies manual/help layout overrides and key-token cleanup. Retained for future manual edits. |
| `tools/make_chs_name_input_sheet.py` | Creates DATA002/0065 name-input confirmation rows 82-84 when that sheet is regenerated. |
| `tools/make_equipment_jp_first_layers.py` | Builds layered DATA001/0015 equipment sheets with `chs_unshrunk` for review and `chs_shrunk` for runtime fitting; accepts reviewer `current_chs` overrides from `translation_reviewed/equipment.json`. |
| `tools/apply_story_glossary.py` | Applies `docs/chs-glossary.json` to DATA003/1089 target and review sheets so story names stay consistent. |
| `tools/make_ui_data002_review_layers.py` | Builds the DATA001/0016 UI and DATA002/0065 target/review overlays: English standalone attack attributes plus translated DATA002 rough rows. Retained for regenerating those layers if needed. |
| `tools/promote_reviewed_translation_package.py` | Promotes the local `translation_reviewed/` JSON package into v41 target sheets and a consolidated v12 review package, with runtime-fit overrides for rows too long for source slots. |
| `tools/compare_chs_fonts.py` | Compares candidate CHS font rendering. |
| `tools/patch_savedata_sfo.py` | Lists or patches existing PSP savedata `PARAM.SFO` metadata; `--rengoku2-chs` translates the current Rengoku 2 save-list title/detail fields in fixed-size UTF-8 slots. |

Current broad-build command shape:

```powershell
.\.venv\Scripts\python.exe tools/build_chs_combined_data001.py `
  --target DATA001/0003 local/work/translation_refine_v1/merged_target_sheets_v41_reviewed_all/DATA001_0003_full_current_target_sheet.json `
  --target DATA001/0008 local/work/translation_refine_v1/merged_target_sheets_v41_reviewed_all/DATA001_0008_full_current_target_sheet.json `
  --target DATA001/0012 local/work/translation_refine_v1/merged_target_sheets_v41_reviewed_all/DATA001_0012_full_current_target_sheet.json `
  --target DATA001/0015 local/work/translation_refine_v1/merged_target_sheets_v41_reviewed_all/DATA001_0015_full_current_target_sheet.json `
  --target DATA001/0016 local/work/translation_refine_v1/merged_target_sheets_v41_reviewed_all/DATA001_0016_full_current_target_sheet.json `
  --target DATA001/0017 local/work/translation_refine_v1/merged_target_sheets_v41_reviewed_all/DATA001_0017_full_current_target_sheet.json `
  --target DATA002/0065 local/work/translation_refine_v1/merged_target_sheets_v41_reviewed_all/DATA002_0065_full_current_target_sheet.json `
  --target DATA003/1089 local/work/translation_refine_v1/merged_target_sheets_v41_reviewed_all/DATA003_1089_jp_first_target_sheet.json `
  --work-root local/work/<name> `
  --output-root local/rebuilt/<name>_extracted `
  --font local/fonts/full-semibold-18.fnt `
  --font-size 13 `
  --render-mode palette3 `
  --threshold 64 `
  --gray-threshold 176 `
  --assignment-model bitplane `
  --overwrite
```

## Text Extraction And Import

| Script | Purpose |
| --- | --- |
| `tools/extract_text.py` | Exports candidate strings or confirmed offset-table runs to JSON. |
| `tools/import_text.py` | Imports same-size or shorter edited text JSON back into an entry binary. |
| `tools/extract_offset_table_runs.py` | Extracts length-prefixed text/glyph-code runs from confirmed offset-table containers. |
| `tools/decode_offset_table_text.py` | Applies a seed glyph map to offset-table records for survey/debug output. |
| `tools/export_script_table.py` | Exports script-like offset-table rows with nearby `#start` command context. |
| `tools/search_encoded_text.py` | Searches encoded text/code sequences in local binaries. |
| `tools/scan_text.py` | Raw ASCII/UTF-8/Shift-JIS candidate scanner. Useful for first-pass inspection. |
| `tools/align_reference_text.py` | Aligns a JP extraction with ignored USA reference extraction by record/run. |

## Archive And Container Utilities

| Script | Purpose |
| --- | --- |
| `tools/inspect_mcd3.py` | Inspects the Rengoku 2 `DATA000.BIN` MCD3 archive index. |
| `tools/extract_mcd3_entries.py` | Extracts indexed MCD3 entries into ignored local work folders with a manifest. |
| `tools/replace_mcd3_entry.py` | Replaces one same-size indexed MCD3 entry in a copied archive. |
| `tools/archive_entry_inventory.py` | Inventories entries referenced by the MCD3 index. |
| `tools/binary_inventory.py` | Summarizes headers, entropy, markers, and ASCII strings. |
| `tools/inspect_tdl.py` | Inspects `.TDL` resource containers. |
| `tools/replace_tdl_child.py` | Replaces one same-size child in a `.TDL` copy. |
| `tools/replace_tdl_children.py` | Replaces multiple same-size children in a `.TDL` copy. |
| `tools/inspect_pack0001.py` | Inspects `PACK0001` resource containers. |
| `tools/inspect_mscr.py` | Inspects `MSCR` map/scene resource bundles. |

Library modules used by the command-line scripts:

```text
tools/mcd3.py
tools/mig.py
tools/mscr.py
tools/offset_table.py
tools/pack0001.py
tools/param_sfo.py
tools/tdl.py
tools/text_codec.py
tools/glyph_map.py
tools/png_rgba.py
```

## Font And Rendering

| Script | Purpose |
| --- | --- |
| `tools/inspect_mig.py` | Inspects `MIG.00.1PSP` resources. |
| `tools/export_mig_png.py` | Exports supported MIG textures to PNG. |
| `tools/analyze_font_grid.py` | Analyzes font grid geometry. |
| `tools/analyze_font_levels.py` | Analyzes original font palette/index levels. |
| `tools/export_glyph_cells.py` | Exports font atlas cells and glyph ID hypotheses for mapping. |
| `tools/export_jp_glyph_table.py` | Exports a JP logical glyph-cell map and contact sheets. |
| `tools/build_jp_glyph_table_v2.py` | Builds the reviewer glyph-table package and 2bpp contact sheets. |
| `tools/research_jp_glyph_usage.py` | Joins human-reviewed OCR text grids to extracted JP `glyph_codes` usage. |
| `tools/make_glyph_identification_sheet.py` | Builds reviewer sheets for unknown/blank used glyph cells. |
| `tools/mark_glyph_identification_cells.py` | Marks cells needing identification on v2-style 2bpp contact sheets. |
| `tools/render_mig_font_cell.py` | Renders a TTF/TTC/BMFont glyph into a MIG font cell with layer-preserving 2bpp writes. |
| `tools/patch_mig_font_cell.py` | Replaces font atlas cells with test patterns. Retained because tests cover the low-level patch path. |
| `tools/copy_mig_font_cell.py` | Copies one compatible MIG font cell into another page. |
| `tools/font_cell_inventory.py` | Inventories occupied and empty font cells. |
| `tools/map_runtime_font_pages.py` | Maps PPSSPP dumped font texture addresses back to extracted font pages. |
| `tools/report_runtime_font_pages.py` | Reports distinct dumped runtime font-page observations by pixels, CLUT hash, and row/cell fingerprints. |
| `tools/runtime_texture_inventory.py` | Inventories PPSSPP dumped texture PNGs. |
| `tools/translation_char_inventory.py` | Counts unique translated characters from local draft sheets. |

## Patch Packaging Placeholder

| Script | Purpose |
| --- | --- |
| `tools/make_patch.py` | Placeholder for future xdelta/PPF/BPS style patch generation. Not part of the current PPSSPP extracted-folder build path. |

## Verification

Run the Python tests after tooling changes:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

For current local artifacts and PPSSPP-ready outputs, see
`docs/local-artifacts.md`.

Existing-save metadata patch example:

```powershell
.\.venv\Scripts\python.exe tools/patch_savedata_sfo.py `
  G:\Codes-roms\emulators\ppsspp_win\memstick\PSP\SAVEDATA\ULJM05055_DATA0000\PARAM.SFO `
  --rengoku2-chs --dry-run
```

Replace `--dry-run` with `--in-place` only after reviewing the reported field
changes, or pass an explicit output `PARAM.SFO` path to write a patched copy.
