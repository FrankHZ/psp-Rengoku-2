# Simplified Chinese Patch Plan

Goal: produce a Simplified Chinese translation patch for the legally obtained Japanese Rengoku 2 dump. The USA release and wiki transcripts are reference material only; generated reference exports stay under ignored `local/` paths and must not be committed.

## Current Position

The text-container problem is mostly solved for the first practical targets:

- `DATA001/0008`: live in-stage tutorial/objective overlay, runtime-confirmed editable.
- `DATA001/0016`: menu/UI labels, runtime-confirmed editable.
- `DATA001/0017`: help/manual pages, runtime-confirmed editable.
- `DATA001/0012`: story/dialogue table, Briareos scene anchored.
- `DATA001/0003` and `DATA002/0065`: confirmed boot/name-input UI anchors.

The current importer safely patches same-size or shorter `u16` text/glyph-code runs and then replaces the same-size MCD3 entry back into the archive. This is enough for probes and concise text, but not enough for full-length rewrites.

## Reference Workflow

Use USA text to identify meaning and record alignment, not as binary patch data.

Confirmed local reference mappings:

| JP target | USA reference | Role |
| --- | --- | --- |
| `DATA001/0003` | `DATA001/0009` | Boot/init UI |
| `DATA001/0008` | `DATA001/0017` | Live tutorial/objective overlay |
| `DATA001/0012` | `DATA001/0022` | Story/dialogue |
| `DATA001/0015` | `DATA001/0026` | Large UI/text table |
| `DATA001/0016` | `DATA001/0027` | Menu/UI labels |
| `DATA001/0017` | `DATA001/0028` | Help/manual |

Use:

```powershell
python tools/align_reference_text.py <jp-export.json> <usa-export.json> local/work/<alignment>.json
```

The generated alignment includes record/run IDs, JP slot length, USA reference text, and whether the reference fits the current same-size budget.

## CHS Font Strategy

The existing font atlas is compact:

| Page family | Pages | Cell size | Capacity | Observed nonempty |
| --- | ---: | ---: | ---: | ---: |
| `codeANK9x14` | 1 | `9x14` | 126 | 120 |
| `codeJAP14x14` | 11 | `14x14` | 891 | 843 |

There are only about 48 visibly empty Japanese cells. That is not enough for unrestricted Simplified Chinese. The practical path is a curated glyph subset:

1. Build translation sheets for one target table at a time.
2. Count unique CHS characters needed by that table.
3. Reuse existing glyph codes for ASCII, numbers, punctuation, and any Japanese glyphs that are visually acceptable.
4. Assign CHS-only characters to empty or deliberately reclaimed `codeJAP14x14` cells.
5. Render those CHS glyphs into the font-page MIG textures.
6. Encode translated text as the assigned `u16` glyph codes.
7. Test in PPSSPP with the same extracted-folder workflow.

This means each patch build needs a generated local CHS glyph map, for example:

```text
local/work/chs_glyph_map.json
local/work/chs_font_pages/
```

Those files are generated build inputs and should remain ignored until we create repo-safe templates or scripts.

Current empty-cell inventory command:

```powershell
python tools/font_cell_inventory.py local/work/tdl_DATA001_0002 --empty-only --output local/work/font_empty_cells.csv
```

Current translation character inventory command:

```powershell
python tools/translation_char_inventory.py local/work/<translation-draft>.json --field chs_translation --output local/work/<chars>.json
```

The best first allocation pool is the empty tail of `codeJAP14x14_20_`:

```text
page_index 11, cell 33..80
candidate contiguous IDs 0x03c9..0x03f8
```

The ANK page also has a few empty 9x14 cells, but those are not ideal for CHS because they are narrower and closer to ASCII/control territory.

First local tutorial draft:

```text
local/work/chs_tutorial_draft_DATA001_0008.json
local/work/chs_tutorial_chars_DATA001_0008.json
```

Current result: all drafted CHS tutorial lines fit the original run budgets, but the draft needs 80 unique CJK characters. The empty `codeJAP14x14_20_` tail only provides 48 cells, so the first CHS font test must either reduce wording/character variety or deliberately reclaim at least 32 occupied glyph cells.

## Open Technical Tasks

### Required

- Create a translator-facing table format with:
  - `archive`, `mcd3_entry`, `record`, `run`
  - `source_max_units`
  - source partial decode / code list
  - USA reference text
  - CHS translation
  - assigned `translation_codes`
- Add an encoder that maps CHS translation text to `u16` glyph codes via a generated CHS glyph map.
- Add a font-page writer for 4bpp `MIG.00.1PSP` textures.
- Add a `.TDL` child replacement path for `DATA001/0002`, then same-size MCD3 replacement for the parent font table.

### Likely Dependency

Rendering CHS glyphs into 14x14 cells is easiest with Pillow and a local font such as:

```text
C:\Windows\Fonts\NotoSansSC-VF.ttf
C:\Windows\Fonts\simhei.ttf
C:\Windows\Fonts\simsun.ttc
```

Do not add this dependency until the font writer is ready to consume it.

### Risk

- Full story translation may require more unique CHS glyphs than the available empty/reclaimable cells.
- Longer CHS lines may still exceed original run budgets, even though CHS is usually denser than English.
- Reclaiming Japanese glyph cells is safe only after we know those glyphs are not needed by untranslated strings left in the build.
- Font atlas replacement must preserve MIG and TDL sizes unless/until archive resizing is implemented.

### Backup: Add More Glyph Pages

Adding new `codeJAP14x14` pages may be possible, but it is a second-stage fallback rather than the first prototype path.

The optimistic version is:

1. Create another 128x128, 4bpp `MIG.00.1PSP` font page such as `codeJAP14x14_22_`.
2. Append it as a new child in `DATA001/0002`'s `.TDL` table.
3. Rebuild the `.TDL` table and child offsets, because adding a row shifts the child data area.
4. Grow `DATA001/0002` and rebuild the parent `DATA001.BIN` MCD3 archive offsets.
5. Encode CHS text with glyph codes that target the new page.

Unknowns before this is safe:

- Whether the renderer reads the `.TDL` child count dynamically or expects exactly the known pages.
- Whether the glyph-code-to-page lookup accepts page IDs beyond the final observed `codeJAP14x14_20_` page.
- Whether executable code or another config table declares the font page range.
- Whether growing `DATA001/0002` and shifting later MCD3 entries is enough, or whether other offsets also reference the old layout.

Treat this as the backup plan for larger CHS coverage. The first prototype should use existing empty or deliberately reclaimed cells so that only same-size MIG, TDL, and MCD3 replacement is needed.

## Recommended Next Step

Start with `DATA001/0008` tutorials because the records are runtime-confirmed and small.

1. Create a local CHS translation sheet for records `10`, `11`, and `66-71`.
2. Count unique CHS characters.
3. Assign them to empty cells on `codeJAP14x14_20_`.
4. Render a tiny CHS font test replacing just `MOVE` and one body line.
5. Confirm PPSSPP renders CHS glyphs before scaling to larger tables.

## Current Prototype

The first font-routing probe is staged locally and ignored by git:

```text
local/rebuilt/font_cell33_probe_extracted/
```

What it changes:

- `DATA001/0002` font `.TDL`: child `11` / `codeJAP14x14_20_`, cell `33`, is replaced with a visible box test mark.
- `DATA001/0008`: record `70`, run `0`, is replaced with four copies of candidate glyph code `0x03c9`.

Test expectation:

- If `0x03c9` maps to `codeJAP14x14_20_` cell `33`, the 0F movement tutorial title should show four box marks.
- If it shows blank text or another glyph, the empty-cell inventory is still useful but the glyph-code formula needs correction before real CHS rendering.

Observed result:

- `0x03c9` renders as `欠`, so the contiguous glyph ID formula does not match this runtime text-code path.
- The next probe should keep the same patched font cell but replace the title with `0x0b21`, the `page_index * 0x100 + cell_index` candidate for page `11`, cell `33`.
- `0x0b21` crashes the game during execution, so high page-style glyph IDs are not safe to use as runtime text codes without more renderer research.
- A safer follow-up probe patches cell `33` across all `codeJAP14x14` pages and uses known-valid `0x03c9` again:

```text
local/rebuilt/font_all_jap_cell33_03c9_probe_extracted/
```

If this shows box marks, `0x03c9` is using cell `33` but from a different loaded page/bank than the static page-11 hypothesis. If it still shows `欠`, the code-to-cell mapping is not the manifest formula for this runtime text path.

Observed result:

- Patching cell `33` across all Japanese pages still renders `欠欠欠欠`.
- Therefore `0x03c9` is not cell `33` in the renderer mapping used by `DATA001/0008`.

Current narrowing probes patch cell ranges across all Japanese font pages while still using known-safe code `0x03c9`:

```text
local/rebuilt/font_range_00_20_03c9_probe_extracted/
local/rebuilt/font_range_21_40_03c9_probe_extracted/
local/rebuilt/font_range_41_60_03c9_probe_extracted/
local/rebuilt/font_range_61_80_03c9_probe_extracted/
```

Open each folder at the 0F movement tutorial. The build that turns `欠欠欠欠` into box marks identifies the cell range containing the real `0x03c9` glyph.

Extra runtime observation:

- PPSSPP GE shows the tutorial title glyph atlas at texture address `0x040e6700`.
- Using the observed `0x2100` runtime stride from base `0x040dc200`, this is page index `5`.
- Page index `5` corresponds to static font child `0005_codeJAP14x14_08_.bin`.
- Therefore the next focused probe should patch only child `5` after the range containing `欠` is known.

Range result:

- `font_range_00_20_03c9_probe_extracted`: many UI/tutorial glyphs become boxes, confirming the broad font patch is active, but the title remains `欠欠欠欠`. Therefore `0x03c9` is not in cell range `0-20`.
- `font_range_21_40_03c9_probe_extracted`: many UI/tutorial glyphs become boxes, but the title remains `欠欠欠欠`. Therefore `0x03c9` is not in cell range `21-40`.
- `font_range_41_60_03c9_probe_extracted`: many UI/tutorial glyphs become boxes, but the title remains `欠欠欠欠`. Therefore `0x03c9` is not in cell range `41-60`.
- `font_range_61_80_03c9_probe_extracted`: title becomes box marks. Therefore `0x03c9` is in cell range `61-80`.

Next focused probes should patch only child `5` / `0005_codeJAP14x14_08_.bin` in subranges of `61-80`, because GE showed the active title texture as `0x040e6700`.

Focused child-5 probe folders:

```text
local/rebuilt/font_child5_range_61_65_03c9_probe_extracted/
local/rebuilt/font_child5_range_66_70_03c9_probe_extracted/
local/rebuilt/font_child5_range_71_75_03c9_probe_extracted/
local/rebuilt/font_child5_range_76_80_03c9_probe_extracted/
```

Observed result:

- The hit is `61-65`.
- GE cursor inspection identifies the specific glyph as cell `65`.
- Confirmed mapping for this runtime path:

```text
glyph code 0x03c9 -> DATA001/0002 child 5, codeJAP14x14_08_, cell 65
```

Repo-safe seed file:

```text
samples/runtime_glyph_map_seed.csv
```

Exact-cell confirmation build:

```text
local/rebuilt/font_child5_cell65_03c9_probe_extracted/
```

This patches only child `5`, cell `65`, and uses `0x03c9` for the movement tutorial title.

Observed result:

- Confirmed. The title renders the replacement box mark from child `5`, cell `65`.
- This proves the current same-size chain works:

```text
edit MIG font cell -> replace TDL child -> replace DATA001 MCD3 entry 2 -> replace DATA001 MCD3 entry 8 text -> PPSSPP renders changed glyph
```

The next prototype can replace cell `65` with a real glyph bitmap while continuing to use text code `0x03c9`.

Existing-glyph copy prototype:

```text
local/rebuilt/font_child5_cell65_from_child6_cell59_03c9_probe_extracted/
```

This copies the existing `移` glyph candidate from child `6` / `codeJAP14x14_10_`, cell `59`, into child `5`, cell `65`. If the seed atlas transcription is correct, the 0F movement tutorial title should render as repeated `移` glyphs.

Observed result:

- Confirmed. The 0F movement tutorial title renders as `移移移移`.

## Efficient Probe Workflow

Use `tools/stage_font_probe.py` to stage future extracted-folder probes from JSON instead of manually chaining copy/import/archive commands.

Example:

```powershell
python tools/stage_font_probe.py samples/font_probe_move_copy.example.json --overwrite
```

Probe strategy from here:

1. Use GE to identify the active texture address for the target text.
2. Map the address back to a static child with the known `0x2100` stride.
3. Patch only that child, not all pages.
4. Use range probes only when the exact cell is unknown.
5. Once a code-to-cell mapping is confirmed, test real glyphs by copying known cells first; render new CHS glyphs only after the routing is proven.

`tools/stage_font_probe.py` accepts either one `font_patch` object or a `font_patches` array. Use the array form for CHS prototypes that need several glyph slots patched in one build.

Next mapping target:

- Original 0F movement title `移動方法` begins with codes `0x0465, 0x033f, 0x042e, 0x05ca`.
- `0x033f` is the likely `動` slot to reclaim for Simplified Chinese `动`.
- Focused child-5 range probes for `0x033f` are staged locally:

```text
local/rebuilt/font_child5_range_00_20_033f_probe_extracted/
local/rebuilt/font_child5_range_21_40_033f_probe_extracted/
local/rebuilt/font_child5_range_41_60_033f_probe_extracted/
local/rebuilt/font_child5_range_61_80_033f_probe_extracted/
```

Multi-code mapping is more efficient when several codes appear in one controlled string. For the 0F movement title, use:

```text
position 1 -> 0x0465
position 2 -> 0x033f
position 3 -> 0x042e
position 4 -> 0x05ca
```

The staged multi-code range probes are:

```text
local/rebuilt/font_child5_range_00_20_title4_probe_extracted/
local/rebuilt/font_child5_range_21_40_title4_probe_extracted/
local/rebuilt/font_child5_range_41_60_title4_probe_extracted/
local/rebuilt/font_child5_range_61_80_title4_probe_extracted/
```

Read them by position: if the second displayed glyph becomes a box in `41-60`, then `0x033f` is in range `41-60`.

Observed result:

- None of the child-5-only range probes changed the four original title glyphs.
- Therefore the original title codes are not on child `5`; the child-5 mapping is confirmed only for forced code `0x03c9`.
- Next step: patch all `codeJAP14x14` pages by range while displaying the four title codes, then read hits by position.

All-page multi-code probes:

```text
local/rebuilt/font_allpages_range_00_20_title4_probe_extracted/
local/rebuilt/font_allpages_range_21_40_title4_probe_extracted/
local/rebuilt/font_allpages_range_41_60_title4_probe_extracted/
local/rebuilt/font_allpages_range_61_80_title4_probe_extracted/
```

GE draw-order evidence for the unmodified 0F movement tutorial title:

| Draw count | Runtime texture | Runtime page | Static child | Title contribution |
| ---: | --- | ---: | ---: | --- |
| `3032/6325` | `0x040e8800` | `6` | `6` | `移` and `方` |
| `3044/6325` | `0x040e4600` | `4` | `4` | `動` |
| `305x/6325` | `0x040eca00` | `8` | `8` | `法` |

This explains why child-5-only title probes did not hit: child `5` is valid for forced code `0x03c9`, but the original title draws from children `4`, `6`, and `8`.

GE cell inspection is sufficient for the remaining original title glyphs, so no additional PPSSPP range probes are needed for `移動方法`:

- `動`: `0x033f -> DATA001/0002 child 4, cell 8`, first row ninth column on `0x040e4600`.
- `法`: `0x05ca -> DATA001/0002 child 8, cell 11`, on `0x040eca00`.

These derive the current runtime page bases:

```text
child 4 base = 0x033f -  8 = 0x0337
child 6 base = 0x0465 - 59 = 0x042a
child 8 base = 0x05ca - 11 = 0x05bf
```

Focused title-page probes now patch only children `4`, `6`, and `8`:

```text
local/rebuilt/font_title_pages_468_range_00_20_probe_extracted/
local/rebuilt/font_title_pages_468_range_21_40_probe_extracted/
local/rebuilt/font_title_pages_468_range_41_60_probe_extracted/
local/rebuilt/font_title_pages_468_range_61_80_probe_extracted/
```

Read by title position against the same original-code probe:

```text
position 1 -> 0x0465
position 2 -> 0x033f
position 3 -> 0x042e
position 4 -> 0x05ca
```

Even tighter page-specific probes:

Child `6`, positions `1` and `3`:

```text
local/rebuilt/font_p1p3_child6_range_00_20_probe_extracted/
local/rebuilt/font_p1p3_child6_range_21_40_probe_extracted/
local/rebuilt/font_p1p3_child6_range_41_60_probe_extracted/
local/rebuilt/font_p1p3_child6_range_61_80_probe_extracted/
```

Child `4`, position `2`:

```text
local/rebuilt/font_p2_child4_range_00_20_probe_extracted/
local/rebuilt/font_p2_child4_range_21_40_probe_extracted/
local/rebuilt/font_p2_child4_range_41_60_probe_extracted/
local/rebuilt/font_p2_child4_range_61_80_probe_extracted/
```

Child `8`, position `4`:

```text
local/rebuilt/font_p4_child8_range_00_20_probe_extracted/
local/rebuilt/font_p4_child8_range_21_40_probe_extracted/
local/rebuilt/font_p4_child8_range_41_60_probe_extracted/
local/rebuilt/font_p4_child8_range_61_80_probe_extracted/
```

GE row/column shortcut for child `6`:

- `移`: row `7`, column `6` on a 9-column page -> cell `59`.
- `方`: row `1`, column `5` on a 9-column page -> cell `4`.
- Confirmed `移`: `0x0465 -> DATA001/0002 child 6, cell 59`, matching exported cell `local/work/glyph_cells/0006_codeJAP14x14_10_/cell_059_r06_c05.png`.
- Confirmed `方`: `0x042e -> DATA001/0002 child 6, cell 4`, matching exported cell `local/work/glyph_cells/0006_codeJAP14x14_10_/cell_004_r00_c04.png`.
- Inferred child-6 base for this runtime path: `0x042a`.

```text
0x0465 - 59 = 0x042a
0x042e -  4 = 0x042a
cell = glyph_code - 0x042a
```

This is the first evidence that each loaded font page has a runtime code base. The important question is now finding or deriving those page bases, not treating the cell manifest's old `glyph_id_*` columns as runtime code formulas.

Exact combined probe:

```text
local/rebuilt/font_child6_cells04_59_title_probe_extracted/
```

This patches child `6`, cells `4` and `59`, while displaying the four original title codes.

Current first-deliverable target:

- Stage a PPSSPP-testable extracted-folder build with selected `DATA001/0008` tutorial text replaced by Simplified Chinese.
- Use the confirmed original title mappings as the first controlled route:

```text
移 0x0465 -> child 6 cell 59, base 0x042a
動 0x033f -> child 4 cell  8, base 0x0337
方 0x042e -> child 6 cell  4, base 0x042a
法 0x05ca -> child 8 cell 11, base 0x05bf
```

- Reuse existing glyphs where acceptable, then patch new CHS-only glyphs into known cells and encode tutorial rows with the confirmed runtime codes.

Homebrew rendered-title workflow:

- `tools/render_mig_font_cell.py` renders a TrueType/OpenType glyph into one 4bpp MIG font cell.
- `tools/stage_font_probe.py` supports `font_patches[].mode = "render"` for staging real CHS glyph patches alongside text-code replacements.
- `tools/build_chs_tutorial.py` generates a full `DATA001/0008` tutorial build from the CHS draft, assigns CHS characters to known runtime slots, writes exact `translation_codes`, and stages the extracted-folder artifact.
- `requirements-dev.txt` now includes Pillow for glyph rendering.
- Small-font quality note: the low-level renderer still defaults to grayscale antialiasing for compatibility, but accepts `render_mode`, `threshold`, `gray_threshold`, `stroke_radius`, and `font_index` in render patch JSON. The full tutorial builder now defaults to `C:/Windows/Fonts/simsun.ttc --font-index 0 --render-mode palette3 --threshold 64 --gray-threshold 176 --stroke-radius 0`, which is closer to the PSP-era small CJK UI look than the first antialiased Noto Sans SC prototype. If a chosen font is too thin, try `--stroke-radius 1`; if strokes fill in, raise `--threshold`.
- Original font level analysis:

```powershell
python tools/analyze_font_levels.py
```

This writes a local report under:

```text
local/work/font_level_analysis/
```

Current result: the font pages are 4bpp and original glyph cells use indices across `1..15`, but the CLUT repeats only three visible colors: black, gray, and white. So the atlas is not literally 2bpp, but it behaves like a tiny effective palette. For CHS rendering, `palette3` keeps output in original-style gray/white classes while preserving the existing 4bpp container path. Use `binary` only as a maximum-crispness comparison mode.
- Local font comparison helper:

```powershell
python tools/compare_chs_fonts.py
```

This writes local previews and a report under:

```text
local/work/font_compare/
```

Current local comparison result: `SimSun` / `NSimSun` are the best first candidates for the tutorial font. `NotoSansSC-VF.ttf` remains a readable sans fallback, but its default face renders much thinner and less like the original game UI at 14x14. Japanese gothic/mincho fonts are useful stylistic references but miss several Simplified glyphs in the current tutorial sample.

First local rendered-title artifact:

```text
local/rebuilt/tutorial_chs_v1_extracted/
```

This build changes `DATA001/0008` record `70` from the original visual title `移動方法` to homebrew-rendered `移动方式` by reusing the same four runtime text codes and replacing all four glyph cells:

```text
移 -> 0x0465 -> child 6 cell 59
动 -> 0x033f -> child 4 cell  8
方 -> 0x042e -> child 6 cell  4
式 -> 0x05ca -> child 8 cell 11
```

The first staged build uses `C:/Windows/Fonts/NotoSansSC-VF.ttf` at 13px for these 14x14 cells.

Local build inputs:

```text
local/work/tutorial_chs_v1/stage_move_method_chs.json
local/work/tutorial_chs_v1/DATA001_0008_title_move_method.json
local/work/tutorial_chs_v1/runtime_glyph_assignments.csv
```

Local structural verification:

- Rebuilt `DATA001.BIN` stays `21016576` bytes.
- Patched font child pages stay `8464` bytes each.
- Extracted rebuilt `DATA001/0008` record `70` contains `0x0465 0x033f 0x042e 0x05ca`.

First local full-tutorial artifact:

```text
local/rebuilt/tutorial_chs_full_v1_extracted/
```

This build translates the currently drafted `DATA001/0008` tutorial records:

```text
10, 11, 66, 67, 68, 69, 70, 71
```

The generated build uses:

```text
local/work/chs_tutorial_draft_DATA001_0008.json
local/work/tutorial_chs_full_v1/DATA001_0008_chs_full.json
local/work/tutorial_chs_full_v1/runtime_glyph_assignments.csv
local/work/tutorial_chs_full_v1/stage_chs_full.json
```

Rebuild with the current crisp preset:

```powershell
python tools/build_chs_tutorial.py --overwrite
```

To compare against the original antialiased prototype:

```powershell
python tools/build_chs_tutorial.py --render-mode grayscale --threshold 0 --overwrite
```

To compare against full-white binary rendering:

```powershell
python tools/build_chs_tutorial.py --render-mode binary --threshold 64 --overwrite
```

To force the previous Noto Sans SC font:

```powershell
python tools/build_chs_tutorial.py --font C:/Windows/Fonts/NotoSansSC-VF.ttf --font-index 0 --overwrite
```

Local structural verification:

- Rebuilt `DATA001.BIN` stays `21016576` bytes.
- Generated 84 CHS/non-ASCII glyph assignments into confirmed runtime slot pools on children `4`, `6`, and `8`.
- Re-extracted rebuilt `DATA001/0008` records match generated `translation_codes`:

```text
record 10:  9/21 code units
record 11:  9/21 code units
record 66:  2/4 code units
record 67: 53/112 code units
record 68:  2/5 code units
record 69: 49/124 code units
record 70:  4/4 code units
record 71: 43/121 code units
```

First local equipment-slice artifact:

```text
local/rebuilt/equipment_chs_v1_extracted/
```

Generic-builder verification artifact:

```text
local/rebuilt/equipment_chs_v1_generic_extracted/
```

Both were confirmed in PPSSPP. The slice patches `DATA001/0015` records `70-81` and `94-97`, covering the screenshot-visible equipment family around `C-K.O.D.`, `Gladiator`, `Dante`, chainsaws, `SAA Magnum 88`, and `D Dragoon`.

Local source sheets:

```text
local/work/equipment_chs_v1/DATA001_0015_equipment_slice_70-81_94-97.csv
local/work/equipment_chs_v1/DATA001_0015_equipment_slice_70-81_94-97.json
```

Build commands:

```powershell
python tools/build_chs_equipment_slice.py --overwrite
python tools/build_chs_offset_table.py --table DATA001/0015 --sheet local/work/equipment_chs_v1/DATA001_0015_equipment_slice_70-81_94-97.json --work-root local/work/equipment_chs_v1/build_generic --output-root local/rebuilt/equipment_chs_v1_generic_extracted --overwrite
```

`K.O.D.` / `C-K.O.D.` preserve the punctuation dots and match the aligned English names.

First combined DATA001 artifact:

```text
local/rebuilt/combined_chs_v1_0008_0015_0016_extracted/
```

This build patches one shared `DATA001/0002` font archive, then applies multiple same-size text entry replacements into the same `DATA001.BIN`.

Multi-base runtime probe artifact:

```text
local/rebuilt/page_base_probe_v1_extracted/
```

Build command:

```powershell
python tools/build_page_base_probe.py --overwrite
```

Local marker map:

```text
local/work/page_base_probe_v1/probe_manifest.csv
```

This probe patches `DATA001/0008` overlay hint/body rows with raw codes from
several candidate base families, while rendering marker letters into competing
static MIG cells. The marker visible in PPSSPP identifies which candidate
page/cell route the runtime used. This is separate from the yellow tutorial
title path; in the first `page_base_probe_v1` run, the yellow title still used
the original `移動方法` title glyphs while the probe text appeared in the
overlay/body hint area.

Patched overlay/body rows:

```text
record 10: overlay/body hint line BASE PROBE
record 11: overlay/body hint line LOOK AT BODY ROWS
record 67: B0 0100=<mark> 0101=<mark> 011B=<mark>
record 69: B1 01FE=<mark> 01FB=<mark> 01D4=<mark>
record 71: B2 021B=<mark> 0222=<mark> 023C=<mark> 0276=<mark> 026E=<mark>
```

Candidate interpretation:

```text
0100: A = child 1 cell  0 base 0x0100; B = child 2 cell 49 base 0x00cf
0101: C = child 1 cell  1 base 0x0100; D = child 2 cell 50 base 0x00cf
011B: E = child 1 cell 27 base 0x0100; F = child 2 cell 76 base 0x00cf
01FE: G = child 5 cell 60 base 0x01c2
01FB: H = child 5 cell 57 base 0x01c2
01D4: I = child 5 cell 18 base 0x01c2
021B: J = child 2 cell 40 base 0x01f3; K = child 2 cell 27 base 0x0200
0222: L = observed cell 47 base 0x01f3; M = child 2 cell 34 base 0x0200
023C: N = child 3 cell 73 base 0x01f3; O = child 2 cell 60 base 0x0200
0276: P = observed cell 50 base 0x0244
026E: Q = observed cell 42 base 0x0244
```

PPSSPP/GE observation from the first probe run:

- `0x021b` rendered as `る` in the overlay/body row and is cell `40` on runtime texture `local/work/dumped_textures/040e040028998f6f134f822a.png`.
- `0x023c` rendered as `ス` in the overlay/body row and is cell `73` on runtime texture `local/work/dumped_textures/040e2500676a3b4e3748fa38.png`.
- `0x0222` rendered as `を` in the overlay/body row and is cell `47` on runtime texture `0x040e0400`.
- `0x026e` rendered as `ル` in the overlay/body row and is cell `42` on runtime texture `0x040e2500`.
- `0x0276` rendered as `ン` in the overlay/body row and is cell `50` on runtime texture `0x040e2500`.
- The `0x021b`, `0x0222`, and `0x023c` observations give `code - cell = 0x01f3`.
- The `0x026e` and `0x0276` observations give `code - cell = 0x0244`.
- In `page_base_probe_v2`, the `C3` row on runtime texture `0x040e0400` confirmed another shared overlay base:

```text
0x01e7 し cell 69 -> base 0x01a2
0x01e9 す cell 71 -> base 0x01a2
0x01dc が cell 58 -> base 0x01a2
0x01e3 こ cell 65 -> base 0x01a2
0x01dd き cell 59 -> base 0x01a2
```

- Because these came from the overlay/body runtime path, treat `0x01a2`, `0x01f3`, and `0x0244` as overlay-context base observations rather than globally promoted title-page bases.

Post-`0x01a2` scan:

```text
local/work/page_base_candidates/post_overlay2_unknown_base_scan.md
```

Current remaining high-weight candidate bases after excluding `0x01a2`,
`0x01f3`, `0x0244`, `0x0337`, `0x0388`, `0x042a`, and `0x05bf`:

```text
0x0100 / child 1 / 0x040de300  punctuation-style page100 candidate
0x00cf / child 2 / 0x040e0400  competing punctuation contiguous candidate
0x0120 / child 3 / 0x040e2500  ellipsis and early-symbol candidate
0x0171 / child 4 / 0x040e4600  lower-priority overlay candidate
0x03a8 / child 11 / 0x040f2d00 lower-priority high-page candidate
```

Second probe artifact:

```text
local/rebuilt/page_base_probe_v2_extracted/
```

Build command:

```powershell
python tools/build_page_base_probe.py --variant v2 --work-root local/work/page_base_probe_v2 --output-root local/rebuilt/page_base_probe_v2_extracted --overwrite
```

Probe manifest:

```text
local/work/page_base_probe_v2/probe_manifest.csv
```

`page_base_probe_v2` includes:

```text
record 67: C2 1FE 1FB 1D4 1EF 1F6
record 69: P0 100 101 102 11B 123
record 71: C3 1E7 1E9 1DC 1E3 1DD
```

The C3 row confirmed overlay base `0x01a2`. The P0 row then distinguished
`0x0100` from the competing `0x00cf` punctuation/control-like route, and
`0x0123` from the competing child 3 / base `0x0120` route.

The P0 row later confirmed overlay base `0x0100` on runtime texture
`0x040de300`:

```text
0x0100    cell  0 -> base 0x0100
0x0101 、 cell  1 -> base 0x0100
0x0102 。 cell  2 -> base 0x0100
0x011b ー cell 27 -> base 0x0100
0x0123 … cell 35 -> base 0x0100
```

For this overlay/body path, `0x0100` wins over the competing `0x00cf`
contiguous candidate, and `0x0123` uses child 1 / base `0x0100` rather than
child 3 / base `0x0120`.

Post-`0x0100` scan:

```text
local/work/page_base_candidates/post_overlay3_unknown_base_scan.md
```

Remaining counts after excluding confirmed overlay/body bases `0x0100`,
`0x01a2`, `0x01f3`, and `0x0244`, plus the earlier title bases:

```text
unique unknown codes: 812
unknown-code occurrences: 7745
```

The next compact probe is:

```text
local/rebuilt/page_base_probe_v4_extracted/
```

Build command:

```powershell
python tools/build_page_base_probe.py --variant v4 --work-root local/work/page_base_probe_v4 --output-root local/rebuilt/page_base_probe_v4_extracted --overwrite
```

Probe manifest:

```text
local/work/page_base_probe_v4/probe_manifest.csv
```

`page_base_probe_v4` includes:

```text
record 65: R4  19D 1A0 194 196 1A1   candidate base 0x0171 / child 4
record 67: H4  428 410 411 424 40D   candidate base 0x0400 / child 4
record 69: H5  52E 530 523 532 52A   candidate base 0x0500 / child 5
record 71: H11 3DE 3F1 3E1 3F2       candidate base 0x03a8 / child 11
```

The v4 marker candidates did not win for H11/H5/H4, but the original glyphs
visible in the same rows exposed two actual overlay bases:

```text
H11 0x03de 戦 cell  5 texture 0x040e6700 -> base 0x03d9
H11 0x03f1 全 cell 24 texture 0x040e6700 -> base 0x03d9
H11 0x03e1 最 cell  8 texture 0x040e6700 -> base 0x03d9
H11 0x03f2 目 cell 25 texture 0x040e6700 -> base 0x03d9

H4  0x0428 押 cell 79 texture 0x040e6700 -> base 0x03d9
H4  0x0410 子 cell 55 texture 0x040e6700 -> base 0x03d9
H4  0x0411 横 cell 56 texture 0x040e6700 -> base 0x03d9
H4  0x0424 越 cell 75 texture 0x040e6700 -> base 0x03d9
H4  0x040d 増 cell 52 texture 0x040e6700 -> base 0x03d9

H5  0x052e 入 cell 17 texture 0x040ea900 -> base 0x051d
H5  0x0530 戻 cell 19 texture 0x040ea900 -> base 0x051d
H5  0x0523 選 cell  6 texture 0x040ea900 -> base 0x051d
H5  0x0532 位 cell 21 texture 0x040ea900 -> base 0x051d
H5  0x052a 元 cell 13 texture 0x040ea900 -> base 0x051d
```

These observations mean the static candidate bases `0x03a8`, `0x0400`, and
`0x0500` did not describe those v4 overlay/body rows. H11/H4 route through
child 5 / texture `0x040e6700`, while H5 routes through child 7 / texture
`0x040ea900`.

Post-`0x03d9` and `0x051d` scan:

```text
local/work/page_base_candidates/post_overlay4_unknown_base_scan.md
```

Remaining counts after excluding the v4-observed overlay/body bases:

```text
unique unknown codes: 657
unknown-code occurrences: 4603
```

Next probe artifact:

```text
local/rebuilt/page_base_probe_v5_extracted/
```

Build command:

```powershell
python tools/build_page_base_probe.py --variant v5 --work-root local/work/page_base_probe_v5 --output-root local/rebuilt/page_base_probe_v5_extracted --overwrite
```

Probe manifest:

```text
local/work/page_base_probe_v5/probe_manifest.csv
```

`page_base_probe_v5` keeps `R4` visible and adds the next two compact
families:

```text
record 67: D3  314 311 310 334       candidates 0x0306/child9 vs 0x0300/child3
record 69: H5L 508 502 51B 516 51A   candidate 0x0500/child5 for lower 0x05xx
record 71: R4  19D 1A0 194 196 1A1   candidate 0x0171/child4
```

The v5 marker candidates did not describe the displayed routes, but the row
glyphs/GE cells exposed three more overlay bases:

```text
R4  0x019d A cell 76 texture 0x040de300 -> base 0x0151
R4  0x01a0 D cell 79 texture 0x040de300 -> base 0x0151
R4  0x0194 1 cell 67 texture 0x040de300 -> base 0x0151
R4  0x0196 3 cell 69 texture 0x040de300 -> base 0x0151
R4  0x01a1 E cell 80 texture 0x040de300 -> base 0x0151

D3  0x0314 一 cell 46 texture 0x040e4600 -> base 0x02e6
D3  0x0311 練 cell 43 texture 0x040e4600 -> base 0x02e6
D3  0x0310 熟 cell 42 texture 0x040e4600 -> base 0x02e6
D3  0x0334 代 cell 78 texture 0x040e4600 -> base 0x02e6

H5L 0x0508 変 cell 60 texture 0x040ea900 -> base 0x04cc
H5L 0x0502 取 cell 54 texture 0x040ea900 -> base 0x04cc
H5L 0x051b 形 cell 79 texture 0x040ea900 -> base 0x04cc
H5L 0x0516 得 cell 74 texture 0x040ea900 -> base 0x04cc
H5L 0x051a 明 cell 78 texture 0x040ea900 -> base 0x04cc
```

Post-`0x0151`, `0x02e6`, and `0x04cc` scan:

```text
local/work/page_base_candidates/post_overlay5_unknown_base_scan.md
```

Remaining unknown pool:

```text
unique unknown codes: 518
unknown-code occurrences: 2508
```

Next unknown-base probe:

```text
local/rebuilt/page_base_probe_v6_extracted/
```

Build command:

```powershell
python tools/build_page_base_probe.py --variant v6 --work-root local/work/page_base_probe_v6 --output-root local/rebuilt/page_base_probe_v6_extracted --overwrite
```

Probe manifest:

```text
local/work/page_base_probe_v6/probe_manifest.csv
```

`page_base_probe_v6` combines the last clean static candidates with
observe-only high-frequency leftovers:

```text
record 65: H6   63B 62E 62C 62D 63A   candidate base 0x0600 / child 6
record 67: H7   712 72A 72E 74C 705   candidate base 0x0700 / child 7
record 69: S2   2AE 2AF 2AC 2AD       candidate base 0x0264 / child 7
record 71: OBS  493 48A 4A5 49D 483   observe-only high 0x04xx leftovers
record 73: OBS2 485 4A6 496 5AB 599   observe-only 0x04xx/0x05xx leftovers
```

For `OBS` and `OBS2`, no marker cells are patched. The useful observation is
the original rendered glyph plus GE cell/texture; derive the base with
`base = code - cell`, as with H11/H5/H4/H5L.

Help/manual probe alternative:

```text
local/rebuilt/page_base_probe_help0017_v1_extracted/
```

Build command:

```powershell
python tools/build_page_base_probe.py --variant help0017-v1 --work-root local/work/page_base_probe_help0017_v1 --output-root local/rebuilt/page_base_probe_help0017_v1_extracted --overwrite
```

Probe manifest:

```text
local/work/page_base_probe_help0017_v1/probe_manifest.csv
```

This patches `DATA001/0017` help/manual rows instead of the in-stage tutorial
overlay. The first page/index rows use one code each so they are easy to
inspect:

```text
record 1:  A 493=<mark>   candidate base 0x047b / child 6 / cell 24
record 2:  B 48A=<mark>   candidate base 0x047b / child 6 / cell 15
record 3:  C 4A5=<mark>   candidate base 0x047b / child 6 / cell 42
record 4:  D 49D=<mark>   candidate base 0x047b / child 6 / cell 34
record 5:  E 485=<mark>   candidate base 0x047b / child 6 / cell 10
record 6:  F 5AB=<mark>   candidate base 0x056e / child 8 / cell 61
record 7:  G 5B1=<mark>   candidate base 0x056e / child 8 / cell 67
record 8:  H 599=<mark>   candidate base 0x056e / child 8 / cell 43
record 9:  I 591=<mark>   candidate base 0x056e / child 8 / cell 35
record 11: J 5B0=<mark>   candidate base 0x056e / child 8 / cell 66
record 12: P6 63B 62E 62C 62D 63A   candidate base 0x0600 / child 6
record 14: P7 712 72A 72E 74C 705   candidate base 0x0700 / child 7
record 16: S2 2AE 2AF 2AC 2AD       candidate base 0x0264 / child 7
```

Observation rule: if the marker letter appears after `=`, the candidate base
for that row is confirmed. If the marker does not appear, record the rendered
glyph plus GE texture address and highlighted cell number so we can derive the
actual base.

Observed help/manual probe results:

```text
0x0493 -> marker A, child 6, cell 24, texture 0x040e8800, base 0x047b
0x048a -> marker B, child 6, cell 15, texture 0x040e8800, base 0x047b
0x05b0 -> marker J, child 8, cell 66, texture 0x040eca00, base 0x056e
0x063b -> 欲, child 9, cell 43, texture 0x040eeb00, base 0x0610
0x072e -> 脱, child 10, cell 43, texture 0x040f0c00, base 0x0703
0x02ae -> β, child 3, cell 25, texture 0x040e2500, base 0x0295
```

Post-help-probe scan:

```text
local/work/page_base_candidates/post_help0017_v1_unknown_base_scan.md
```

Remaining unknown pool after excluding the newly observed bases:

```text
unique unknown codes: 202
unknown-code occurrences: 423
```

At this point the unknown-base scan is functionally complete for broad
translation work. The remaining pool is dominated by low-frequency
DATA003/DATA002 tails plus tiny punctuation/control candidates; no high-impact
static candidate base remains in the current evidence set.

## Runtime kana map

The full kana runtime map is generated by:

```powershell
python tools/build_kana_runtime_map.py --output samples/runtime_kana_map.csv
```

Output:

```text
samples/runtime_kana_map.csv
```

This map currently covers `169` kana rows:

```text
83 hiragana rows
86 katakana rows
18 existing seed points used as consistency checks
```

The map is inferred from contiguous JIS-style kana order and confirmed
runtime bases. It should be used as a decoding aid and coverage layer, not as
a global replacement for context-aware glyph handling. Known guardrail:
static/manual maps can conflict with runtime/story maps, e.g. a code can be a
kanji in one static page context and kana in the story/overlay path.

Included:

```text
DATA001/0008 tutorial draft
DATA001/0015 equipment screenshot slice
DATA001/0016 drafted UI/menu rows
DATA001/0017 drafted help/manual rows
```

Local build notes:

```text
local/work/combined_chs_v2_0008_0015_0016_0017/
```

Rebuild command:

```powershell
python tools/build_chs_combined_data001.py --work-root local/work/combined_chs_v2_0008_0015_0016_0017 --output-root local/rebuilt/combined_chs_v2_0008_0015_0016_0017_extracted --overwrite
```

Current combined build:

- The previous capacity blocker is removed by the newly confirmed child 1,
  child 5, and child 7 overlay slot pools.
- `0008 + 0015 + 0016 + 0017` now stages successfully and uses `262`
  assigned non-ASCII glyphs.
- Assignment distribution in the current build: child 1 / base `0x0151` uses
  `81` cells, child 4 / base `0x0337` uses `81`, child 5 / base `0x03d9`
  uses `81`, child 6 / base `0x042a` uses `18`, and child 8 / base `0x05bf`
  uses `1`.
- PPSSPP-ready output: `local/rebuilt/combined_chs_v2_0008_0015_0016_0017_extracted/`.
