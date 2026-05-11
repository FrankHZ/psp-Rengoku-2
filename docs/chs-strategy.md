# Chinese Patch Strategy

This file holds current project strategy. It is expected to change as the patch
workflow evolves.

## Build Strategy

Prioritize PPSSPP-ready builds that validate a broad slice of the game. The
current broad build should be treated as the baseline until superseded:

```text
local/rebuilt/combined_chs_v23_tutorial_usa_aligned_bitplane_extracted/
```

The main blocker is glyph capacity. Do not assume alternate runtime bases add
storage; bases like child 9 / `0x0610` and child 9 / `0x0661` are alternate code
windows over the same physical 81 cells.

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
logical capacity hypothesis: 11 JP pages * 81 cells * 2 layers = 1782 cells
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

The broad CHS composer now has a bitplane assignment model. v20 was PPSSPP
checked and looked good. Current v23 result after packing every current target
row and promoting DATA001/0008 tutorial placeholders from USA alignment:

```text
artifact: local/work/combined_chs_v23_tutorial_usa_aligned_bitplane/
logical assigned glyphs:           1033
physical cells used:                554
low-layer glyphs:                   553
high-layer glyphs:                  480
logical capacity model:            1782
usable logical headroom:            about 742 after reserved icon cells
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

Current v23 coverage report:

```text
artifact: local/work/chs_coverage_v23_tutorial_usa_aligned_bitplane/
parsed rows:                         1637
rows in current build:               1637
rows not in current build:              0
local draft rows not built:             0
estimate-only rows not built:           0
```

Quality caveat: v23 still includes rough rows outside the tutorial table. The
previous v22 all-target sheet included 314 estimate rows; 66 of those were
automatically fitted to original slot budgets, recorded at:

```text
local/work/full_current_target_sheets_v2/fit_adjustments.csv
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
