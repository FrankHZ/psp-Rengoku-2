# Local Artifacts

Everything under `local/` is ignored by git. Keep ignored outputs only when
they are current evidence, current build inputs, or PPSSPP-ready deliverables.
Remove superseded builds after their results are copied into tracked docs.

## Current Keep List

Current PPSSPP build:

| Path | Purpose |
| --- | --- |
| `local/rebuilt/combined_chs_v36_story_data003_extracted/` | Current PPSSPP-ready broad CHS build plus first DATA003/1089 story patch pass. |
| `local/work/combined_chs_v36_story_data003/` | Current build metadata, stage config, glyph assignment, text payloads, and previews. |
| `local/work/chs_coverage_v35_quality_translation/` | Current parsed-row and glyph-headroom coverage report. |

Current text/review inputs:

| Path | Purpose |
| --- | --- |
| `local/work/mcd3_entries/` | Extracted JP archive entries used by text/font tools. |
| `local/work/mcd3_entries_usa/` | Extracted USA archive entries used for alignment. |
| `local/work/tdl_DATA001_0002/` | Extracted JP font TDL children. |
| `local/work/global_text_inventory/` | Table inventory and translation queue. |
| `local/work/full_translation_glyph_estimate_v1/` | Parsed target-row estimate and queue reports. |
| `local/work/actual_cjk_requirement_v1/` | Actual translated/candidate-bank CJK requirement report. |
| `local/work/full_jp_text_decode_v1/` | JP decode output built from the reviewed glyph table. |
| `local/work/translation_refine_v1/` | Current JP+EN refinement packs and merged target sheets. |
| `local/work/translation_review_slim_v5/` | Current human review package, one concise JSON per category. |
| `local/work/translation_review_slim_v6_story/` | Concise DATA003/1089 story-script review pack for the v36 story pass. |

Current font artifacts:

| Path | Purpose |
| --- | --- |
| `local/fonts/full-semibold-18.fnt`, `local/fonts/full-semibold-18_*.png` | Current default full CJK SemiBold 18px BMFont atlas. |
| `local/fonts/corpus-semibold-18.fnt`, `local/fonts/corpus-semibold-18_0.png` | Smaller corpus-only fallback atlas. |
| `local/work/chs_font_corpus_v3_refined_cjk_only/` | Current CJK-only corpus used for external font generation. |
| `local/work/font_compare/` | Current font-render comparison output. |
| `local/ocr_reviewed/` | Human-reviewed OCR text grids used as the JP glyph-map source. |

Older one-off font experiments were removed. Regenerate a comparison font only
when a new visual test is needed.

## Cleanup Rule

Do not keep old probe/build directories by habit. If a new ignored local output
is still useful, add it here with a one-line purpose. If it only served a past
experiment, delete it after the result is captured in docs or git history.
