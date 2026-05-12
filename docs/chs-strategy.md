# Chinese Patch Strategy

This file holds current project strategy. It is expected to change as the patch
workflow evolves.

## Build Strategy

Treat this as the baseline until tester/reviewer feedback says otherwise:

```text
local/rebuilt/combined_chs_v38_jp_equipment_story_extracted/
```

The current build keeps the v37 JP-first DATA003/1089 story pass and replaces
DATA001/0015 equipment descriptions with a layered JP-first pass. Glyph capacity
is not the active blocker after the confirmed low/high bitplane packing model.

Current build policy:

```text
use generated CHS font only for CJK ideographs
reuse source Latin, digits, punctuation, symbols, and key icons when known
reserve source cells for every reused symbol code
preserve explicit paragraph/list hard breaks
let tooling add soft visual wraps for long Chinese lines
use reviewed JP as primary source for DATA003/1089 story text
separate full review translation from fitted build text for equipment descriptions
```

Do not assume alternate runtime bases add storage. Bases like child 9 /
`0x0610` and child 9 / `0x0661` are alternate code windows over the same
physical 81 cells.

## Translation Policy

Use Simplified Chinese for tutorial, UI, help, and ordinary prose.

Now that the build has headroom, translation quality is more important than
aggressive compression:

```text
preserve meaningful modifiers and proper-name flavor
preserve equipment function, construction, behavior, and gameplay effect
avoid opaque consonant-code abbreviations
keep English only for actual proper nouns/model names/stylized names when readable
compress only after the core meaning is intact
```

For cramped equipment descriptions, maintain two layers:

```text
chs_unshrunk: JP-first full-meaning translation for reviewer quality checks
chs_shrunk: fitted runtime string derived from the full layer and source slot budget
```

Examples:

```text
偽竜ファング / Faux Dragon Fang -> preserve 偽/Faux, e.g. 伪龙牙爪
熟練度 / Skill Points in this game context -> 熟练度
```

Avoid `技能点` for the help/manual status category unless a reviewer explicitly
decides a specific row is about spendable points rather than proficiency.

Runtime user input such as the player name is a variable token. Treat it as a
wildcard, for example `@GRAM@`/`#GRAM#`, not as literal translatable text.

### Optional Story References

The Japanese wiki at https://w.atwiki.jp/rengoku2/ can be used only as an
optional future reference for story and boss dialogue checks. For example,
https://w.atwiki.jp/rengoku2/pages/11.html includes boss dialogue/event text.
Do not treat wiki text as current translation provenance or as a patch source;
current story translations are based on local JP extraction plus local USA
release alignment/extraction.

## Glyph Capacity

Confirmed model:

```text
physical JP pages:       11
cells per JP page:       81
logical layers:           2
logical capacity:      1782
```

Current v38 usage:

```text
assigned CJK glyphs:                   1498
physical cells used:                    800
low-layer glyphs:                       734
high-layer glyphs:                      764
reserved source logical cells:           91
logical headroom before source reserves: 284
font: local/fonts/full-semibold-18.fnt
quantization: palette3, threshold 64, gray threshold 176
2bpp convention: 0 background, 1 light gray, 2 deep gray, 3 white
source values 1..16: dropped to background
```

Actual translated/candidate-bank requirement:

```text
artifact: local/work/actual_cjk_requirement_v1/
parsed target rows:                   1637
DATA003/1089 visible script rows:      851
translated/classified rows:           2488
missing rows:                            0
unique CJK required:                  1430
unique non-ASCII required:            1452
```

The full candidate-bank number remains useful for planning. The current broad
build needs 1498 assigned CJK glyphs after the JP-first story and equipment passes.

## JP Glyph Table Backup

Current JP decode source:

```text
local/ocr_reviewed/
local/work/full_jp_text_decode_v1/
```

Use the reviewed glyph table as a backup when aligned USA text is unavailable.
OCR output should be treated as reviewed evidence, not as automatic truth.

Current watch notes:

```text
block02_child00_codeANK9x14_00_0_low: Windows-1252-style symbols reviewed; remaining blanks are intentional blank/control cells.
block08_child03_codeJAP14x14_04__low: contains reusable key glyphs for L/R/O/X/triangle/square.
block12_child05_codeJAP14x14_08__low: 0x03b6 is U+339C ㎜.
block23/block24 child11 high/low: blank/unknown cells are classified as unused for now.
current unresolved blank/unknown used cells: 0.
```

## Human Review

Current review package:

```text
local/work/translation_review_slim_v5/
total built rows: 1637
fields: id, category, chs, jp, en
changed from v4: 116 rows

local/work/translation_review_slim_v8_equipment_jp_first/
DATA001/0015 equipment rows: 672
fields: id, category, jp, en, current_chs, chs_unshrunk, chs_shrunk, max_units, fit_note

local/work/translation_review_slim_v7_story_jp_first/
DATA003/1089 story rows: 855
fields: id, category, chs, jp, en, fit_note
```

v35 quality pass:

```text
DATA001/0008 record 64: 熟练度 title correction
DATA001/0015: 112 equipment name/description revisions
DATA001/0017: visible Skill Points wording normalized to 熟练度
review pack v5 regenerated from the v35 build
```

v37 story pass:

```text
DATA003/1089: JP-first story-script pass
855 reviewed JP glyph rows patched
old USA alignment retained only as reviewer reference context
rows are fitted to JP source slot budgets
```

v38 equipment pass:

```text
DATA001/0015: JP-first equipment description layer split
336 names and 336 descriptions exported
313 unique JP description clauses covered
unknown JP clauses: 0
runtime build uses chs_shrunk; reviewer pack keeps chs_unshrunk
```

Recommended next loop:

```text
1. Collect reviewer corrections against translation_review_slim_v8_equipment_jp_first and translation_review_slim_v7_story_jp_first.
2. Promote corrections into translation_refine_v1 target sheets.
3. Run coverage and CJK requirement reports.
4. Build a new PPSSPP artifact only after enough corrections accumulate.
```
