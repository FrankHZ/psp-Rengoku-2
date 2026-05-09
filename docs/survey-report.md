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

Start the glyph-map and text-container phase:

1. Expand `samples/glyph_map_seed.csv` from exported glyph-cell PNGs and runtime screenshots until Japanese UI entries decode into meaningful strings.
2. Use `tools/extract_text.py --format offset-table-runs --glyph-map ...` as the translator-facing export path for `DATA001` offset tables.
3. Implement a reversible importer for edited same-length or rebuilt offset-table records, then test on a copy.

This is the right next phase because raw string scans did not reveal obvious dialogue text. The game may use indexed text, compressed script data, or executable-driven tables, and font mapping will tell us what encodings and glyph ranges are actually supported.
