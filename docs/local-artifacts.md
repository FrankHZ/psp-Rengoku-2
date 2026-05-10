# Local Artifacts

Everything under `local/` is ignored by git. This file records which ignored
outputs are useful to keep around during the Chinese patch workflow and which
ones are disposable scratch.

## Preserve

These folders are useful local evidence or inputs for the current workflow:

| Path | Purpose |
| --- | --- |
| `local/work/mcd3_entries/` | Extracted JP archive entries used by text/font tools. |
| `local/work/mcd3_entries_usa/` | Extracted USA archive entries used for alignment. |
| `local/work/tdl_DATA001_0002/` | Extracted JP font TDL children. |
| `local/work/glyph_cells/` | Exported font cell crops and manifest for page/cell reasoning. |
| `local/work/rendered_mig_pages/` | Baseline rendered MIG pages for font comparison. |
| `local/work/dumped_textures/` | Runtime texture dumps used to compare static and in-game font pages. |
| `local/work/global_text_inventory/` | Current table inventory and translation queue. |
| `local/work/equipment_catalog_inventory/` | Equipment/catalog inventory report. |
| `local/work/story_chs_v1/` | Story readiness sheets and glyph-gap report. |
| `local/work/ui_help_chs_v1/` | Draft UI/help translation sheets. |
| `local/work/ui_help_chs_build_v1/` | UI/help selected build sheets and summary. |
| `local/work/equipment_chs_v1/` | Screenshot equipment slice sheets and summary. |
| `local/work/equipment_chs_v2/` | Expanded melee equipment sheet and summary. |
| `local/work/tutorial_chs_full_v1/` | Full tutorial sheet, stage config, and glyph assignments. |
| `local/work/combined_chs_v1_0008_0015_0016/` | Combined tutorial/equipment/UI build metadata. |
| `local/work/combined_chs_v2_0008_0015_0016_0017/` | Combined tutorial/equipment/UI/help build metadata using expanded runtime slot pools. |
| `local/work/font_compare/` | SimSun/local-font comparison report and contact sheet. |
| `local/work/font_level_analysis/` | Original font palette/index-level analysis. |
| `local/work/page_base_candidates/` | Unknown JP code scan and static MIG candidate matches. |
| `local/work/page_base_probe_v*/` | Multi-base probe manifests, stage configs, and marker previews. |
| `samples/runtime_kana_map.csv` | Generated full kana runtime map with seeded consistency checks. |
| `local/rebuilt/combined_chs_v1_0008_0015_0016_extracted/` | Current large PPSSPP-ready build. |
| `local/rebuilt/combined_chs_v2_0008_0015_0016_0017_extracted/` | Current larger PPSSPP-ready build with help/manual rows included. |
| `local/rebuilt/page_base_probe_v*_extracted/` | Multi-base PPSSPP probe builds. |
| `local/rebuilt/equipment_chs_v1_extracted/` | First equipment screenshot-slice build. |
| `local/rebuilt/equipment_chs_v1_generic_extracted/` | Same equipment slice through the generic builder. |
| `local/rebuilt/equipment_chs_v2_extracted/` | Expanded melee equipment build. |
| `local/rebuilt/tutorial_chs_full_v1_extracted/` | Full tutorial CHS build. |
| `local/rebuilt/ui_help_chs_v1_DATA001_0016_extracted/` | UI build probe. |
| `local/rebuilt/ui_help_chs_v1_DATA001_0017_extracted/` | Help/manual build probe. |

## Disposable

These are scratch outputs that can be removed after the information has been
copied into tracked docs or superseded by a current build:

- `local/work/archives_*`
- `local/work/verify_plus_entries/`
- `local/work/decode_offsets/`
- `local/work/decode_variants/`
- `local/work/dumped_textures_scaled_grid/`
- `local/work/rendered_mig_pages_abgr/`
- `local/work/rendered_mig_pages_bgra/`
- `local/work/rendered_mig_pages_contrast/`
- `local/work/rendered_mig_pages_rgba/`
- `local/work/rendered_mig_pages_scaled/`
- nested build/stage copies under current work roots, once their summary
  JSON/CSV files and `local/rebuilt/*_extracted/` outputs are preserved.

If PPSSPP is open, it may lock old `DATA*.BIN` scratch copies. Close PPSSPP
before removing locked ignored folders.
