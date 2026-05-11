# Chinese Patch Current Plan

This is the short, current-stage handoff. Older experiment details live in the
runtime observation docs, seed CSVs, local work summaries, and git history.
Mutable strategy and layout rules live in:

```text
docs/chs-strategy.md
docs/chs-layout-rules.md
```

## Current State

Current PPSSPP-ready broad build:

```text
local/rebuilt/combined_chs_v23_tutorial_usa_aligned_bitplane_extracted/
```

Current work root:

```text
local/work/combined_chs_v23_tutorial_usa_aligned_bitplane/
```

This build covers:

```text
DATA001/0003 boot/init UI
DATA001/0008 tutorial/objective overlay with all previous tutorial placeholders promoted from USA alignment
DATA001/0012 full local story sheet plus 3 estimate rows
DATA001/0015 full equipment/catalog table with readable equipment names
DATA001/0016 full UI/menu table
DATA001/0017 full help/manual table with queued manual body layouts reworked and JP key-icon cells reserved
DATA002/0065 name-input confirmation rows 82-84
```

The build has all 1637 currently parsed target rows and uses 1033 assigned CHS glyphs.
The confirmed low/high bitplane model provides a logical capacity of about 1782
14x14 glyph slots across the 11 physical JP font pages. v23 uses 554 physical
cells: 553 low-layer glyphs and 480 high-layer glyphs. Seven source button-icon
cells remain reserved, leaving about 742 usable logical glyphs of headroom.

Current parsed-row coverage report:

```text
local/work/chs_coverage_v23_tutorial_usa_aligned_bitplane/
parsed rows across current target tables: 1637
rows in current v23 build:               1637
rows not in current build:                  0
local draft rows not yet built:             0
estimate-only rows not yet built:           0
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
child 11 base 0x0754 provisional
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

## Next Deliverable

Target: PPSSPP-check v23, then continue replacing rough rows in controlled
batches. Start with `DATA002/0065` placeholders; keep the JP glyph-table/OCR
fallback for rows where no aligned USA text is recovered.

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
```

Older generated combined/probe builds were removed during cleanup. If a stale
local build is recreated, either document why it is useful or remove it.
