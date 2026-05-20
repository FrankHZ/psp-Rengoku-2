# Local Artifacts

Everything under `local/` is ignored by git. Keep ignored outputs only when
they are current evidence, current build inputs, or PPSSPP-ready deliverables.
Remove superseded builds after their results are copied into tracked docs.

## Current Keep List

Current PPSSPP build:

| Path | Purpose |
| --- | --- |
| `local/rebuilt/combined_chs_v43_savedata_extracted/` | Current PPSSPP-ready broad CHS build with promoted reviewer feedback, reviewed equipment text, story glossary names, English attack attributes, DATA002 rough UI labels cleared, EBOOT halfwidth `1` advance patch, EBOOT new-save metadata string patches, translated `PIC0.PNG`, and the PSP shell `PIC1.PNG` upper-left credit. It intentionally has no in-game title-texture credit patch. |
| `local/rebuilt/combined_chs_v43_savedata.iso` | Current ISO built from the v43 extracted folder by `tools/build_psp_iso.py`; its high-level ISO9660/UMD layout follows the PPSSPP-tested v41/v40 path. |
| `local/rebuilt/combined_chs_v43_title_logo_ank3_retry_extracted/`, `local/rebuilt/combined_chs_v43_title_logo_ank3_retry.iso` | Latest local title-credit experiment. It patches `DATA001/0004` `tlogo` with `小方 oid Codex 汉化`, using the CHS SemiBold BMFont for CJK and original ANK glyphs for Latin. PPSSPP shows it, but the visual quality is not final, so it is not the releasable baseline. |
| `local/work/combined_chs_v43_savedata/` | Current build metadata, stage config, glyph assignment, text payloads, and previews. |
| `local/work/chs_coverage_v43_savedata/` | Current parsed-row and glyph-headroom coverage report. |
| `local/work/eboot_width_patch/` | Current EBOOT work area. `EBOOT_DEC_WIDTH7_SAVECHS.BIN` is the decrypted EBOOT with ASCII `1` advance patched from 5 to 7 plus new-save metadata and OSK prompt strings; broad builds copy it into `PSP_GAME/SYSDIR/EBOOT.BIN` when present. |
| `local/work/title_credit_probe/` | Ignored title-texture extraction/probe outputs and PNG previews from the texture search. `rebuilt_pic1_credit.png` is the current source for the PSP shell `PIC1.PNG` credit used by the releasable v43 ISO. `tback` probes proved visible but too dark/filter-affected; the latest in-game experiment targets `DATA001/0004` TDL child `tlogo` instead. Intermediate test ISOs were removed; some extracted folders may remain as local evidence. |
| `local/tools/deceboot_0_3/` | Local PSP EBOOT decryptor used to produce the decrypted ELF for the width-table patch. |

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
| `local/work/translation_refine_v1/` | Current JP+EN refinement packs and merged target sheets. Keep `merged_target_sheets_all_fit_v1/` plus `merged_target_sheets_v41_reviewed_all/`; older intermediate target-sheet directories were removed. |
| `local/work/translation_review_slim_v12_reviewed_all/` | Current all-file review package promoted from `translation_reviewed/`; includes 2492 entries, 244 changed/promoted rows, and runtime-fit notes. |
| `translation_reviewed/` | Local reviewer-edited input packs; promote into generated work sheets, but do not treat as build output. |

Current font artifacts:

| Path | Purpose |
| --- | --- |
| `local/fonts/full-semibold-18.fnt`, `local/fonts/full-semibold-18_*.png` | Current default full CJK SemiBold 18px BMFont atlas. |
| `local/fonts/corpus-semibold-18.fnt`, `local/fonts/corpus-semibold-18_0.png` | Smaller corpus-only fallback atlas. |
| `local/work/chs_font_corpus_v3_refined_cjk_only/` | Current CJK-only corpus used for external font generation. |
| `local/work/font_compare/` | Current font-render comparison output. |
| `local/work/font_digit1_probe/` | Retired evidence from the abandoned ANK halfwidth `1` bitmap experiment; bitmap edits alone did not fix advance/spacing. |
| `local/ocr_reviewed/` | Human-reviewed OCR text grids used as the JP glyph-map source. |

Older one-off font experiments were removed. Regenerate a comparison font only
when a new visual test is needed.

## Cleanup Rule

Do not keep old probe/build directories by habit. If a new ignored local output
is still useful, add it here with a one-line purpose. If it only served a past
experiment, delete it after the result is captured in docs or git history.
