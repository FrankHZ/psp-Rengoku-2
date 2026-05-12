# Chinese Patch Current Plan

This is the short current-stage handoff. Strategy and layout rules live in:

```text
docs/chs-strategy.md
docs/chs-layout-rules.md
```

## Current Build

Current PPSSPP-ready broad build:

```text
local/rebuilt/combined_chs_v36_story_data003_extracted/
```

Current work root and coverage:

```text
local/work/combined_chs_v36_story_data003/
local/work/chs_coverage_v35_quality_translation/
```

Included targets:

```text
DATA001/0003 boot/init UI
DATA001/0008 tutorial/objective overlay
DATA001/0012 story/local story table slice
DATA001/0015 equipment/catalog names and descriptions
DATA001/0016 UI/menu table
DATA001/0017 help/manual table
DATA002/0065 name-input confirmation rows and related visible rows
DATA003/1089 first story-script patch pass
```

Current coverage:

```text
parsed rows across v35 target tables:    1637
DATA003/1089 story glyph rows patched:    610
total current text patch rows:           2247
assigned CJK glyphs:                     1361
physical cells used:                      721
reserved source logical cells:             91
logical headroom before source reserves:  421
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

local/work/translation_review_slim_v6_story/
entries: 610 DATA003/1089 story-script rows
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
v36 keeps the v35 quality pass and adds the first DATA003/1089 story-script
coverage pass:

```text
DATA001/0008 record 64: 熟练 -> 熟练度
DATA001/0015: 112 equipment name/description rows revised for semantic completeness
DATA001/0017: Skill Points wording normalized to 熟练度 in visible status/help text
DATA003/1089: 610 story glyph rows patched; reported illustrated page translated directly from JP
source hard paragraph breaks and generated soft wraps preserved
Latin, punctuation, symbols, and key-icon glyphs still reuse original source cells where known
```

DATA003/1089 still needs reviewer/tester pass. Some USA-aligned story chunks do
not map one-to-one to JP glyph rows, so v36 uses source-budget compression and a
small direct JP override for the reported page rather than treating the story
pass as final prose.

## Current Local Artifacts

The local workspace has been cleaned to the current keep list. See:

```text
docs/local-artifacts.md
```
