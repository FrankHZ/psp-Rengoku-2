# Chinese Patch Strategy

This file holds current project strategy. It is expected to change as the patch
workflow evolves.

## Build Strategy

Treat this as the baseline until tester/reviewer feedback says otherwise:

```text
local/rebuilt/combined_chs_v43_savedata_extracted/
```

The current build keeps the JP-first DATA003/1089 story pass, applies the story-name glossary, promotes reviewer-edited DATA001/0015 equipment text into layered review/runtime sheets, promotes the full local reviewer JSON package plus the latest help/manual and DATA002 UI feedback, keeps standalone attack attributes in English, keeps known DATA002 rough UI rows cleared, patches EBOOT runtime metadata strings for new saves, and adds a small `小方 oid Codex 汉化` title-background credit. Glyph capacity is not the active blocker after the confirmed low/high bitplane packing model.

Current build policy:

```text
use generated CHS font only for CJK ideographs
reuse source Latin, digits, punctuation, symbols, and key icons when known
patch EBOOT ASCII advance table so source halfwidth `1` uses width 7 like other halfwidth digits
patch EBOOT runtime save-list metadata templates and name-input prompt
patch `PSP_GAME/PIC1.PNG` title background with a small credit
reserve source cells for every reused symbol code
preserve explicit paragraph/list hard breaks
let tooling add soft visual wraps for long Chinese lines
use reviewed JP as primary source for DATA003/1089 story text
separate full review translation from fitted build text for equipment names/descriptions
apply the story glossary before building DATA003/1089
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

For cramped equipment names and descriptions, maintain two layers:

```text
chs_unshrunk: JP-first/reviewer full-meaning translation for reviewer quality checks
chs_shrunk: fitted runtime string derived from the full layer and source slot budget
```

Examples:

```text
偽竜ファング / Faux Dragon Fang -> preserve 偽/Faux, e.g. 伪龙牙爪
熟練度 / Skill Points in this game context -> 熟练度
```

Avoid `技能点` for the help/manual status category unless a reviewer explicitly
decides a specific row is about spendable points rather than proficiency.

Story proper names must pass through `docs/chs-glossary.json`. Use Divine Comedy forms where applicable, e.g. `ベアトリーチェ`/Beatrice -> `贝雅特丽齐`, `ヴェルギリウス`/Virgil -> `维吉尔`, `ダンテ`/Dante -> `但丁`, `スタティウス`/Statius -> `斯塔提乌斯`, and `ルシファー`/Lucifer -> `路西法`.

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

Current v43 usage:

```text
assigned CJK glyphs:                   1524
physical cells used:                    846
low-layer glyphs:                       746
high-layer glyphs:                      778
reserved source logical cells:          153
logical headroom before source reserves: 258
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
build needs 1524 assigned CJK glyphs after promoting the v43 reviewer feedback package.

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
block02_child00_codeANK9x14_00_0_low cell 17: source halfwidth `1` bitmap stays original; alignment is handled by the EBOOT ASCII advance table (`1` width 5 -> 7).
block03_child01_codeJAP14x14_00__high: digits 0-9 and letters A-E are fullwidth glyphs, mapped as ０-９ and Ａ-Ｅ.
block06_child02_codeJAP14x14_02__low: letters F-Z and a-z are fullwidth glyphs, mapped as Ｆ-Ｚ and ａ-ｚ.
block08_child03_codeJAP14x14_04__low: contains reusable key glyphs for L/R/O/X/triangle/square.
block12_child05_codeJAP14x14_08__low: 0x03b6 is U+339C ㎜.
block23/block24 child11 high/low: blank/unknown cells are classified as unused for now.
current unresolved blank/unknown used cells: 0.
```

## Human Review

Current review package:

```text
local/work/translation_review_slim_v12_reviewed_all/
all current reviewer-facing rows: 2492 entries
fields: id, category, chs, jp, en plus equipment layer fields where applicable
runtime-fit overrides are documented in the package

translation_reviewed/
local reviewer-edited JSON inputs, tracked by its own local git repo
```

Current v43 pass:

```text
DATA001/0015: reviewer-edited current_chs promoted to chs_unshrunk/chs_shrunk layers
DATA001/0016: standalone attack attributes use English labels matching JP/EN: GRAPPLE, SLASH, IMPACT, QUANTUM, BULLET, HEAT
DATA001/0017: visible Skill Points wording normalized to 熟练度
DATA001/0016 records 142-144: upgrade stat abbreviations use source labels En/He/Pr
DATA002/0065: standalone GRAPPLE label restored to English; DATA002 rough UI/gallery/sound rows cleared
DATA002/0065: latest missing UI/gallery/sound rows promoted, including `开场` and `结局`
DATA001/0017: latest help/manual layout feedback promoted
DATA001/0012 and DATA003/1089: latest runtime-fit handoff applied without mixing fitted strings into reviewed JSON
DATA003/1089: JP-first story-script pass with glossary-normalized story names
EBOOT: new-save metadata templates and the name-input OSK prompt are patched in decrypted EBOOT runtime strings
PSP_GAME/PIC1.PNG: title background has a small `小方 oid Codex 汉化` credit
translation_reviewed/: local-only nested git repo for reviewer JSON inputs
local/work/translation_review_slim_v12_reviewed_all/: all-file reviewed package, 2492 entries
runtime-fit overrides: source-slot shortening for a small set of long reviewed rows; reviewer text is retained in the review pack
```

Known remaining external/system text:

```text
PSP savedata list metadata is written into savedata PARAM.SFO. v43 patches the EBOOT templates used for new saves.
Existing savedata PARAM.SFO files can be patched separately with tools/patch_savedata_sfo.py.
The PSP OSK title/prompt, e.g. 名前を入力してください, is outside the DATA001/002/003 text-table path but is patched in the decrypted EBOOT runtime strings.
```

Recommended next loop:

```text
1. Collect reviewer corrections in the local-only `translation_reviewed/` repo, then promote with `tools/promote_reviewed_translation_package.py`.
2. Promote corrections into translation_refine_v1 target sheets.
3. Run coverage and CJK requirement reports.
4. Build a new PPSSPP artifact only after enough corrections accumulate.
```
