# Survey Targets

The survey phase is complete when every target below has a read-only classification, enough header/table notes to choose the next parser, and a clear decision: `translation-relevant`, `supporting`, `asset/media`, or `defer`.

Current status: complete enough to stop. See `docs/survey-report.md`.

Do not edit or reinsert data during the survey phase.

## Primary Targets

These directly affect text extraction or the structure needed to reach text.

| Target | Current Lead | Stop Criteria |
| --- | --- | --- |
| `DATA000.BIN` / `MCD3` | Top-level archive index | Done: entry table parsed, archive mapping confirmed, extractor manifest implemented |
| `DATA001.BIN` entry `2` / `.TDL` | Font/text-rendering lead: `codeANK9x14`, `codeJAP14x14` | Done: 12 `MIG` child resources identified as 128x128 4bpp font/code-page textures |
| `DATA001.BIN` entries `10`, `11` / `PACK0001` | Possible object/item packs | Done at container level: object/model packs with `dummy_*` and `item_obj*`; not high-confidence text |
| `PARAM.SFO` | PSP metadata/title | Done: contains title `煉獄弐 - The Stairway to H.E.A.V.E.N.`; optional metadata target |
| `EBOOT.BIN` / `BOOT.BIN` | Executable text/code possibility | Done: `EBOOT.BIN` high entropy with no useful plain strings; `BOOT.BIN` all zeroes; defer executable analysis |

## Archive Entry Targets

These are all non-empty entries referenced by `DATA000.BIN`.

| Archive | Entry IDs | Count | Survey Goal |
| --- | ---: | ---: | --- |
| `DATA001.BIN` | `0`-`19` | 20 | Classify mixed UI/font/audio/model/container entries |
| `DATA002.BIN` | `64`-`157` | 94 | Classify media/image/model entries and rule out obvious text containers |
| `DATA003.BIN` | `1088`-`1098` | 11 | Classify `OMG`/`MIG`/`.TDL` model or asset bundles |
| `DATA004.BIN` | `2112`-`2156` | 45 | Classify `MSCR` scene/map bundles and decide if any contain text-bearing tables |
| `DATA005.BIN` | `3136`-`3154` | 19 | Classify `OMG` boss/model bundles |

## Format Targets

Each observed format should have a small read-only note before survey ends.

| Format | Seen In | Stop Criteria |
| --- | --- | --- |
| `MCD3` | `DATA000.BIN` | Done: parsed with tests and extractor |
| `.TDL` | `DATA001`, `DATA002`, `DATA003`, embedded in `MSCR` | Done for survey: header fields identified enough to list child resources |
| `PACK0001` | `DATA001` entries `10`, `11` | Done: entry table parsed; contained object/model names listed |
| `MIG.00.1PSP` | Many entries, especially font-page children | Done for survey: font-page samples are 128x128 4bpp paletted texture resources |
| `MSCR` | `DATA004` entries `2112`-`2156` | Done for survey: embeds `.TDL` at `0x30`; map/scene resource names; asset/media for now |
| `MIG.00.1PSP` | Many entries | Classified as image/model/font resource data; next phase only for font rendering |
| `OMG.00.1PSP` | `DATA003`, `DATA005`, some `DATA001` | Classified as model/animation/other; no need for full parser unless it contains text |
| `PSMF` | `DATA001`, `DATA002` | Classified as video/media |
| `RIFF` | `DATA001`, `DATA002` | Classified as audio/media |
| `VAGp` | `DATA001` | Classified as audio/media |
| `PNG` | `DATA002` and PSP root assets | Classified as image/media |
| `PBP` | `DATA002` entry `66` | Classified; likely embedded updater or PSP package |

## Text Signal Targets

Survey should answer these before extraction begins:

- Where are high-confidence user-facing strings, if any?
- Are strings raw Shift-JIS, UTF-8, ASCII, table encoded, or rendered from image/font resources?
- Are menu/item/system strings in data archives, executable code, or both?
- Does the game use fixed-width font pages that constrain translation length/rendering?
- Are there pointer tables, length tables, or compressed containers between us and text?

## Survey Stop Checklist

Stop the survey phase when all of these are true:

- `MCD3` extraction is implemented read-only into `local/work/mcd3_entries/`. Done.
- Every non-empty `MCD3` entry has a manifest row with ID, archive, offset, size, format hint, and sample strings. Done.
- `.TDL`, `PACK0001`, and `MSCR` each have at least a preliminary header/table note. Done.
- Known media-only formats are marked as `asset/media` and not pursued further. Done.
- At least one high-confidence translation target is identified, or the report states that the next phase must investigate executable/font rendering before text extraction. Done: next phase is font/rendering.
- No original ROM, extracted asset, rebuilt ROM, or generated entry dump is tracked by git.
