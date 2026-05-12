# Chinese Patch Current Plan

This is the short, current-stage handoff. Older experiment details live in the
runtime observation docs, seed CSVs, local work summaries, and git history.
Mutable strategy and layout rules live in:

```text
docs/chs-strategy.md
docs/chs-layout-rules.md
```

## Current State

Current PPSSPP-ready broad build for tester/font review:

```text
local/rebuilt/combined_chs_v33_full_semibold18_extracted/
```

Current work root:

```text
local/work/combined_chs_v33_full_semibold18/
```

Underlying text baseline remains v23:

```text
local/work/combined_chs_v23_tutorial_usa_aligned_bitplane/
local/rebuilt/combined_chs_v23_tutorial_usa_aligned_bitplane_extracted/
```

The current v33 test build uses the multi-page full SemiBold 18px BMFont atlas,
preserves source `0x000a` hard breaks, reuses original Latin/symbol glyphs, and
integrates the first JP+EN translation refinement pass. It covers:

```text
DATA001/0003 boot/init UI
DATA001/0008 tutorial/objective overlay with all previous tutorial placeholders promoted from USA alignment
DATA001/0012 full local story sheet plus 3 estimate rows
DATA001/0015 full equipment/catalog table with readable equipment names
DATA001/0016 full UI/menu table
DATA001/0017 full help/manual table with queued manual body layouts reworked and JP key-icon cells reserved
DATA002/0065 name-input confirmation rows 82-84
```

The build has all 1637 currently parsed target rows and uses 1084 assigned CJK glyphs.
The confirmed low/high bitplane model provides a logical capacity of about 1782
14x14 glyph slots across the 11 physical JP font pages. v33 uses 561 physical
cells: 560 low-layer glyphs and 524 high-layer glyphs. Seven source button-icon
physical cells remain reserved across both layers, leaving about 684 usable
logical glyphs of headroom.

Current font/quantizer baseline:

```text
font: local/fonts/full-semibold-18.fnt
render mode: palette3
gray threshold: 176
2bpp mapping: 0..16 -> 0, 17..64 -> 1, 65..176 -> 2, 177..255 -> 3
```

Current parsed-row coverage report:

```text
local/work/chs_coverage_v33_full_semibold18/
parsed rows across current target tables: 1637
rows in current v33 build:               1637
rows not in current build:                  0
local draft rows not yet built:             0
estimate-only rows not yet built:           0
```

Current v32/v33 coverage and font corpus:

```text
local/work/chs_coverage_v32_refined_cjk_only_symbols/
rows in current v32 build:               1637 / 1637

local/work/chs_font_corpus_v3_refined_cjk_only/
current build generated-font chars:      1084 CJK ideographs
full translated candidate-bank CJK:      1430 CJK ideographs
```

Current v33 full-font check:

```text
local/fonts/full-semibold-18.fnt
font glyph entries:                     20971 across 9 pages
required current-build CJK missing:         0
```

Full parsed-target estimate:

```text
local/work/full_translation_glyph_estimate_v1/
parsed rows across current target tables: 1637
rows in legacy v19 build:                1116
rows with reviewed/local drafts:          1323
rows needing rough/generated estimate:     314
estimated full unique non-ASCII glyphs:   1020
old single-layer physical capacity:        891
old estimated over capacity:              ~129 glyphs
```

Actual translated/candidate-bank CJK requirement:

```text
local/work/actual_cjk_requirement_v1/
old parsed target rows:                  1637
new DATA003/1089 visible script rows:     851
translated or classified rows:           2488
missing rows:                               0
unique CJK required:                     1430
unique non-ASCII required:               1452
old single-layer usable CHS capacity:      884 (891 cells - 7 reserved icons)
old over usable capacity:                ~546 CJK glyphs
```

This replaces the older placeholder-heavy `1020` estimate for strategy work.
`DATA003/1089` is now counted as a visible script/story candidate bank because
the USA `DATA003/1089` extraction is readable and sectioned by `#start` rows.

## Active Findings

Confirmed runtime page bases now include:

```text
child 1  base 0x0100 / 0x0151
child 2  base 0x01a2 / 0x01f3
child 3  base 0x0244 / 0x0295
child 4  base 0x02e6 / 0x0337
child 5  base 0x0388 / 0x03d9
child 6  base 0x042a / 0x047b
child 7  base 0x04cc / 0x051d
child 8  base 0x056e / 0x05bf
child 9  base 0x0610 / 0x0661
child 10 base 0x06b2 / 0x0703
child 11 base 0x0754 / 0x07a5
```

Important caveat: alternate bases on the same child are alternate runtime code
windows, not extra storage. For example, child 9 / base `0x0610` and child 9 /
base `0x0661` both use the same 81 physical cells. The alternate bases improve
decoding and code routing, but do not increase glyph capacity.

Most recent page-base evidence:

```text
0x0689 -> 暗, child 9,  cell 40, base 0x0661
0x06b2 -> L,  child 10, cell 0,  base 0x06b2
0x0702 -> E,  child 10, cell 80, base 0x06b2
0x07a5 -> B,  child 11, cell 0,  base 0x07a5
0x07f5 -> H,  child 11, cell 80, base 0x07a5
```

Seed/reference files:

```text
samples/runtime_glyph_map_seed.csv
samples/runtime_kana_map.csv
local/work/page_base_candidates/
```

## Current Blockers

Glyph capacity is no longer the active blocker for the current parsed target
set after the bitplane model. The remaining blocker is translation quality and
context: v23 intentionally still includes rough placeholders outside the
tutorial table.

Fresh tutorial alignment:

```text
local/work/align_JP0008_USA0017_tutorial_full_v1.json
aligned DATA001/0008 rows:             66
previous tutorial placeholders:        55
tutorial placeholders with USA refs:   55

local/work/tutorial_usa_alignment_promotions_v1/
promoted tutorial placeholders:        55
remaining DATA001/0008 `粗译` rows:     0
```

Current rough markers in v23:

```text
DATA001/0012:   2
DATA002/0065: 161
total:        163
```

First tutorial anchor, now kept as glyph-table evidence:

```text
local/work/tutorial_placeholder_investigation_v1/
DATA001/0008 records 70-71 decode to the JP Movement tutorial.
20 new JP glyph labels were added to samples/runtime_glyph_map_seed.csv.
```

This anchor improved nearby tutorial placeholder decoding and helped confirm
that the USA `DATA001/0017` table is a same-record English reference for all
current `DATA001/0008` tutorial rows.

First-pass full JP glyph-table backup:

```text
local/work/jp_glyph_table_v1/
1782 confirmed logical low/high cells exported
246 seeded labels
144 inferred punctuation/Latin sequence labels
template-OCR guesses are review candidates only

local/work/jp_glyph_clear_pages_v1/ocr_joined_map.csv
Google OCR joined back to manifest; several blocks need alignment review before promotion.

local/work/jp_glyph_clear_pages_v1/ocr_reviewed_map.csv
1423 coded cells filled with explicit review status.

local/work/jp_glyph_table_v2/
human-edit CSVs and plain text grids split by priority/page; contact sheets use
the 2bpp page renders by default, and ANK `9x14` page geometry is explicit.
```

## Next Deliverable

Target: tester review of the v33 PPSSPP build and human translation review of
the slim packages:

```text
local/work/translation_review_slim_v1/
```

New text rules:

```text
Use generated CHS font only for CJK ideographs.
Reuse original Latin, digits, punctuation, symbols, and key icons whenever a source code is known.
Treat source 0x000a as either soft wrap or paragraph break by context.
For Stun Anchor-style equipment descriptions, the first JP break can be a visual wrap while the later break starts a new paragraph.
```

Continue replacing rough rows in controlled batches. Start with equipment,
help/manual, tutorial, and then `DATA002/0065` placeholders; keep the JP
glyph-table/OCR fallback for rows where no aligned USA text is recovered.

First autonomous refinement pass:

```text
local/work/translation_refine_v1/
DATA001_0015_refined.json                 672 equipment rows, 255 initially changed
help_tutorial_ui_refined.json             147 tutorial/UI/help candidate rows
story_data002_refined.json                194 story/DATA002 candidate rows
merged_target_sheets_all_fit_v1/          budget-fitted merged target sheets

v32 net changes after budget fitting:
DATA001/0008  61
DATA001/0012  34
DATA001/0015 254
DATA001/0016  55
DATA001/0017  22
DATA002/0065  93
total        519 changed rows
```

Manual layout note: the current DATA001/0017 manual/help text is included, and
the queued body records have explicit manual-layout overrides. These still need
PPSSPP page-by-page visual checks, but they are no longer the active known
layout gap.

See `docs/chs-strategy.md` for the recommended order and
`docs/chs-layout-rules.md` for current layout/name-input rules.

## Current Local Artifacts

Keep these current generated outputs:

```text
local/work/combined_chs_v23_tutorial_usa_aligned_bitplane/
local/rebuilt/combined_chs_v23_tutorial_usa_aligned_bitplane_extracted/
local/work/chs_coverage_v23_tutorial_usa_aligned_bitplane/
local/work/combined_chs_v24_bmfont_test/
local/rebuilt/combined_chs_v24_bmfont_test_extracted/
local/work/chs_coverage_v24_bmfont_test/
local/work/combined_chs_v25_semibold18_quantizer_test/
local/rebuilt/combined_chs_v25_semibold18_quantizer_test_extracted/
local/work/chs_coverage_v25_semibold18_quantizer_test/
local/work/combined_chs_v26_regular18_cutoff_test/
local/rebuilt/combined_chs_v26_regular18_cutoff_test_extracted/
local/work/chs_coverage_v26_regular18_cutoff_test/
local/work/combined_chs_v26_semibold18_cutoff_test/
local/rebuilt/combined_chs_v26_semibold18_cutoff_test_extracted/
local/work/chs_coverage_v26_semibold18_cutoff_test/
local/work/combined_chs_v27_semibold19_cutoff_test/
local/rebuilt/combined_chs_v27_semibold19_cutoff_test_extracted/
local/work/chs_coverage_v27_semibold19_cutoff_test/
local/work/combined_chs_v28_semibold18_cutoff16_test/
local/rebuilt/combined_chs_v28_semibold18_cutoff16_test_extracted/
local/work/chs_coverage_v28_semibold18_cutoff16_test/
local/work/full_current_target_sheets_v2/
local/work/tutorial_placeholder_investigation_v1/
local/work/tutorial_usa_alignment_promotions_v1/
local/work/v23_translation_review_pack/
local/work/equipment_chs_name_english_v1/
local/work/full_translation_glyph_estimate_v1/
local/work/name_input_chs_v1/
local/work/page_base_probe_help0017_gap66_v2/
local/rebuilt/page_base_probe_help0017_gap66_v2_extracted/
local/work/bitplane_probe_v1/
local/rebuilt/bitplane_probe_v1_extracted/
local/work/child11_high_base_probe_v1/
local/rebuilt/child11_high_base_probe_v1_extracted/
```

Older generated combined/probe builds were removed during cleanup. If a stale
local build is recreated, either document why it is useful or remove it.
