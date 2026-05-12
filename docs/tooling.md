# Tooling Index

This is the current map of repo scripts. Keep this file practical: one-line
purpose, main local inputs/outputs when they matter, and whether a script is on
the current CHS build path or mainly for research/probes.

## Current CHS Build Path

| Script | Purpose | Main inputs | Main outputs |
| --- | --- | --- | --- |
| `tools/make_equipment_name_english_variant.py` | Creates the readable equipment-name variant used by current broad builds; actual English only when it fits, otherwise CHS names. | `local/work/equipment_chs_full_buildfit/DATA001_0015_equipment_chs_full_buildfit.json` | `local/work/equipment_chs_name_english_v1/` |
| `tools/make_chs_name_input_sheet.py` | Creates DATA002/0065 name-input confirmation rows 82-84. | `local/work/extract_text_DATA002_0065_seeded.json` | `local/work/name_input_chs_v1/` |
| `tools/make_full_current_target_sheets.py` | Merges a validated build root with coverage estimate rows to make full current-target sheets, fitting rough rows to slot budgets. | A build root plus `not_in_current_build.csv` | `local/work/full_current_target_sheets_*/` |
| `tools/format_chs_manual_layout.py` | Applies current UI/manual layout fixes, including key-token cleanup, preserved JP icon-code tokens, and help-body wrapping. | `local/work/ui_help_chs_v1/*.json` | Updates the same local sheets in place |
| `tools/report_chs_coverage.py` | Summarizes parsed-row coverage, not-in-build rows, and current glyph headroom. | `local/work/full_translation_glyph_estimate_v1/all_rows_estimate.csv`, current build root | `local/work/chs_coverage_v19_manual_prose_layout/` |
| `tools/report_actual_cjk_requirement.py` | Counts actual unique CJK/non-ASCII requirements from translated rows plus local override/classification sheets. | `local/work/full_translation_glyph_estimate_v1/row_queue.csv`, `local/work/actual_cjk_requirement_v1/translation_overrides.json` | `local/work/actual_cjk_requirement_v1/` |
| `tools/report_placeholder_rows.py` | Reports rough placeholder rows and whether current local alignment has usable USA reference text. | `local/work/full_translation_glyph_estimate_v1/all_rows_estimate.csv`, `local/work/full_current_target_sheets_v2/fit_adjustments.csv` | `local/work/placeholder_investigation_v*/` |
| `tools/promote_tutorial_usa_alignments.py` | Promotes DATA001/0008 tutorial placeholders from same-record USA DATA001/0017 alignment and writes a fit report. | `local/work/full_current_target_sheets_v2/DATA001_0008_full_current_target_sheet.json`, `local/work/align_JP0008_USA0017_tutorial_full_v1.json` | `local/work/tutorial_usa_alignment_promotions_v*/` |
| `tools/export_translation_review_pack.py` | Exports one local JSON review file per patched bin/table with current CHS text and USA alignment text. | Current combined build root plus local alignment JSON files | `local/work/v*_translation_review_pack/` |
| `tools/build_chs_combined_data001.py` | Builds the broad PPSSPP-ready artifact with one shared font assignment pass; despite the legacy filename, it can include DATA002 text patches. | Target translator sheets via repeated `--target` | `local/work/combined_chs_*/`, `local/rebuilt/combined_chs_*_extracted/` |
| `tools/build_chs_offset_table.py` | Builds one translated offset-table target with font patches and preserves source `0x000a` hard-break layout. | A translator sheet plus source export/entry | A single-target work root and rebuilt extracted folder |
| `tools/build_chs_tutorial.py` | Older focused DATA001/0008 tutorial build helper. | Tutorial draft and source export | `local/work/tutorial_chs_full_v1/`, `local/rebuilt/tutorial_chs_full_v1_extracted/` |
| `tools/build_chs_equipment_slice.py` | Older focused DATA001/0015 equipment-slice build helper. | Equipment slice sheet | A single-target equipment slice build |
| `tools/stage_font_probe.py` | Stages extracted-folder builds by patching font pages and same-size MCD3 text entries. | JSON stage config | PPSSPP-ready extracted folder |

Current broad build command shape:

```powershell
.\.venv\Scripts\python.exe tools/build_chs_combined_data001.py `
  --target DATA001/0003 local/work/translation_refine_v1/merged_target_sheets_all_fit_v1/DATA001_0003_full_current_target_sheet.json `
  --target DATA001/0008 local/work/translation_refine_v1/merged_target_sheets_all_fit_v1/DATA001_0008_full_current_target_sheet.json `
  --target DATA001/0012 local/work/translation_refine_v1/merged_target_sheets_all_fit_v1/DATA001_0012_full_current_target_sheet.json `
  --target DATA001/0015 local/work/translation_refine_v1/merged_target_sheets_all_fit_v1/DATA001_0015_full_current_target_sheet.json `
  --target DATA001/0016 local/work/translation_refine_v1/merged_target_sheets_all_fit_v1/DATA001_0016_full_current_target_sheet.json `
  --target DATA001/0017 local/work/translation_refine_v1/merged_target_sheets_all_fit_v1/DATA001_0017_full_current_target_sheet.json `
  --target DATA002/0065 local/work/translation_refine_v1/merged_target_sheets_all_fit_v1/DATA002_0065_full_current_target_sheet.json `
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
| `tools/scan_text.py` | Raw ASCII/UTF-8/Shift-JIS candidate scanner. Useful early, less useful after format ownership is known. |
| `tools/translation_char_inventory.py` | Counts unique non-ASCII chars needed by local translation drafts. |

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
tools/tdl.py
tools/text_codec.py
```

## Font And Rendering

| Script | Purpose |
| --- | --- |
| `tools/inspect_mig.py` | Inspects `MIG.00.1PSP` resources. |
| `tools/export_mig_png.py` | Exports supported MIG textures to PNG. |
| `tools/export_glyph_cells.py` | Exports font atlas cells and glyph ID hypotheses for mapping. |
| `tools/export_jp_glyph_table.py` | Exports the confirmed low/high JP logical glyph-cell map, seeded labels, template-OCR guesses, and contact sheets. |
| `tools/render_clear_glyph_pages.py` | Renders 24 clean unlabeled high-res low/high font pages, grid copies, and cell crops for external OCR. |
| `tools/import_ocr_glyph_map.py` | Joins block OCR CSV output back to rendered glyph pages, cells, runtime codes, and seed-match diagnostics. |
| `tools/make_reviewed_ocr_glyph_map.py` | Builds a safer reviewed OCR glyph map with status tags for confirmed seeds, reliable full-page OCR, prefix candidates, and shifted blocks. |
| `tools/build_jp_glyph_table_v2.py` | Builds the v2 reviewer package, human-edit CSVs, and text grids, using 2bpp page renders for contact sheets and preserving ANK `9x14` and JP `14x14` geometry. |
| `tools/research_jp_glyph_usage.py` | Reads human-reviewed OCR text grids and reports which glyph cells are used by extracted JP `glyph_codes` records, with raw-bin u16 sightings kept as lower-confidence context. |
| `tools/make_glyph_identification_sheet.py` | Builds reviewer contact sheets for unknown/blank glyph cells that appear in the usage research report. |
| `tools/mark_glyph_identification_cells.py` | Marks glyph cells needing identification on v2-style 2bpp contact sheets, preserving ANK `14x9` and JP `9x9` page geometry. |
| `tools/build_full_jp_texts.py` | Builds a fresh `code,char` map from `local/ocr_reviewed/`, re-decodes all known JP extracts from the global inventory, and writes full JP text CSV/JSON plus samples. |
| `tools/export_chs_font_corpus.py` | Exports translated CHS character corpora for external font generation; under the current policy the font-char set is CJK-only because Latin/punctuation/symbols reuse source glyph codes. |
| `tools/font_cell_inventory.py` | Inventories occupied and empty font cells for CHS glyph planning. |
| `tools/render_mig_font_cell.py` | Renders a font glyph into a MIG font cell from TTF/TTC or single/multi-page BMFont `.fnt` atlases, including low/high two-bit layer-preserving writes; 2bpp output uses `0=background`, `1=light gray`, `2=deep gray`, `3=white`, with source values `1..16` dropped to background. |
| `tools/patch_mig_font_cell.py` | Replaces font atlas cells with test patterns for probes. |
| `tools/copy_mig_font_cell.py` | Copies one compatible MIG font cell into another page. |
| `tools/compare_chs_fonts.py` | Compares candidate CHS font rendering. |
| `tools/analyze_font_grid.py` | Analyzes font grid geometry. |
| `tools/analyze_font_levels.py` | Analyzes original font palette/index levels. |
| `tools/png_rgba.py` | Small PNG/RGBA helper module. |

## Runtime Mapping And Probes

| Script | Purpose |
| --- | --- |
| `tools/runtime_texture_inventory.py` | Inventories PPSSPP dumped texture PNGs. |
| `tools/map_runtime_font_pages.py` | Maps PPSSPP dumped font texture addresses back to extracted font pages. |
| `tools/report_runtime_font_pages.py` | Reports distinct dumped runtime font-page observations by pixels, CLUT hash, and row/cell fingerprints. |
| `tools/report_font_routing_survey.py` | Joins clean runtime font observations, archive MIG candidates, and glyph-code usage into a routing survey. |
| `tools/render_mig_candidates.py` | Force-renders same-size archive MIG candidates as 128x128 CLUT4 pages for font-page discovery. |
| `tools/report_mig_index_layers.py` | Splits MIG font pages into separate palette-index layer renders. |
| `tools/infer_runtime_clut_layers.py` | Infers which static low/high index groups match clean PPSSPP runtime CLUT dumps. |
| `tools/build_bitplane_probe.py` | Builds the current PPSSPP marker probe for low/high logical pages sharing one physical font cell. |
| `tools/build_child11_high_probe.py` | Builds the help/manual probe that confirmed child 11 high base `0x07a5`. |
| `tools/build_page_base_probe.py` | Builds controlled page-base/code-window probes. |
| `tools/build_kana_runtime_map.py` | Builds kana runtime map references from seeded observations. |
| `tools/stage_font_probe.py` | Also used directly for custom font/page/text probe configs. |
| `tools/compare_texture_pngs.py` | Compares dumped texture PNGs for runtime/font investigation. |
| `tools/glyph_map.py` | Glyph-map helper module used by mapping scripts. |

## Alignment And Analysis

| Script | Purpose |
| --- | --- |
| `tools/align_reference_text.py` | Aligns a JP extraction with ignored USA reference extraction by record/run. |
| `tools/analyze_offset_table_values.py` | Analyzes offset-table values during format research. |

## Patch Packaging Placeholder

| Script | Purpose |
| --- | --- |
| `tools/make_patch.py` | Placeholder for future xdelta/PPF/BPS style patch generation. Not part of the current PPSSPP extracted-folder build path. |

## Verification

Run the Python tests after tooling changes:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

For current local artifacts and PPSSPP-ready outputs, see `docs/local-artifacts.md`.
