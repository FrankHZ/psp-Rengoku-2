# Detected File Formats

These notes are evidence logs, not final specifications. Do not build irreversible import logic from them until the fields are confirmed with tests and binary diffs.

## ISO Layout

Files:
`local/extracted/Rengoku 2/`

Evidence:
- Standard PSP layout with `UMD_DATA.BIN`, `PSP_GAME/PARAM.SFO`, `PSP_GAME/SYSDIR`, and `PSP_GAME/USRDIR`.
- Game data is concentrated in `PSP_GAME/USRDIR/DATA000.BIN` through `DATA005.BIN`.
- `SYSDIR/UPDATE` appears to be PSP firmware update data and is not a translation target.

Unknowns:
- Exact rebuild requirements and whether file ordering/LBA positions matter for this title.

## DATA000.BIN

Files:
`PSP_GAME/USRDIR/DATA000.BIN`

Evidence:
- Starts with little-endian fields followed by ASCII magic `MCD3` at offset `0x0C`.
- Header fields observed: `header_size = 0x60`, `archive_count = 5`, `entry_count = 3155`.
- Contains the names `DATA001.BIN` through `DATA005.BIN` at offsets `0x10` through `0x50`.
- After the header, contains 3155 fixed-size 16-byte entries.
- 189 entries are non-empty; 2966 entries are empty.
- Non-empty entries map cleanly into `DATA001.BIN` through `DATA005.BIN`.

Text encoding:
- Plain ASCII file names confirmed.

String layout:
- File names appear as 16-byte null-padded slots.

Pointer layout:
- Each entry is four little-endian `u32` values: `selector`, `size`, `offset`, `stored_size`.
- `offset` and `size` point into the selected `DATA00*.BIN` archive.
- `stored_size` currently matches `size` for observed entries.
- Selector mapping observed:
  - `0x08000` -> `DATA001.BIN`
  - `0x18000` -> `DATA002.BIN`
  - `0x28000` -> `DATA003.BIN`
  - `0x38000` -> `DATA004.BIN`
  - `0x48000` -> `DATA005.BIN`

Mutation rules:
- Unknown. Treat as read-only until parsed.

Verification:
- `tools/inspect_mcd3.py` confirms all non-empty entries stay inside their archive file bounds.
- `tools/scan_text.py` finds only the archive file names and a few noisy short candidates.

Unknowns:
- Meaning of the selector high bits beyond archive selection.
- Whether `stored_size` can differ from `size` for compressed entries in other builds.
- Whether empty ID gaps carry semantic meaning.

## DATA001.BIN

Files:
`PSP_GAME/USRDIR/DATA001.BIN`

Evidence:
- Starts with ASCII magic/version-like string `MIG.00.1PSP`.
- Header is followed by structured binary records.
- `MCD3` entry `2` is a `.TDL` container with 12 `MIG.00.1PSP` children named like font/code pages.
- `MCD3` entries `10` and `11` are `PACK0001` object/model containers.

Text encoding:
- Unknown.

String layout:
- Unknown.

Pointer layout:
- Unknown.

Mutation rules:
- Unknown. Treat as packed asset data until parsed.

Verification:
- Header inspected with `Format-Hex`.

Unknowns:
- Whether `MIG` is a container, image/model format, or game-specific package.

## .TDL

Files:
Observed as `MCD3` entries such as `DATA001.BIN` entry `2`.

Evidence:
- Starts with ASCII magic `.TDL`.
- Header appears to be `<4s magic, u32 entry_count, u32 declared_data_size, u32 flags_or_reserved>`.
- Child table starts at `0x10`.
- Child rows are 24 bytes: 16-byte null-padded ASCII name, `u32 size`, `u32 offset`.
- `DATA001` entry `2` contains 12 child resources named `codeANK9x14_00_0` and `codeJAP14x14_*`.

Text encoding:
- Confirmed ASCII resource names.

String layout:
- 16-byte null-padded child names.

Pointer layout:
- Child offsets are relative to the start of the `.TDL` file.

Mutation rules:
- Unknown. Treat as read-only until child formats are understood.

Verification:
- `tools/inspect_tdl.py` parses `DATA001` entry `2` and extracts all 12 children.

Unknowns:
- Meaning of `flags_or_reserved`.
- Whether all `.TDL` entries use the same row layout.

## PACK0001

Files:
Observed as `DATA001.BIN` entries `10` and `11`.

Evidence:
- Starts with ASCII magic `PACK0001`.
- Header includes entry count and table offset.
- Child table rows are 16 bytes: `u32 offset`, reserved zero, `u32 size`, reserved zero.
- Entries `10` and `11` contain `OMG.00.1PSP` child resources with names such as `dummy_00`, `item_obj001`, and `item_obj010`.

Text encoding:
- Confirmed ASCII model/object resource names.

String layout:
- No high-confidence user-facing text found.

Pointer layout:
- Child offsets are relative to the start of the `PACK0001` file.

Mutation rules:
- Unknown. Treat as read-only object/model packs.

Verification:
- `tools/inspect_pack0001.py` parses entries `10` and `11`.

Unknowns:
- Whether this format appears elsewhere with non-model payloads.

## DATA002.BIN

Files:
`PSP_GAME/USRDIR/DATA002.BIN`

Evidence:
- Starts with `.TDL`.
- Early ASCII labels include `lobbyBg` and `parts`.
- Largest data file in the ISO.

Text encoding:
- Unknown. Early labels are ASCII asset identifiers.

String layout:
- Unknown.

Pointer layout:
- Unknown.

Mutation rules:
- Unknown.

Verification:
- Header inspected with `Format-Hex`.

Unknowns:
- Whether `.TDL` is a top-level archive or embedded asset format.

## DATA003.BIN

Files:
`PSP_GAME/USRDIR/DATA003.BIN`

Evidence:
- Starts with ASCII magic/version-like string `OMG.00.1PSP`.
- ASCII scan mostly returns noisy binary-looking runs plus asset names such as `ch00_00H.tm2`.

Text encoding:
- Unknown.

String layout:
- Unknown.

Pointer layout:
- Unknown.

Mutation rules:
- Unknown.

Verification:
- Header inspected with `Format-Hex`.
- ASCII scan performed with `tools/scan_text.py`.

Unknowns:
- Whether `OMG` is a model/graphics container.

## DATA004.BIN

Files:
`PSP_GAME/USRDIR/DATA004.BIN`

Evidence:
- Starts with ASCII magic `MSCR`.
- `MCD3` maps 45 entries into this file, and all 45 start with `MSCR`.
- Each observed `MSCR` entry declares a size matching its `MCD3` entry size.
- Contains embedded `.TDL` marker at offset `0x30`; inspected entries parse as `.TDL` resource tables.
- ASCII previews are mostly map/scene asset names such as `map_wall04`, `map_hdoor00`, `F5_door0`, and `map_bg_001a`.

Text encoding:
- No high-confidence dialogue text found yet.
- Confirmed ASCII asset names.

String layout:
- Unknown.

Pointer layout:
- Unknown.

Mutation rules:
- Unknown. Treat as read-only map/scene resource data until the internal section table is parsed.

Verification:
- Header inspected with `Format-Hex`.
- `tools/inspect_mscr.py` confirms inspected entries embed `.TDL` resource tables with map/scene asset names.

Unknowns:
- Whether `MSCR` means map scene/resource rather than message script.
- Header fields, offsets, compression, checksums, and alignment.

## MIG.00.1PSP

Files:
Observed throughout `MCD3` entries and inside `.TDL` containers.

Evidence:
- Font/code-page children from `DATA001` entry `2` are all 8464 bytes.
- Each has three 16-byte internal records after the magic.
- Font/code-page samples are 128x128, 4bpp, paletted texture-like resources.
- Observed palette offset: `0x80`.
- Observed pixel/index offset: `0x110`.
- Observed pixel/index data size: `8192` bytes.
- Pixel data is PSP-swizzled in 16-byte by 8-row blocks.
- Current exporter default treats embedded palette bytes as `rgba`; alternate `abgr` and `bgra` modes are available for experiments.

Text encoding:
- No text strings expected; this appears to be texture/glyph image data.

String layout:
- Not applicable except parent `.TDL` resource names.

Pointer layout:
- Preliminary only. Internal record fields need more work before mutation.

Mutation rules:
- Unknown. Treat as read-only until texture decode/re-encode is proven.

Verification:
- `tools/inspect_mig.py` identifies all 12 font/code-page children as 128x128 4bpp resources.
- `tools/export_mig_png.py` exports legible static font pages after unswizzling.
- `tools/map_runtime_font_pages.py` maps PPSSPP texture dump addresses to static font pages by `0x2100` address stride.
- `tools/analyze_font_grid.py` confirms `codeANK9x14` uses a 14x9 grid and `codeJAP14x14` uses 9x9 grids.
- `pixel_offset=0x110` is confirmed against PPSSPP dumped textures; the earlier `0x100` guess included a 16-byte descriptor and caused cracked glyphs.
- `tools/export_glyph_cells.py` exports per-cell PNGs plus a manifest for glyph mapping work.

Unknowns:
- Exact runtime palette/CLUT variant behavior.
- Glyph cell ordering and mapping from encoded text to texture cells.

## DATA001 Offset Tables

Files:
`DATA001.BIN` MCD3 entries `3`, `8`, `12`, `15`, `16`, and `17`.

Evidence:
- No ASCII magic.
- Header shape is consistent: `u32 word0`, `u32 count`, then `count` little-endian `u32` offsets.
- `word0` is currently always `0`.
- The first record offset equals `8 + count * 4`.
- Offsets are sorted and point inside the same file.
- Records begin with repeated small values and include length-prefixed `u16` runs.
- Some runs are direct ASCII text stored as `u16` code units.
- Other runs are glyph-code streams that reference the font/code-page atlas.

Role:
- Confirmed text/layout container family.
- These entries are near the shared UI/font resources in `DATA001.BIN`.
- `DATA001` entry `16` contains visible UI/menu strings such as `GRAPPLE`, `SLASH`, `IMPACT`, `QUANTUM`, `BULLET`, `HEAT`, `EQUIP`, `BUILD`, `ITEM`, `FILE`, `OPTION`, `EXIT`, `HELP`, and floor labels.
- Screenshot Japanese phrases are not present as exact standard encoded strings because they are represented as glyph-code streams rather than plain Shift-JIS/UTF-8 text.

Mutation rules:
- Read-only until record commands and payload boundaries are understood.
- Any importer must preserve offsets or rebuild the table from record lengths.

Verification:
- `tools/inspect_offset_table.py` parses the current candidate entries.
- `tools/extract_offset_table_runs.py` extracts length-prefixed runs and identifies ASCII text runs.
- `tools/extract_text.py --format offset-table-runs` exports these runs to the normal translation JSON shape.
- `tools/extract_text.py --format offset-table-runs --glyph-map samples/glyph_map_seed.csv` performs partial Japanese glyph-code decoding for known glyph IDs.
- `samples/glyph_map_seed.csv` is a repo-safe, manually seeded `code,char` table. It is intentionally incomplete and should grow from screenshots plus exported glyph-cell images.
- `local/work/offset_table_runs_DATA001_candidates.json` is an ignored generated extraction report.
- `local/work/extract_text_DATA001_0016_seeded.json` is an ignored generated seeded export for the currently confirmed UI table.

Unknowns:
- Record command structure.
- Exact meaning of control fields before text runs.
- Full glyph-code map for Japanese runs.
- Rebuild rules for changed run lengths.

## PARAM.SFO

Files:
`PSP_GAME/PARAM.SFO`

Evidence:
- Contains PSP metadata fields such as `DISC_ID`, `TITLE`, and `PSP_SYSTEM_VER`.
- Title string found: `煉獄弐 - The Stairway to H.E.A.V.E.N.`

Mutation rules:
- Optional metadata translation target; do not edit until rebuild workflow is stable.

## Executables

Files:
`PSP_GAME/SYSDIR/EBOOT.BIN`, `PSP_GAME/SYSDIR/BOOT.BIN`

Evidence:
- `EBOOT.BIN` starts with `~PSP`, has high entropy, and quick scans show no useful plain strings.
- `BOOT.BIN` is all zeroes in this extraction.

Mutation rules:
- Defer executable work until data/font survey results require it.

## DATA005.BIN

Files:
`PSP_GAME/USRDIR/DATA005.BIN`

Evidence:
- Starts with ASCII magic/version-like string `OMG.00.1PSP`.
- Early ASCII asset label `BossH01_ALL`.

Text encoding:
- Unknown.

String layout:
- Unknown.

Pointer layout:
- Unknown.

Mutation rules:
- Unknown.

Verification:
- Header inspected with `Format-Hex`.

Unknowns:
- Relationship to `DATA003.BIN`, which has the same `OMG.00.1PSP` header.

Use this file as the logbook for evidence. For each candidate file type, record:

- Path pattern or extension.
- Magic bytes, headers, or version fields.
- Encoding evidence.
- String termination or length rules.
- Pointer table location and pointer math, if known.
- Compression, encryption, checksums, or alignment requirements.
- Tools or scripts used to inspect it.
- Open questions.

## Template

```text
Format name:
Files:
Evidence:
Text encoding:
String layout:
Pointer layout:
Mutation rules:
Verification:
Unknowns:
```
