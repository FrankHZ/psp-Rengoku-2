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
- Starts with little-endian values followed by ASCII magic/name `MCD3`.
- Contains the names `DATA001.BIN` through `DATA005.BIN` at offsets `0x0C` through `0x50`.
- Likely an index, manifest, or table describing the other data blobs.

Text encoding:
- Plain ASCII file names confirmed.

String layout:
- File names appear as 16-byte null-padded slots.

Pointer layout:
- Unknown. Data after `0x60` appears table-like and may contain offsets, sizes, alignment, or flags.

Mutation rules:
- Unknown. Treat as read-only until parsed.

Verification:
- `tools/scan_text.py` finds only the archive file names and a few noisy short candidates.

Unknowns:
- Meaning of the first fields.
- How table rows map to `DATA001.BIN` through `DATA005.BIN`.

## DATA001.BIN

Files:
`PSP_GAME/USRDIR/DATA001.BIN`

Evidence:
- Starts with ASCII magic/version-like string `MIG.00.1PSP`.
- Header is followed by structured binary records.

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
- Contains embedded `.TDL` marker near offset `0x30`.
- Name suggests a strong candidate for mission/script or game script data, but this is only an inference from the magic.

Text encoding:
- Unknown.

String layout:
- Unknown.

Pointer layout:
- Unknown.

Mutation rules:
- Unknown. This is a priority candidate for read-only analysis.

Verification:
- Header inspected with `Format-Hex`.

Unknowns:
- Whether `MSCR` means script, and whether dialogue/menu text lives here.
- Header fields, offsets, compression, checksums, and alignment.

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
