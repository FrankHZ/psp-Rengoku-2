# Chinese Patch Strategy

This file holds current project strategy. It is expected to change as the patch
workflow evolves.

## Build Strategy

Treat this as the baseline until tester/reviewer feedback says otherwise:

```text
local/rebuilt/combined_chs_v35_quality_translation_extracted/
```

The current build covers all 1637 parsed target rows. Glyph capacity is not the
active blocker for that target set after the confirmed low/high bitplane packing
model.

Current build policy:

```text
use generated CHS font only for CJK ideographs
reuse source Latin, digits, punctuation, symbols, and key icons when known
reserve source cells for every reused symbol code
preserve explicit paragraph/list hard breaks
let tooling add soft visual wraps for long Chinese lines
wait for reviewer/tester feedback before the next broad rebuild
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

Current v35 usage:

```text
assigned CJK glyphs:                   1086
physical cells used:                    601
low-layer glyphs:                       533
high-layer glyphs:                      553
reserved source logical cells:           91
usable logical headroom:          about 605
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

The full candidate-bank number remains useful for planning, but the current
broad build only needs the 1084 assigned CJK set.

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
```

v35 quality pass:

```text
DATA001/0008 record 64: 熟练度 title correction
DATA001/0015: 112 equipment name/description revisions
DATA001/0017: visible Skill Points wording normalized to 熟练度
review pack v5 regenerated from the v35 build
```

Do not rush a new PPSSPP build while reviewer/tester feedback is still pending
unless the feedback identifies a blocking runtime correctness bug.

Recommended next loop:

```text
1. Collect reviewer corrections against translation_review_slim_v5.
2. Promote corrections into translation_refine_v1 target sheets.
3. Run coverage and CJK requirement reports.
4. Build a new PPSSPP artifact only after enough corrections accumulate.
```
