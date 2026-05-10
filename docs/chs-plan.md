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

This probe patches `DATA001/0008` tutorial rows with raw codes from several
candidate base families, while rendering marker letters into competing static
MIG cells. The marker visible in PPSSPP identifies which candidate page/cell
route the runtime used.

Patched rows:

```text
record 10: BASE PROBE
record 11: LOOK AT BODY ROWS
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
021B: J = child 6 cell  8 base 0x0213; K = child 2 cell 27 base 0x0200
0222: L = child 6 cell 15 base 0x0213; M = child 2 cell 34 base 0x0200
023C: N = child 6 cell 41 base 0x0213; O = child 2 cell 60 base 0x0200
0276: P = child 7 cell 18 base 0x0264
026E: Q = child 7 cell 10 base 0x0264
```

Included:

```text
DATA001/0008 tutorial draft
DATA001/0015 equipment screenshot slice
DATA001/0016 drafted UI/menu rows
```

Local build notes:

```text
local/work/combined_chs_v1_0008_0015_0016/README.md
```

Rebuild command:

```powershell
python tools/build_chs_combined_data001.py --target DATA001/0008 local/work/chs_tutorial_draft_DATA001_0008.json --target DATA001/0015 local/work/equipment_chs_v1/DATA001_0015_equipment_slice_70-81_94-97.json --target DATA001/0016 local/work/ui_help_chs_v1/DATA001_0016_ui_sheet.json --work-root local/work/combined_chs_v1_0008_0015_0016 --output-root local/rebuilt/combined_chs_v1_0008_0015_0016_extracted --overwrite
```

Current combined-build blocker:

- Adding `DATA001/0017` help/manual drafted rows to the same build requires `262` assigned non-ASCII glyphs.
- The currently confirmed runtime slot pool covers `243` cells across children `4`, `6`, and `8`.
- Therefore `0008 + 0015 + 0016 + 0017` is blocked by glyph capacity, not by archive staging.
- The three-entry build uses `216` assigned glyphs and is structurally verified.
