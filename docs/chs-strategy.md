# Chinese Patch Strategy

This file holds current project strategy. It is expected to change as the patch
workflow evolves.

## Build Strategy

Prioritize PPSSPP-ready builds that validate a broad slice of the game. The
current broad build should be treated as the baseline until superseded:

```text
local/rebuilt/combined_chs_v33_full_semibold18_extracted/
```

Glyph capacity is no longer the blocker for the current parsed target set after
bitplane packing. Do not assume alternate runtime bases add storage; bases like
child 9 / `0x0610` and child 9 / `0x0661` are alternate code windows over the
same physical 81 cells.

When capacity is tight, prefer:

```text
reuse existing ASCII and preserved button/input symbols
keep readable equipment names; do not use opaque consonant-code abbreviations
keep stylized equipment names in English only when the actual name fits
use shorter Simplified Chinese wording
split full-story and full-catalog deliverables when needed
```

## Translation Policy

Use Simplified Chinese for tutorial, UI, help, and ordinary prose.

For equipment names, prefer a hybrid policy:

```text
keep actual English proper nouns/model names/stylized names only when they fit
translate short generic functional names when the glyph cost is reasonable
prefer readable Chinese names over opaque ASCII abbreviations
keep descriptions concise and Chinese unless capacity requires an English mode
```

Examples that should usually stay English:

```text
C-K.O.D
SAA Magnum 88
Raijin
```

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

Legacy single-layer broad build before bitplane packing:

```text
assigned glyphs: 847
physical capacity: 891
reserved source icon cells: 7
raw headroom: about 44
usable CHS headroom: about 37
```

Packed font-layer finding:

```text
clean runtime observations: 18 distinct rendered pages
bitplane mapping: CLUT 676a3b4e = low two bits, CLUT 28998f6f = high two bits
logical capacity: 11 JP pages * 81 cells * 2 layers = 1782 cells
```

This likely changes the glyph-capacity strategy. The old 891-cell model is the
physical-page limit, but the original font textures pack two logical glyph pages
into low/high 2-bit planes. A layer-preserving renderer now exists, and the
current probe build is:

```text
local/rebuilt/bitplane_probe_v1_extracted/
```

The probe was confirmed in PPSSPP:

```text
P1 ABCDEF confirmed
P2 GHIJKL confirmed
P3 MNOP confirmed
```

The focused help/manual probe confirmed the remaining child 11 high window:

```text
local/rebuilt/child11_high_base_probe_v1_extracted/
low base:  0x0754
high base: 0x07a5 (= 0x0754 + 0x51)
observed: 0754=A, 07A5=B, 0755=C, 07A6=D, 0774=E, 07C5=F, 07A4=G, 07F5=H
```

The broad CHS composer now has a bitplane assignment model. v20 was PPSSPP
checked and looked good. The current PPSSPP-ready build is v33, which uses the
multi-page full SemiBold 18px BMFont atlas, restores source `0x000a`
hard-break layout, reuses original Latin/symbol glyphs, and integrates the
first JP+EN autonomous translation refinement pass:

```text
current artifact: local/work/combined_chs_v33_full_semibold18/
logical assigned glyphs:           1084 CJK ideographs
logical capacity model:            1782
physical cells used:                561
low-layer glyphs:                   560
high-layer glyphs:                  524
usable logical headroom:            about 684 after reserved icon cells
font:                              local/fonts/full-semibold-18.fnt
current quantization default:       palette3, threshold 64, gray threshold 176
2bpp value convention:              0 background, 1 light gray, 2 deep gray, 3 white; source 1..16 is dropped
hard-break rule:                    source 0x000a count is preserved unless draft has explicit newlines
symbol rule:                        generated CHS font is CJK-only; Latin/punctuation/symbols reuse source codes
```

Full parsed-target estimate:

```text
artifact: local/work/full_translation_glyph_estimate_v1/
parsed rows:                         1637
legacy v19 build rows:               1116
reviewed/local draft rows:           1323
rough/generated estimate rows:        314
estimated full non-ASCII glyphs:     1020
estimated over current capacity:     ~129
```

Actual translated/candidate-bank requirement:

```text
artifact: local/work/actual_cjk_requirement_v1/
old parsed target rows:              1637
DATA003/1089 visible script rows:     851
translated/classified rows:          2488
missing rows:                           0
unique CJK required:                 1430
unique non-ASCII required:           1452
old single-layer usable CHS capacity: 884
old over usable capacity:            ~546
```

Use this actual measurement, not the older placeholder-heavy `1020` estimate,
when planning glyph-reduction strategy. `DATA003/1089` remains a script/story
bank, not part of v19, but it now has readable USA extraction and a local CHS
translation estimate for visible non-command rows.

Current parsed-row coverage report:

```text
artifact: local/work/chs_coverage_v32_refined_cjk_only_symbols/
parsed rows:                         1637
rows in current build:               1637
rows not in current build:              0
local draft rows not built:             0
estimate-only rows not built:           0
```

Latest full-font coverage check:

```text
artifact: local/work/chs_coverage_v33_full_semibold18/
parsed rows:                         1637
rows in current build:               1637
rows not in current build:              0
full BMFont glyph entries:          20971 across 9 pages
required current-build CJK missing:     0
```

Quality caveat: v23 still includes rough rows outside the tutorial table. The
previous v22 all-target sheet included 314 estimate rows; 66 of those were
automatically fitted to original slot budgets, recorded at:

```text
local/work/full_current_target_sheets_v2/fit_adjustments.csv
```

The first autonomous JP+EN refinement pass is merged into v33 through:

```text
local/work/translation_refine_v1/merged_target_sheets_all_fit_v1/
net changed rows after slot-budget fitting: 519
```

Slim human-review packages for the current refinement pass:

```text
local/work/translation_review_slim_v1/
equipment.json:        672 entries
help_tutorial_ui.json: 147 entries
story_data002.json:    194 entries
summary.json:         1013 total entries
```

Tutorial USA alignment:

```text
artifact: local/work/align_JP0008_USA0017_tutorial_full_v1.json
same-record DATA001/0008 alignments:  66
previous tutorial placeholders:       55
with USA reference:                   55

artifact: local/work/tutorial_usa_alignment_promotions_v1/
promoted rows:                        55
remaining DATA001/0008 `粗译`:         0
```

The older `placeholder_investigation_v1` report used a stale alignment source
and should not be used to conclude that DATA001/0008 lacks English references.
For the current build, remaining rough markers are in DATA001/0012 and
DATA002/0065.

First tutorial anchor:

```text
artifact: local/work/tutorial_placeholder_investigation_v1/
anchor rows: DATA001/0008 records 70-71
result: JP Movement tutorial decoded from source codes
new seed labels: 20 added to samples/runtime_glyph_map_seed.csv
```

Keep this as local glyph-table evidence. The wider same-record USA alignment is
now the primary source for `DATA001/0008` tutorial replacement.

### JP Glyph Table Backup

If aligned USA text is unavailable for a placeholder group, use the completed
MIG page/base work to build a full JP glyph table:

```text
1. Render/crop every confirmed low/high logical cell from the original MIG pages.
2. OCR or manually label each cell once, keyed by child/base/layer/cell/code.
3. Merge OCR output with confirmed seed maps and reject conflicts by context.
4. Re-decode placeholder source rows to Japanese.
5. Translate from decoded JP, using the USA release only when alignment is found later.
```

This is slower than alignment, but it is now practical because the physical page
set, low/high layers, and sampled base windows are confirmed. Treat OCR output
as evidence requiring review, not as an automatically trusted translation
source.

First-pass artifact:

```text
local/work/jp_glyph_table_v1/
logical cells exported: 1782
seeded labels: 246
inferred punctuation/Latin sequence labels: 144
template-OCR guesses: review only, not confirmed
contact sheets: local/work/jp_glyph_table_v1/contact_sheets/
```

The local template OCR uses Windows bitmap/font rendering as a rough recognizer.
It is useful for triage and contact-sheet review, but several seeded
punctuation/kana cells score poorly or receive wrong guesses, so only
`status=seeded` rows should be treated as confirmed. `status=inferred_sequence`
rows are low-risk punctuation/Latin sequence labels, but remain distinct from
PPSSPP-confirmed seeds until visual review promotes them.

External OCR pass:

```text
local/work/jp_glyph_clear_pages_v1/ocr.csv
local/work/jp_glyph_clear_pages_v1/ocr_joined_map.csv
local/work/jp_glyph_clear_pages_v1/ocr_reviewed_map.csv
local/work/jp_glyph_clear_pages_v1/ocr_summary.json
```

The Google OCR block output is useful, especially for full 81-cell kanji
blocks, but it is not uniformly cell-aligned: some symbol/kana blocks omit or
insert glyphs, causing downstream shifts. Use `ocr_joined_map.csv` together
with `seed_match` and the block length fields before promoting OCR results into
the trusted glyph map.

`ocr_reviewed_map.csv` is the safer working file. It fills 1423 coded cells and
keeps review status separate:

```text
confirmed_seed:              246
reviewed_ocr_full_block:     671
reviewed_ocr_partial_block:   33
ocr_prefix_candidate:        376
inferred_sequence:            97
needs_alignment_review:      482
blank_or_missing_ocr:        129
```

Use `confirmed_seed`, `reviewed_ocr_full_block`, and
`reviewed_ocr_partial_block` first. Treat `ocr_prefix_candidate` as useful but
not final, and do not promote `needs_alignment_review` without per-cell visual
alignment.

Reviewer package:

```text
local/work/jp_glyph_table_v2/
local/work/jp_glyph_table_v2/human_review/
```

Human reviewers should edit `reviewer_char` and leave `final_char` untouched so
their corrections can be merged cleanly. The package includes priority CSVs and
one CSV plus one plain text grid per page/block. The ANK page is explicitly
marked as `14 x 9` cells of `9x14` pixels; JP pages are `9 x 9` cells of
`14x14` pixels. Contact sheets use the `original_pages_2bpp/` renders as the
default visual source.

Human-reviewed OCR text grids are now available at:

```text
local/ocr_reviewed/
```

Current usage research output:

```text
local/work/jp_glyph_usage_research_v1/
```

High-confidence usage counts in that report come from extracted JP
`glyph_codes` records only. Raw little-endian u16 sightings are included for
context but are noisy, especially for low ASCII/ANK codes. Current watch-block
findings:

```text
block01_child00_codeANK9x14_00_0_high: no confirmed runtime code window; no extracted usage.
block02_child00_codeANK9x14_00_0_low: reviewed against Windows-1252-style symbols; remaining blank cells are confirmed intentional blank/control cells, not glyph-ID work.
block03_child01_codeJAP14x14_00__high: reviewed against the JIS-style symbol table; 0x0166 is confirmed blank/reserved, while 0x015f is a literal white square and 0x0161 is a literal white triangle.
block08_child03_codeJAP14x14_04__low: row 8 contains reusable original key glyphs at 0x0283-0x028a (L/L/R/R/O/X/triangle/square); keep those cells reserved even though the extracted records do not currently reference them directly.
block12_child05_codeJAP14x14_08__low: 0x03b6 is U+339C `㎜` and is used in extracted glyph-code records.
block23_child11_codeJAP14x14_20__high and block24_child11_codeJAP14x14_20__low: blank/unknown cells are currently classified as unused.
current unresolved blank/unknown used cells: 0.
```

The follow-up special-symbol contact sheets in
`local/work/jp_glyph_usage_research_v1/marked_contact_sheets_next_v2/` were
human-confirmed. The confirmed used symbols are:

```text
0x011e ／  0x013b ＋  0x013c −  0x013e ×
0x02ac Ω   0x02ad α   0x02ae β   0x02af γ
0x027a ™   0x027b “   0x027c ”   0x0282 €
0x0327 Ⅱ   0x0328 Ⅲ   0x0329 Ⅳ   0x032a Ⅴ
0x032c Ⅶ   0x032d Ⅷ   0x032e Ⅸ   0x032f Ⅹ
0x03b6 ㎜
```

Equipment-name result:

```text
legacy single-layer broad unique glyphs:   849
v13 with aggressive ASCII abbreviations:   773  (-76), superseded as unreadable
v14 with readable equipment names:         849
v15 with manual layout pass:               851
v16 with attack-page button hints:         855
v17 preserving JP key-icon glyph codes:    847
v18 reserving JP key-icon source cells:    847  (7 protected cells)
equipment sheet unique glyphs:             554
```

`tools/make_equipment_name_english_variant.py` now keeps actual English names
only when they fit the original run budget; otherwise it preserves the existing
readable Chinese name. Do not reintroduce generated consonant-code abbreviations
like `GLDT` or `DNT`.

## Next Deliverable

Target: keep readable equipment names while deciding how to split or compress
the 1430-CJK full candidate-bank requirement.

Recommended order:

```text
1. PPSSPP-check v23 as the current all-target tutorial-aligned build.
2. Review estimate rows in controlled batches, starting with DATA002/0065 placeholders.
3. If USA alignment remains empty, build the JP glyph OCR table and decode those source rows from JP.
4. Rebuild coverage and actual CJK reports after each promoted batch.
5. Decide whether DATA003/1089 story text joins the broad build or remains a separate full-story deliverable.
```
