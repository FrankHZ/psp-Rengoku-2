# Early-Stage Report

Date: 2026-05-09

Status: Superseded by `docs/survey-report.md`.

Target: Rengoku 2 PSP extracted ISO at `local/extracted/Rengoku 2/`

This report summarizes the first read-only analysis pass. It intentionally avoids extraction or mutation of game assets.

## Stop Condition For This Pass

This pass is enough to stop when:

- The top-level archive/index layout is reproducibly described.
- We can identify which large files are archives and which are likely media/assets.
- We have one concrete next parser target that is more useful than blind string scanning.
- The tooling and tests are updated so future observations are repeatable.

That condition is now met.

## Confirmed Layout

The PSP ISO has a standard layout:

```text
UMD_DATA.BIN
PSP_GAME/
  PARAM.SFO
  SYSDIR/
  USRDIR/
    DATA000.BIN
    DATA001.BIN
    DATA002.BIN
    DATA003.BIN
    DATA004.BIN
    DATA005.BIN
    DLL/*.prx
```

`DATA000.BIN` is an `MCD3` index for `DATA001.BIN` through `DATA005.BIN`.

Observed `MCD3` fields:

```text
header_size   0x60
archive_count 5
entry_count   3155
entry_size     16 bytes
```

Only 189 of 3155 entries are non-empty. The remaining 2966 are empty slots.

The selector field maps entries to archives like this:

```text
0x08000 -> DATA001.BIN
0x18000 -> DATA002.BIN
0x28000 -> DATA003.BIN
0x38000 -> DATA004.BIN
0x48000 -> DATA005.BIN
```

All non-empty entry ranges are inside their referenced archive files.

## Archive Entry Summary

Top-level `MCD3` entry classification:

```text
MIG   45
MSCR  45
RIFF  44
OMG   21
other  9
PSMF   8
TDL    8
PNG    5
PACK   2
VAGp   1
PBP    1
```

Per archive:

```text
DATA001.BIN: MIG 1, OMG 1, PACK 2, PSMF 1, RIFF 1, TDL 6, VAGp 1, other 7
DATA002.BIN: MIG 36, PBP 1, PNG 5, PSMF 7, RIFF 43, TDL 1, other 1
DATA003.BIN: MIG 8, OMG 1, TDL 1, other 1
DATA004.BIN: MSCR 45
DATA005.BIN: OMG 19
```

## Current Interpretation

`DATA000.BIN` is the first format we should support formally. It gives us stable entry IDs, archive names, offsets, and sizes. This should become the backbone for future extraction.

`DATA004.BIN` initially looked like the strongest script candidate because every entry starts with `MSCR`, but the entry inventory suggests it is mostly map/scene asset bundles. Its ASCII strings are names such as:

```text
map_wall04
map_gokou00
map_hdoor00
map_parts01
F5_door0
map_bg_001a
```

So `MSCR` may mean map scene/resource rather than message script. It may still contain important in-game resource names, but it is not yet a high-confidence dialogue target.

`DATA001.BIN` has a more interesting translation lead:

```text
entry 2: .TDL, strings include codeANK9x14_00_0, codeJAP14x14_00_, codeJAP14x14_02_
```

This likely relates to fonts or text rendering. Understanding this entry may tell us how Japanese glyphs are stored and which encodings the game expects.

`EBOOT.BIN` has very high entropy and no useful plain-text strings in the quick inventory. Treat it as packed/encrypted/compressed PSP executable content for now, not a first target.

## String Scan Findings

Raw ASCII scans mostly find:

- Archive names.
- Asset names.
- Font/resource names.
- Media/container magic.
- Binary false positives.

Raw Shift-JIS scans are currently noisy. The scanner can find byte runs that decode as Shift-JIS, but most hits look like accidental decodes from binary data rather than real prose. We should not export translations from raw Shift-JIS scans yet.

## Tools Added

- `tools/mcd3.py`: read-only parser for the `MCD3` index.
- `tools/inspect_mcd3.py`: summarizes archive entry counts, bounds, and sample headers.
- `tools/extract_mcd3_entries.py`: extracts non-empty `MCD3` entries into ignored local work folders with a manifest.
- `tools/archive_entry_inventory.py`: inventories all non-empty `MCD3` entries by header, entropy, format hint, and ASCII preview.
- `tools/binary_inventory.py`: lightweight file-level binary inventory.
- `tools/tdl.py` and `tools/inspect_tdl.py`: parse preliminary `.TDL` resource containers.
- `tools/pack0001.py` and `tools/inspect_pack0001.py`: parse preliminary `PACK0001` resource containers.

Existing scanner improvements:

- Faster encoded scanning on real binary files.
- UTF-8 console output handling.
- Optional `--encoding` selection.
- Optional `--require-japanese` filter.
- Quiet exit when command output is intentionally truncated by a pipe.

## Additional Survey Results

`MCD3` entry extraction now writes 189 non-empty entries to:

```text
local/work/mcd3_entries/
```

with:

```text
local/work/mcd3_entries/manifest.json
```

`DATA001.BIN` entry `2` is a `.TDL` container with 12 child resources. All children are 8464-byte `MIG.00.1PSP` resources named:

```text
codeANK9x14_00_0
codeJAP14x14_00_
codeJAP14x14_02_
...
codeJAP14x14_20_
```

This is a strong font/glyph-page lead, not a dialogue table by itself.

`DATA001.BIN` entries `10` and `11` are `PACK0001` containers. They contain `OMG.00.1PSP` child resources with names like:

```text
dummy_00
dummy_01
item_obj001
item_obj002
...
item_obj010
```

These appear to be object/model packs and are not high-confidence text targets.

## Actual Next Step

Build a minimal `MIG` inspector for the font-page resources extracted from `DATA001.BIN` entry `2`:

```text
local/work/tdl_DATA001_0002/
  0000_codeANK9x14_00_0.bin
  0001_codeJAP14x14_00_.bin
  ...
```

The goal is to determine whether `MIG.00.1PSP` is a texture/image format we can decode into glyph sheets. If yes, the next phase can inspect font coverage and rendering constraints. If no, survey should pivot to executable references and other data entries.

Translation extraction should still wait. We have not yet found high-confidence prose/dialogue strings.

See `docs/survey-targets.md` for the full survey checklist and stop criteria.
