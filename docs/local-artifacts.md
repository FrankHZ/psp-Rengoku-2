# Local Artifacts

Everything under `local/` is ignored by git. Keep ignored outputs only when
they are current evidence, current build inputs, or PPSSPP-ready deliverables.
Remove superseded builds after their results are copied into tracked docs.

## Preserve

Current source/extraction inputs:

| Path | Purpose |
| --- | --- |
| `local/work/mcd3_entries/` | Extracted JP archive entries used by text/font tools. |
| `local/work/mcd3_entries_usa/` | Extracted USA archive entries used for alignment. |
| `local/work/tdl_DATA001_0002/` | Extracted JP font TDL children. |
| `local/work/glyph_cells/` | Exported font cell crops and manifest for page/cell reasoning. |
| `local/work/rendered_mig_pages/` | Baseline rendered MIG pages for font comparison. |
| `local/work/dumped_textures/` | Runtime texture dumps used to compare static and in-game font pages. |
| `local/work/runtime_font_page_scan_v1/` | Per-PNG runtime font-page scan; do not collapse same-address CLUT variants. |
| `local/work/font_routing_survey_v1/` | Clean-baseline runtime/archive/glyph-code routing survey. |
| `local/work/rendered_mig_candidates_v1/` | Forced normal-palette render of all `0x2110` archive MIG candidates. |
| `local/work/rendered_mig_candidates_v1_debug/` | Debug-contrast render of all `0x2110` archive MIG candidates. |
| `local/work/mig_index_layers_v1/` | Per-palette-index layer renders for the known font TDL pages. |
| `local/work/mig_index_layers_codejap00_v1/` | Focused per-index layer render for `codeJAP14x14_00_`. |
| `local/work/runtime_clut_layer_inference_v1/` | Clean PPSSPP dump to low/high 2-bit layer inference. |
| `local/work/bitplane_probe_v1/` | Current split low/high bitplane marker probe metadata, stage config, previews, and manifest. |
| `local/work/child11_high_base_probe_v1/` | Confirmed help/manual probe for child 11 low base `0x0754` and high base `0x07a5`. |
| `local/work/jp_glyph_table_v1/` | First-pass full JP logical-cell table: seeded labels, template-OCR guesses, and per-child/layer review contact sheets. |
| `local/work/jp_glyph_clear_pages_v1/` | Low/high glyph page renders for external OCR/API experiments, plus cell crops, manifest, Google OCR CSV, joined OCR map, and summary. |
| `local/work/jp_glyph_table_v2/` | Reviewer-oriented glyph map, human-edit CSVs, and text grids; contact sheets use 2bpp page renders and preserve ANK `14x9`/`9x14` geometry separately from JP `9x9`/`14x14` pages. |
| `local/ocr_reviewed/` | Human-reviewed OCR text grids, one plain text file per low/high page; `□` normally marks unknown/blank except the block08 square-button cell. |
| `local/work/jp_glyph_usage_research_v1/` | Usage report joining `local/ocr_reviewed` to extracted JP `glyph_codes` records; includes watch-block CSVs and blank/unknown-cell follow-up list. |
| `local/work/jp_glyph_usage_research_v1/marked_contact_sheets/` | Correct reviewer sheets for unknown/blank glyph cells, using the same 2bpp full-page layout as `jp_glyph_table_v2/contact_sheets/` and red-marking cells to identify. |
| `local/work/jp_glyph_usage_research_v1/contact_sheets/` | Superseded cropped-cell contact sheets; keep only as a generated intermediate, not as the review source. |
| `local/work/chs_font_corpus_v1/` | Text corpus for external CHS font generation; main file is `translated_chs_unique_font_chars.txt`. |
| `local/fonts/test.fnt`, `local/fonts/test_0.png` | External 8-bit BMFont atlas generated from the CHS font corpus. |
| `local/fonts/test-semibold.fnt`, `local/fonts/test-semibold_0.png` | SemiBold 16px BMFont atlas for font-weight comparison. |
| `local/fonts/test-semibold-17.fnt`, `local/fonts/test-semibold-17_0.png` | SemiBold 17px BMFont atlas for larger/heavier font comparison. |
| `local/fonts/test-semibold-18.fnt`, `local/fonts/test-semibold-18_0.png` | SemiBold 18px BMFont atlas for larger/heavier font comparison. |
| `local/fonts/test-semibold-19.fnt`, `local/fonts/test-semibold-19_0.png` | SemiBold 19px BMFont atlas for larger/heavier font comparison. |
| `local/fonts/test-regular-18.fnt`, `local/fonts/test-regular-18_0.png` | Regular 18px BMFont atlas for larger font comparison. |
| `local/fonts/test_plus.fnt`, `local/fonts/test_plus_0.png` | Local completion of `test.fnt` with the 8 chars needed by current v23 build but absent from `test.fnt`: `亢括擒稍符舱译阈`. |
| `local/fonts/corpus-semibold-18.fnt`, `local/fonts/corpus-semibold-18_0.png` | Current corpus SemiBold 18px BMFont generated from the CHS corpus only; fallback if the larger full atlas has runtime issues. |
| `local/fonts/full-semibold-18.fnt`, `local/fonts/full-semibold-18_*.png` | Current default SemiBold 18px BMFont with about 20k CJK glyphs across 9 atlas pages; v33 uses this through the multi-page BMFont renderer. |

Current inventories and translator sheets:

| Path | Purpose |
| --- | --- |
| `local/work/global_text_inventory/` | Table inventory and translation queue. |
| `local/work/equipment_catalog_inventory/` | Equipment/catalog inventory report. |
| `local/work/equipment_chs_full/` | Full equipment/catalog CHS draft. |
| `local/work/equipment_chs_full_buildfit/` | Full equipment sheet adjusted for glyph capacity. |
| `local/work/equipment_chs_name_english_v1/` | Readable equipment-name variant used by current broad builds; actual English only when it fits, otherwise CHS names. |
| `local/work/full_translation_glyph_estimate_v1/` | All-parsed-target glyph estimate from available local CHS drafts plus missing-row queue. |
| `local/work/actual_cjk_requirement_v1/` | Actual translated/candidate-bank CJK requirement report, including DATA003/1089 visible script rows and DATA002/0065 USA alignment overrides. |
| `local/work/name_input_chs_v1/` | DATA002/0065 name-input confirmation sheet for records 82-84. |
| `local/work/story_chs_full/` | Full aligned story sheets and reports. |
| `local/work/tutorial_chs_full_v1/` | Full tutorial sheet, stage config, and glyph assignments. |
| `local/work/ui_help_chs_v1/` | Current UI/help translator sheets. |
| `local/work/font_compare/` | SimSun/local-font comparison report and contact sheet. |
| `local/work/font_level_analysis/` | Original font palette/index-level analysis. |
| `local/work/page_base_candidates/` | Unknown JP code scans and static MIG candidate matches. |

Current PPSSPP artifacts and their work roots:

| Path | Purpose |
| --- | --- |
| `local/work/full_current_target_sheets_v2/` | Merged full target sheets: validated v21 rows plus estimate rows fitted to slot budgets. |
| `local/work/placeholder_investigation_v1/` | Older report of `粗译` placeholder rows from the pre-full-tutorial-alignment estimate source; superseded for DATA001/0008 by `tutorial_usa_alignment_promotions_v1`. |
| `local/work/tutorial_placeholder_investigation_v1/` | First DATA001/0008 tutorial decoding anchor using records 70-71 / Movement page. |
| `local/work/tutorial_usa_alignment_promotions_v1/` | DATA001/0008 same-record USA alignment promotion sheet and fit report; replaces all 55 previous tutorial placeholders. |
| `local/work/v23_translation_review_pack/` | Per-bin JSON review pack for testers: current v23 CHS rows plus local USA alignment text and match metadata. |
| `local/work/combined_chs_v23_tutorial_usa_aligned_bitplane/` | Current text baseline metadata with all 1637 parsed target rows and DATA001/0008 tutorial placeholders promoted; 1033 logical glyphs occupy 554 physical cells. |
| `local/rebuilt/combined_chs_v23_tutorial_usa_aligned_bitplane_extracted/` | PPSSPP-ready v23 text-baseline build, superseded for font testing by v28. |
| `local/work/chs_coverage_v23_tutorial_usa_aligned_bitplane/` | v23 coverage report; zero rows not in build for the current parsed target set. |
| `local/work/combined_chs_v24_bmfont_test/` | v24 test build metadata using the BMFont atlas (`test_plus.fnt`) for CHS glyph rendering. |
| `local/rebuilt/combined_chs_v24_bmfont_test_extracted/` | PPSSPP-ready v24 BMFont test build. |
| `local/work/chs_coverage_v24_bmfont_test/` | Coverage report for the v24 BMFont test build; zero current parsed rows missing. |
| `local/work/combined_chs_v25_semibold18_quantizer_test/` | v25 test build metadata using `test-semibold-18.fnt` and the earlier palette3 2bpp quantizer before cutoff tuning. |
| `local/rebuilt/combined_chs_v25_semibold18_quantizer_test_extracted/` | PPSSPP-ready v25 semibold-18 quantizer test build. |
| `local/work/chs_coverage_v25_semibold18_quantizer_test/` | Coverage report for the v25 semibold-18 quantizer test build; zero current parsed rows missing. |
| `local/work/combined_chs_v26_regular18_cutoff_test/` | v26 regular-18 test build metadata using `test-regular-18.fnt` and the 2bpp `1..32 -> 0` cutoff. |
| `local/rebuilt/combined_chs_v26_regular18_cutoff_test_extracted/` | PPSSPP-ready v26 regular-18 cutoff test build. |
| `local/work/chs_coverage_v26_regular18_cutoff_test/` | Coverage report for the v26 regular-18 cutoff test build; zero current parsed rows missing. |
| `local/work/combined_chs_v26_semibold18_cutoff_test/` | v26 semibold-18 test build metadata using `test-semibold-18.fnt` and the 2bpp `1..32 -> 0` cutoff. |
| `local/rebuilt/combined_chs_v26_semibold18_cutoff_test_extracted/` | PPSSPP-ready v26 semibold-18 cutoff test build. |
| `local/work/chs_coverage_v26_semibold18_cutoff_test/` | Coverage report for the v26 semibold-18 cutoff test build; zero current parsed rows missing. |
| `local/work/combined_chs_v27_semibold19_cutoff_test/` | v27 semibold-19 test build metadata using `test-semibold-19.fnt` and the 2bpp `1..32 -> 0` cutoff. |
| `local/rebuilt/combined_chs_v27_semibold19_cutoff_test_extracted/` | PPSSPP-ready v27 semibold-19 cutoff test build. |
| `local/work/chs_coverage_v27_semibold19_cutoff_test/` | Coverage report for the v27 semibold-19 cutoff test build; zero current parsed rows missing. |
| `local/work/combined_chs_v28_semibold18_cutoff16_test/` | Current font baseline build metadata using `test-semibold-18.fnt` and the 2bpp `1..16 -> 0` cutoff. |
| `local/rebuilt/combined_chs_v28_semibold18_cutoff16_test_extracted/` | Current PPSSPP-ready semibold-18 cutoff16 test build. |
| `local/work/chs_coverage_v28_semibold18_cutoff16_test/` | Coverage report for the v28 semibold-18 cutoff16 build; zero current parsed rows missing. |
| `local/work/combined_chs_v29_source_hardbreaks_semibold18/` | Current broad build metadata using semibold-18 and source `0x000a` hard-break preservation. |
| `local/rebuilt/combined_chs_v29_source_hardbreaks_semibold18_extracted/` | Current PPSSPP-ready broad build for layout regression testing. |
| `local/work/chs_coverage_v29_source_hardbreaks_semibold18/` | Coverage report for v29; zero current parsed rows missing. |
| `local/work/translation_refine_v1/` | Autonomous JP+EN translation refinement packs and merged budget-fitted target sheets. |
| `local/work/translation_review_slim_v1/` | Slim JSON review packages for human reviewers: `id`, `category`, `chs`, `jp`, `en`, plus occasional short review notes. |
| `local/work/combined_chs_v32_refined_cjk_only_symbols/` | Previous broad build metadata with v32 refinements and CJK-only generated glyph assignment. |
| `local/rebuilt/combined_chs_v32_refined_cjk_only_symbols_extracted/` | Previous PPSSPP-ready broad build for translation/font testing, superseded for font testing by v33. |
| `local/work/chs_coverage_v32_refined_cjk_only_symbols/` | Coverage report for v32; zero current parsed rows missing. |
| `local/work/combined_chs_v33_full_semibold18/` | Previous broad build metadata with v32 text refinements, CJK-only generated glyph assignment, and `full-semibold-18.fnt`. |
| `local/rebuilt/combined_chs_v33_full_semibold18_extracted/` | Previous PPSSPP-ready broad build for tester/font review, superseded by v34 because preserved punctuation/symbol cells could still be overwritten. |
| `local/work/chs_coverage_v33_full_semibold18/` | Coverage report for v33; zero current parsed rows missing. |
| `local/work/combined_chs_v34_symbol_softwrap_fix/` | Current broad build metadata with preserved punctuation/symbol cell reservations and automatic source-budget soft wrapping. |
| `local/rebuilt/combined_chs_v34_symbol_softwrap_fix_extracted/` | Current PPSSPP-ready build for punctuation/symbol and soft-linebreak testing. |
| `local/work/chs_coverage_v34_symbol_softwrap_fix/` | Coverage report for v34; zero current parsed rows missing. |
| `local/work/chs_font_corpus_v3_refined_cjk_only/` | Current CJK-only font corpus for external font generation from v32 plus full candidate-bank reference. |
| `local/work/page_base_probe_help0017_gap66_v2/` | Clean page-base boundary probe for child 9 / `0x0661` and child 10 / `0x06b2`. |
| `local/rebuilt/page_base_probe_help0017_gap66_v2_extracted/` | PPSSPP-ready copy of the current page-base boundary probe. |
| `local/rebuilt/bitplane_probe_v1_extracted/` | PPSSPP-ready split low/high bitplane marker probe. |
| `local/rebuilt/child11_high_base_probe_v1_extracted/` | PPSSPP-ready child 11 high-base probe, now confirmed in help/manual `A > 1`. |
| `local/rebuilt/tutorial_chs_full_v1_extracted/` | Full tutorial CHS build, retained as a small known-good artifact. |

Tracked generated references:

| Path | Purpose |
| --- | --- |
| `samples/runtime_glyph_map_seed.csv` | Runtime glyph observations and inferred base seeds. |
| `samples/runtime_kana_map.csv` | Generated kana runtime map with seeded consistency checks. |

## Removed

The stale combined/probe generations below were removed during cleanup because
their results are now captured in tracked docs or superseded by v23:

```text
local/work/combined_chs_v1_* through combined_chs_v22_*
local/rebuilt/combined_chs_v1_* through combined_chs_v22_*
local/work/chs_coverage_v15_* through chs_coverage_v22_*
local/work/combined_chs_story_full_v1_0003_0008_0012full
local/rebuilt/combined_chs_story_full_v1_0003_0008_0012full_extracted
local/work/equipment_chs_v1 through equipment_chs_v3
local/rebuilt/equipment_chs_v1* through equipment_chs_v2*
local/work/full_current_target_sheets_v1
local/work/story_chs_v1
local/work/ui_help_chs_build_v1
local/rebuilt/ui_help_chs_v1_DATA001_0016_extracted
local/rebuilt/ui_help_chs_v1_DATA001_0017_extracted
local/work/page_base_probe_v1 through page_base_probe_v6
local/rebuilt/page_base_probe_v1_extracted through page_base_probe_v6_extracted
local/work/page_base_probe_help0017_v1
local/work/page_base_probe_help0017_gap66_v1
local/rebuilt/page_base_probe_help0017_v1_extracted
local/rebuilt/page_base_probe_help0017_gap66_v1_extracted
```

## Rule

When creating a new ignored local output, either add it to this file with a
one-line purpose or delete it after copying useful findings into tracked docs.
