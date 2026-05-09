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
| `DATA002` entry `65` | Offset table with 702 records; appears to contain game text/data labels and glyph rows | Translation-relevant candidate |
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

Start the story extraction/import phase:

1. Continue extending `samples/story_glyph_map_seed.csv` from known scenes in `DATA001/0012` and related text tables.
2. Keep `tools/export_script_table.py` for command/control context in `DATA003/1089`, preserving command rows and `#start` context.
3. Design a reversible importer for edited same-length or rebuilt offset-table records, then test on a copy of `DATA001/0012`.

This is the right next phase because raw string scans did not reveal obvious dialogue text, but the offset-table and glyph-map workflow now decodes a complete boss scene from game data.
