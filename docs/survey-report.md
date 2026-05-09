# Survey Report

Date: 2026-05-09

Status: Survey phase complete enough to stop.

## Summary

The extracted Rengoku 2 ISO uses `DATA000.BIN` as a top-level `MCD3` archive index for `DATA001.BIN` through `DATA005.BIN`.

The survey did not find high-confidence dialogue/prose strings in raw archive scans. Most strings found so far are resource names, map object names, model names, texture names, media identifiers, or PSP metadata.

The strongest text-related lead is font/rendering data:

```text
DATA001.BIN -> MCD3 entry 2 -> .TDL -> 12 MIG font/code-page resources
```

Those `MIG` resources are consistent 128x128 4bpp paletted texture pages named `codeANK9x14_00_0` and `codeJAP14x14_*`.

Runtime PPSSPP GE captures confirm the game draws Japanese text from 128x128 `CLUT4` textures. Dumped texture addresses advance by `0x2100`, matching the first internal size/stride value in each extracted `MIG` page. The extracted `.TDL` child resources are `0x2110` bytes, with the actual 8192-byte pixel/index block at `0x110`. The captured address range maps cleanly to static font pages 0-8. See `docs/runtime-observations.md`.

Screenshot phrases searched so far, including tutorial text (`移動方法`, `方向キー`, `起動している転送機を使用して１階へ移動せよ`), menu/help text (`ステータス／フロアマップ表示`), and equipment UI labels (`最大耐久力`, `物理防御`, `電子防御`, `素体頭部`, `素体左腕`, `素体右腕`, `素体胸部`, `素体脚部`) do not appear as exact UTF-8, Shift-JIS/CP932, or EUC-JP strings in the extracted ISO. This supports the current assumption that visible text may use a custom glyph index stream, compression, or another encoded container.

The strongest text-container lead is now confirmed: the small unknown `DATA001.BIN` entries parse as simple offset tables and contain length-prefixed text/glyph-code runs.

| MCD3 entry | Count | Size | Why it matters |
| ---: | ---: | ---: | --- |
| `3` | 15 | 1000 | Small table-like records near font/UI resources |
| `8` | 86 | 11504 | Offset table with many short records |
| `12` | 420 | 26696 | Large offset table with many records |
| `15` | 336 | 51956 | Large offset table with variable records |
| `16` | 328 | 18360 | Confirmed UI/menu text table with English labels and floor names |
| `17` | 105 | 26076 | Offset table with variable records |

These records begin with repeated control-looking values and contain length-prefixed runs. Some runs are direct ASCII stored as `u16` code units; others are glyph-code runs that reference the font atlas. Confirmed ASCII strings include `GRAPPLE`, `SLASH`, `IMPACT`, `QUANTUM`, `BULLET`, `HEAT`, `EQUIP`, `BUILD`, `ITEM`, `FILE`, `OPTION`, `EXIT`, `HELP`, and floor names such as `RENGOKU 0F` and `H.E.A.V.E.N.-C 99F Guardian`.

Confirmed extraction command:

```powershell
.\.venv\Scripts\python.exe tools/extract_text.py --format offset-table-runs local/work/mcd3_entries/DATA001/0016_bin.bin local/work/extract_text_DATA001_0016.json
```

A partial seeded glyph-map export is also available for the confirmed UI table:

```powershell
.\.venv\Scripts\python.exe tools/extract_text.py --format offset-table-runs --glyph-map samples/glyph_map_seed.csv local/work/mcd3_entries/DATA001/0016_bin.bin local/work/extract_text_DATA001_0016_seeded.json
```

Current result: 328 extracted runs from `DATA001` entry `16`; 168 are direct `u16` ASCII text runs and 160 are glyph-code runs. The seed map is intentionally incomplete and currently decodes known glyphs only, leaving unknown Japanese glyphs as middots. This is enough to validate the extraction shape, not enough for translation.

The first confirmed story text table with fully anchored dialogue is:

```text
DATA001.BIN -> MCD3 entry 12 -> offset table
```

The 4F boss / Briareos scene supplied by runtime capture and checked against the Rengoku 2 wiki transcript decodes in this table:

| Scene slice | Records | Notes |
| --- | --- | --- |
| Briareos pre-fight | `140-143` | Matches the supplied screenshot dialogue; record `142` has five `ｋ` codepoints in the ROM export. |
| Briareos post-fight | `160-174` | Matches the same reference transcript; record `170` uses `@GRAM@` as a placeholder token. |

Story dialogue export command:

```powershell
.\.venv\Scripts\python.exe tools/extract_text.py --format offset-table-runs --glyph-map samples/story_glyph_map_seed.csv local/work/mcd3_entries/DATA001/0012_bin.bin local/work/extract_text_DATA001_0012_story_seeded.json
```

The first confirmed story command/control table is:

```text
DATA003.BIN -> MCD3 entry 1089 -> offset table
```

It contains script commands stored as direct `u16` ASCII, including `#start 2F`, `#start 3F`, `#start 4F`, `#start 6F`, `#page`, `#white`, `#center`, `#left`, `#color`, `#readbg`, `#readwait`, `#wait`, and `#end`. The observed blue-character line also appears as an encoded row in the `#start 6F` section, record `306`, by the exact repeated code window for `マタ、キターーー`; treat this as command/script context until its relationship to the `DATA001/0012` text table is proven.

Story-script export command:

```powershell
.\.venv\Scripts\python.exe tools/export_script_table.py --glyph-map local/work/dialogue_glyph_map.csv local/work/mcd3_entries/DATA003/1089_bin.bin local/work/script_DATA003_1089_dialogue_seeded.json
```

Current result: 1,174 rows from `DATA003` entry `1089`; 319 are readable script commands and 855 are glyph rows. The generated JSON is ignored local data.

`#start 6F` current page structure:

| Page | Records | Commands | Glyph row lengths |
| ---: | --- | --- | --- |
| setup | `275-283` | `#start 6F`, `#bgm 21`, `#readbg 4`, `#readwait`, fades/wait, `#center 1` | `10` |
| 0 | `284-299` | `#page`, `#left 32`, `#color 255,215,92` | `7, 19, 21, 19, 16, 19, 10, 11, 13, 10, 13, 16, 14` |
| 1 | `300-312` | `#page`, `#white`, `#center 1` | `27, 33, 34, 30, 27, 30, 22, 26, 34` |
| 2 | `313-322` | `#page` | `18, 35, 16, 30, 29, 9, 33, 33` |
| 3 | `323-334` | `#page`, `#left 32`, `#color 255,215,92` | `7, 18, 17, 14, 21, 9, 14, 10, 24` |
| 4 | `335-341` | `#page`, `#center 1`, `#white`, `#end`, `#end` | `32` |

Known story glyph-code anchor from record `306`:

```text
0x0276 0x024c 0x0270 0x0227 0x024c 0x011c 0x011c 0x011c
マ      タ      、      キ      タ      ー      ー      ー
```

## USA Reference Alignment

The ignored local USA extract is available only as reference material. The Japanese dump remains the patch target. Do not commit generated USA extraction or alignment files because they can contain copyrighted English text.

Confirmed `DATA001` offset-table mappings:

| Japanese table | USA reference table | Current role |
| --- | --- | --- |
| `DATA001/0003` | `DATA001/0009` | Boot/init UI table |
| `DATA001/0008` | `DATA001/0017` | Live tutorial/objective overlay table |
| `DATA001/0012` | `DATA001/0022` | Story/dialogue table |
| `DATA001/0015` | `DATA001/0026` | Large UI/text table |
| `DATA001/0016` | `DATA001/0027` | Menu/UI label table |
| `DATA001/0017` | `DATA001/0028` | Help/manual table |

Generated local alignment reports:

| Alignment report | Rows | Fits current same-size budget | Does not fit |
| --- | ---: | ---: | ---: |
| `local/work/align_JP0003_USA0009_boot_ui.json` | 14 | 0 | 14 |
| `local/work/align_JP0008_USA0017_tutorial.json` | 8 | 0 | 8 |
| `local/work/align_JP0012_USA0022_story.json` | 226 | 4 | 222 |
| `local/work/align_JP0015_USA0026_ui.json` | 672 | 207 | 465 |
| `local/work/align_JP0016_USA0027_ui.json` | 297 | 145 | 152 |
| `local/work/align_JP0017_USA0028_help.json` | 103 | 14 | 89 |

Interpretation: the record/run alignment is strong for the matched `DATA001` tables, but official English text is often longer than the Japanese run budget. The safe importer can already make concise playable replacements; full-length reference text needs either shorter writing, page/layout changes, or a future offset-table/archive resizing workflow.

## Completed Survey Targets

| Target | Result | Decision |
| --- | --- | --- |
| `DATA000.BIN` / `MCD3` | Parsed and extracted 189 non-empty entries with manifest | Supporting |
| All non-empty `MCD3` entries | Classified by format hint and string previews | Supporting |
| `DATA001.BIN` entry `2` / `.TDL` | 12 `MIG` font/code-page children | Translation-relevant support |
| `MIG.00.1PSP` font-page children | 128x128 4bpp paletted texture pages | Translation-relevant support |
| Runtime tutorial/menu phrases | No exact UTF-8, Shift-JIS/CP932, or EUC-JP hits | Text likely encoded/compressed/indexed |
| Runtime equipment/status UI | Uses same `codeJAP14x14` atlas pages for visible labels | Confirms font atlas covers UI text |
| `DATA001` offset tables | Parsed as `u32 word0`, `u32 count`, `u32 offsets[count]`, records with length-prefixed text/glyph-code runs | Confirmed text/layout containers |
| `DATA001` entry `12` | Confirmed 4F boss / Briareos dialogue records `140-143` and `160-174` | Translation-relevant target |
| `DATA001` entry `8` | Confirmed live in-stage tutorial/objective overlay table | Translation-relevant target |
| `DATA001` entry `3` | Runtime marker `A00` appears on init loading before the main title | UI/boot text target |
| `DATA001` entry `16` | Runtime marker `E01` appears on the input-key info/help overlay | UI/help text target |
| `DATA002` entry `65` | Offset table with 702 records; appears to contain game text/data labels and glyph rows | Translation-relevant candidate |
| `DATA002` entry `65`, records `82` and `84` | Runtime markers `G1E` and `G1F` appear on the new-game player-name input screen | UI/name-input text target |
| `DATA003` entry `1089` | Offset table with 1499 records; confirmed story script command table | Translation-relevant target |
| `DATA001.BIN` entries `10`, `11` / `PACK0001` | Object/model packs containing `OMG` children such as `item_obj001` | Asset/media |
| `DATA004.BIN` / `MSCR` | Map/scene bundles with embedded `.TDL` resource tables | Asset/media for now |
| `PARAM.SFO` | Contains title `煉獄弐 - The Stairway to H.E.A.V.E.N.` | Metadata, optional translation target |
| `EBOOT.BIN` | Packed PSP executable, high entropy, no useful plain strings found | Defer |
| `BOOT.BIN` | All zeroes in this extract | Ignore |

## Format Decisions

| Format | Survey Result | Next Action |
| --- | --- | --- |
| `MCD3` | Stable top-level index, parser and extractor implemented | Use as archive backbone |
| `.TDL` | Resource table with 24-byte rows: name, size, offset | Use for child extraction |
| `MIG.00.1PSP` | Font-page samples are 128x128 4bpp paletted texture resources | Decode/render glyph sheets next |
| `PACK0001` | 16-byte table rows containing child object/model resources | No translation work now |
| `MSCR` | Scene/map bundle; embeds `.TDL` at `0x30`; names are map assets | No translation work now |
| `OMG.00.1PSP` | Model/object data based on names and context | Defer |
| `PSMF` | PSP video stream/media | Ignore |
| `RIFF` | Audio/media | Ignore |
| `VAGp` | Audio/media | Ignore |
| `PNG` | Image/media | Ignore except visible graphics later |
| `PBP` | Embedded PSP package/update-like payload | Ignore |

## Local Generated Survey Data

Generated files are under ignored `local/work/`:

```text
local/work/mcd3_entries/
local/work/tdl_DATA001_0002/
local/work/pack_DATA001_0010/
local/work/pack_DATA001_0011/
```

These are local analysis products and must not be committed.

## Actual Next Phase

Continue practical edit/rebuild tests:

1. Same-length ASCII UI replacement is confirmed in PPSSPP: `DATA001` entry `16`, record `56`, changes `HELP` to `TEST`.
2. PPSSPP can launch the staged extracted folder directly, so ISO rebuild is not required for fast local smoke tests.
3. Glyph-code/mixed-run replacement is confirmed in PPSSPP: `DATA001` entry `17`, records `30` and `42`, change embedded help-page `HELP` labels to `TEST`.
4. Confirmed staged folder: `local/rebuilt/help_to_test_plus_help_page_extracted/`.
5. First tutorial probe at `local/rebuilt/tutorial_probe_extracted/` missed the 0F tutorial overlay and bottom prompt. It replaced selected candidate rows with tags `T3A`, `T65A`, `T65B`, `T1089A`, and `T1089B`.
6. Second tutorial probe at `local/rebuilt/tutorial_probe2_extracted/` also missed. It focused on `DATA001` entry `16`, records `86-92`, and `DATA001` entry `17`, records `12`, `30`, `38`, `42`, `57`, `91`, `97`, `99`, and `101`.
7. Third tutorial probe at `local/rebuilt/tutorial_probe3_extracted/` changed menu/tutorial-help text but did not affect the live 0F overlay. It broadened to `DATA001` entries `8`, `12`, and `15`.
8. Fourth tutorial probe at `local/rebuilt/tutorial_probe4_extracted/` missed the live 0F overlay. It marked every glyph row in `DATA003` entry `1089` script sections `#start 01A`, `#start 02A`, and `#start 03A`.
9. Fifth tutorial probe at `local/rebuilt/tutorial_probe5_extracted/` also missed. It marked the remaining `DATA003/1089` script sections: `#start 2F-8F` and `#start 04A-09A`.
10. Sixth tutorial probe is staged at `local/rebuilt/tutorial_probe6_extracted/`. It marks every patchable glyph-code row in all currently parsed non-script text tables: `DATA001` entries `3`, `8`, `12`, `15`, `16`, `17`, and `DATA002` entry `65`.
11. Sixth tutorial probe result: `DATA001` entry `8` owns the live in-stage tutorial/objective overlay. Confirmed runtime markers:
    - `B01` / record `10`: 0F bottom objective prompt state.
    - `B02` / record `11`: 0F bottom objective prompt state.
    - `B1C` / record `66`: 1F attack tutorial title.
    - `B1D` / record `67`: 1F attack tutorial body.
    - `B1E` / record `68`: 1F lock-on tutorial title.
    - `B1F` / record `69`: 1F lock-on tutorial body.
    - `B1G` / record `70`: 0F movement tutorial title.
    - `B1H` / record `71`: 0F movement tutorial body.
12. A focused English tutorial probe is staged at `local/rebuilt/live_tutorial_english_extracted/`. It changes only `DATA001` entry `8`, records `10`, `11`, and `66-71`, using same-size or shorter ASCII glyph-code replacements.
13. The broad probe also changed start menu and new-game name-prompt text via other marked tables, especially `DATA002` entry `65`. Treat those as separate UI targets from the live tutorial overlay.
14. Additional confirmed broad-probe UI anchors:
    - `A00` -> `DATA001` entry `3`, record `0`: init loading screen before the main title.
    - `E01` -> `DATA001` entry `16`, record `12`: input-key info/help overlay.
    - `G1E` -> `DATA002` entry `65`, record `82`: new-game player-name input screen.
    - `G1F` -> `DATA002` entry `65`, record `84`: new-game player-name input screen.
15. USA reference alignment is now available for the confirmed `DATA001` tables. Use `tools/align_reference_text.py` to create ignored local comparison reports. The next implementation target is a translator-facing table for `DATA001/0008` that includes source record IDs, max code units, USA reference text, and concise replacement fields.

This is the right next phase because raw string scans did not reveal obvious dialogue text, but the offset-table and glyph-map workflow now decodes a complete boss scene from game data.
