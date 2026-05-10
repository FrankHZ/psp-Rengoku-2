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

Current inventories and translator sheets:

| Path | Purpose |
| --- | --- |
| `local/work/global_text_inventory/` | Table inventory and translation queue. |
| `local/work/equipment_catalog_inventory/` | Equipment/catalog inventory report. |
| `local/work/equipment_chs_full/` | Full equipment/catalog CHS draft. |
| `local/work/equipment_chs_full_buildfit/` | Full equipment sheet adjusted for glyph capacity. |
| `local/work/story_chs_full/` | Full aligned story sheets and reports. |
| `local/work/tutorial_chs_full_v1/` | Full tutorial sheet, stage config, and glyph assignments. |
| `local/work/ui_help_chs_v1/` | Current UI/help translator sheets. |
| `local/work/font_compare/` | SimSun/local-font comparison report and contact sheet. |
| `local/work/font_level_analysis/` | Original font palette/index-level analysis. |
| `local/work/page_base_candidates/` | Unknown JP code scans and static MIG candidate matches. |

Current PPSSPP artifacts and their work roots:

| Path | Purpose |
| --- | --- |
| `local/work/combined_chs_v12_manual_skillpoints_0003_0008_0012anchored_0015full_0016full_0017full/` | Current broad catalog/UI/help build metadata. |
| `local/rebuilt/combined_chs_v12_manual_skillpoints_0003_0008_0012anchored_0015full_0016full_0017full_extracted/` | Current broad PPSSPP-ready build. |
| `local/work/combined_chs_story_full_v1_0003_0008_0012full/` | Current full story build metadata. |
| `local/rebuilt/combined_chs_story_full_v1_0003_0008_0012full_extracted/` | Current full story PPSSPP-ready build. |
| `local/work/page_base_probe_help0017_gap66_v2/` | Clean page-base boundary probe for child 9 / `0x0661` and child 10 / `0x06b2`. |
| `local/rebuilt/page_base_probe_help0017_gap66_v2_extracted/` | PPSSPP-ready copy of the current page-base boundary probe. |
| `local/rebuilt/tutorial_chs_full_v1_extracted/` | Full tutorial CHS build, retained as a small known-good artifact. |

Tracked generated references:

| Path | Purpose |
| --- | --- |
| `samples/runtime_glyph_map_seed.csv` | Runtime glyph observations and inferred base seeds. |
| `samples/runtime_kana_map.csv` | Generated kana runtime map with seeded consistency checks. |

## Removed

The stale combined/probe generations below were removed during cleanup because
they are superseded by v12 and gap66-v2:

```text
local/work/combined_chs_v1_* through combined_chs_v11_*
local/rebuilt/combined_chs_v1_* through combined_chs_v11_*
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
