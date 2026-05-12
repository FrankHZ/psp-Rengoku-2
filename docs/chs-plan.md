# Chinese Patch Current Plan

This is the short current-stage handoff. Strategy and layout rules live in:

```text
docs/chs-strategy.md
docs/chs-layout-rules.md
```

## Current Build

Current PPSSPP-ready broad build:

```text
local/rebuilt/combined_chs_v38_jp_equipment_story_extracted/
```

Current work root and coverage:

```text
local/work/combined_chs_v38_jp_equipment_story/
local/work/chs_coverage_v35_quality_translation/
```

Included targets:

```text
DATA001/0003 boot/init UI
DATA001/0008 tutorial/objective overlay
DATA001/0012 story/local story table slice
DATA001/0015 layered JP-first equipment/catalog names and descriptions
DATA001/0016 UI/menu table
DATA001/0017 help/manual table
DATA002/0065 name-input confirmation rows and related visible rows
DATA003/1089 JP-first story-script pass
```

Current coverage:

```text
parsed rows across v35 target tables:    1637
DATA003/1089 story glyph rows patched:    855
total current text patch rows:           2492
assigned CJK glyphs:                     1498
physical cells used:                      800
reserved source logical cells:             91
logical headroom before source reserves:  284
```

Current font/quantizer baseline:

```text
font: local/fonts/full-semibold-18.fnt
render mode: palette3
gray threshold: 176
2bpp mapping: 0..16 -> 0, 17..64 -> 1, 65..176 -> 2, 177..255 -> 3
```

Current human review package:

```text
local/work/translation_review_slim_v5/
entries: 1637
fields: id, category, chs, jp, en
changed from v4: 116 rows

local/work/translation_review_slim_v8_equipment_jp_first/
entries: 672 DATA001/0015 equipment rows
fields: id, category, jp, en, current_chs, chs_unshrunk, chs_shrunk, max_units, fit_note

local/work/translation_review_slim_v7_story_jp_first/
entries: 855 DATA003/1089 story-script rows
fields: id, category, chs, jp, en, fit_note
```

## Confirmed Runtime Model

The font uses 11 physical JP pages. Each physical 9x9 page provides a low and a
high logical code window, giving up to 1782 logical 14x14 cells.

Confirmed bases:

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

Alternate bases on the same child are code windows over the same physical cells,
not extra storage.

## Active Focus

Glyph capacity is not the active blocker for the current parsed target set.
v38 keeps the v37 story pass and adds a layered JP-first DATA001/0015 equipment
description pass:

```text
DATA001/0008 record 64: 熟练 -> 熟练度
DATA001/0015: review layer separates full JP-first translation from fitted build string
DATA001/0017: Skill Points wording normalized to 熟练度 in visible status/help text
DATA003/1089: 855 story glyph rows patched from reviewed JP decode
source hard paragraph breaks and generated soft wraps preserved
Latin, punctuation, symbols, and key-icon glyphs still reuse original source cells where known
```

DATA001/0015 and DATA003/1089 still need reviewer/tester pass for prose quality
and runtime line flow, but both now expose JP-first review context.

## Current Local Artifacts

The local workspace has been cleaned to the current keep list. See:

```text
docs/local-artifacts.md
```
