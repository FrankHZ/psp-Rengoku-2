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
| `local/work/combined_chs_v23_tutorial_usa_aligned_bitplane/` | Current broad build metadata with all 1637 current parsed target rows and DATA001/0008 tutorial placeholders promoted; 1033 logical glyphs occupy 554 physical cells. |
| `local/rebuilt/combined_chs_v23_tutorial_usa_aligned_bitplane_extracted/` | Current broad PPSSPP-ready build. |
| `local/work/chs_coverage_v23_tutorial_usa_aligned_bitplane/` | Current v23 coverage report; zero rows not in build for the current parsed target set. |
| `local/work/page_base_probe_help0017_gap66_v2/` | Clean page-base boundary probe for child 9 / `0x0661` and child 10 / `0x06b2`. |
| `local/rebuilt/page_base_probe_help0017_gap66_v2_extracted/` | PPSSPP-ready copy of the current page-base boundary probe. |
| `local/rebuilt/bitplane_probe_v1_extracted/` | PPSSPP-ready split low/high bitplane marker probe. |
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
