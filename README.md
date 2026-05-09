# PSP ROM Translation Workspace

This repository contains scripts, tests, and notes for analyzing and translating text from a legally obtained PSP game dump.

Current project target: a Simplified Chinese translation patch for Rengoku 2. English text from the USA release is used only as ignored local reference material for alignment and translation drafting.

Do not commit copyrighted game files, extracted assets, rebuilt images, or generated binary patches. Keep those files in local paths such as `input/`, `work/`, or `out/`, which are ignored by git.

## Workflow

1. Keep the legally obtained original PSP ISO/CSO outside this repository.
2. Manually unpack a copy of the ISO/CSO with an external tool.
3. Inspect the extracted files and record observations in `docs/formats.md`.
4. Identify likely text containers by scanning for ASCII, UTF-8, and Shift-JIS strings.
5. Export candidate text entries to JSON.
6. Edit the JSON translation fields.
7. Import edited text into a copy of the source file.
8. Rebuild the ISO with external tools.
9. Test the rebuilt image in PPSSPP.
10. Document every confirmed format, failed assumption, and unknown.

## Repository Layout

- `docs/`: assumptions, unknowns, and detected file format notes.
- `tools/`: small reversible command-line utilities.
- `tests/`: synthetic binary fixtures and round-trip tests.
- `samples/`: non-copyrighted toy samples and examples only.
- `patch/`: placeholder notes for patch generation workflow.
- `local/`: ignored local workspace for ROMs, emulator builds, unpacked files, and rebuilt images.

Recommended local-only layout:

```text
local/
  emulators/
    ppsspp_win/
  tools/
    UMDGen_v4/
  roms/
  extracted/
  work/
  rebuilt/
```

Everything under `local/` is ignored by git. Keep pristine original ROMs outside this repository, currently under `K:\Codes-roms\psp-roms`. Use `local/extracted/` for unpacked ISO contents, `local/work/` for modified file copies, `local/rebuilt/` for rebuild staging, and `local/roms/` only for rebuilt test images. Keep local helper programs such as PPSSPP and UMDGen under `local/emulators/` or `local/tools/`.

## Tools

The initial tools intentionally avoid assuming any game-specific format:

- `tools/scan_text.py` scans files for candidate text strings.
- `tools/extract_text.py` exports candidate text entries to JSON.
- `tools/import_text.py` imports edited JSON into a copy of a source file.
- `tools/make_patch.py` is a placeholder for future xdelta/PPF/BPS patch generation.
- `tools/inspect_mcd3.py` inspects the Rengoku 2 `DATA000.BIN` archive index.
- `tools/extract_mcd3_entries.py` extracts indexed entries into ignored local work folders with a manifest.
- `tools/archive_entry_inventory.py` inventories entries referenced by the `MCD3` index.
- `tools/binary_inventory.py` summarizes headers, entropy, markers, and ASCII strings.
- `tools/inspect_tdl.py` inspects `.TDL` resource containers.
- `tools/replace_tdl_child.py` replaces one same-size child inside a `.TDL` copy.
- `tools/replace_tdl_children.py` replaces multiple same-size children inside a `.TDL` copy.
- `tools/inspect_pack0001.py` inspects `PACK0001` resource containers.
- `tools/inspect_mig.py` inspects `MIG.00.1PSP` resources.
- `tools/export_mig_png.py` exports supported `MIG.00.1PSP` textures to PNG.
- `tools/export_glyph_cells.py` exports font atlas cells and glyph ID hypotheses for mapping work.
- `tools/copy_mig_font_cell.py` copies one compatible MIG font cell into another page.
- `tools/font_cell_inventory.py` inventories occupied and empty font cells for CHS glyph planning.
- `tools/patch_mig_font_cell.py` replaces one font atlas cell with a test pattern for glyph-code probes.
- `tools/stage_font_probe.py` stages ignored extracted-folder font probes from a JSON config.
- `tools/translation_char_inventory.py` counts unique characters needed by local CHS translation drafts.
- `tools/extract_offset_table_runs.py` extracts length-prefixed text/glyph-code runs from confirmed offset-table containers.
- `tools/decode_offset_table_text.py` applies a seed glyph map to offset-table records for survey/debug output.
- `tools/export_script_table.py` exports script-like offset-table rows with nearby `#start` command context.
- `tools/align_reference_text.py` aligns a source extraction JSON with an ignored local reference extraction by record/run and reports current length-budget fit.
- `tools/replace_mcd3_entry.py` replaces one same-size `MCD3` entry in a copied archive file.
- `tools/inspect_mscr.py` inspects `MSCR` map/scene resource bundles.
- `tools/runtime_texture_inventory.py` inventories PPSSPP dumped texture PNGs.
- `tools/map_runtime_font_pages.py` maps PPSSPP dumped font texture addresses back to extracted font pages.

For the current Rengoku 2 UI table lead, export a partial translator-facing JSON with:

```powershell
python tools/extract_text.py --format offset-table-runs --glyph-map samples/glyph_map_seed.csv local/work/mcd3_entries/DATA001/0016_bin.bin local/work/extract_text_DATA001_0016_seeded.json
```

For the confirmed 4F boss / Briareos dialogue slice, export the story table with:

```powershell
python tools/extract_text.py --format offset-table-runs --glyph-map samples/story_glyph_map_seed.csv local/work/mcd3_entries/DATA001/0012_bin.bin local/work/extract_text_DATA001_0012_story_seeded.json
```

The local USA extract can be used as an ignored reference source for alignment. Do not commit generated reference exports or alignment files because they may contain copyrighted English text. Current confirmed JP -> USA table mappings:

```text
JP DATA001/0003 -> USA DATA001/0009: boot/init UI table
JP DATA001/0008 -> USA DATA001/0017: live tutorial/objective overlay table
JP DATA001/0012 -> USA DATA001/0022: story/dialogue table
JP DATA001/0015 -> USA DATA001/0026: large UI/text table
JP DATA001/0016 -> USA DATA001/0027: menu/UI label table
JP DATA001/0017 -> USA DATA001/0028: help/manual table
```

Example local-only alignment command:

```powershell
python tools/align_reference_text.py local/work/extract_text_DATA001_0008_seeded_fresh.json local/work/usa_extract_text_DATA001_0017.json local/work/align_JP0008_USA0017_tutorial.json
```

The alignment report flags whether reference text fits the current same-size/shorter import budget. Many official English lines are longer than the Japanese slots, so full-length reference text will need either concise rewrites or future offset-table/archive resizing.

Current local smoke test:

```text
DATA001 entry 16, record 56: HELP -> TEST
```

This was confirmed in PPSSPP by launching the extracted folder directly. The patched archive copy is generated under ignored local work paths and staged at:

```text
local/rebuilt/help_to_test_extracted/
```

Second local smoke test:

```text
DATA001 entry 16, record 56: HELP -> TEST
DATA001 entry 17, records 30 and 42: embedded HELP tokens inside glyph-code help-page runs -> TEST
```

This was confirmed in PPSSPP on the help page. It is staged at:

```text
local/rebuilt/help_to_test_plus_help_page_extracted/
```

Current tutorial probe:

```text
local/rebuilt/tutorial_probe_extracted/
```

This is a diagnostic-only extracted tree for finding the first live tutorial text owner. It marks selected candidate glyph-code rows with short ASCII tags:

```text
T3A    DATA001 entry 3, record 2
T65A   DATA002 entry 65, record 86
T65B   DATA002 entry 65, record 88
T1089A DATA003 entry 1089, record 412
T1089B DATA003 entry 1089, record 702
```

If one of those tags appears in PPSSPP around the first tutorial overlay, the table and record are pinned.

Second tutorial probe after the first set missed the 0F tutorial:

```text
local/rebuilt/tutorial_probe2_extracted/
```

This focused probe targets the strongest `DATA001` UI/manual rows:

```text
16A..16G DATA001 entry 16, records 86..92
17A      DATA001 entry 17, record 12
17B      DATA001 entry 17, record 30
17C      DATA001 entry 17, record 38
17D      DATA001 entry 17, record 42
17E      DATA001 entry 17, record 57
17F      DATA001 entry 17, record 91
17G      DATA001 entry 17, record 97
17H      DATA001 entry 17, record 99
17I      DATA001 entry 17, record 101
```

Third tutorial probe after the second set also missed:

```text
local/rebuilt/tutorial_probe3_extracted/
```

This broadens the test to remaining high-signal `DATA001` offset tables:

```text
8A..8L   DATA001 entry 8, selected records 20, 21, 22, 23, 24, 36, 37, 49, 77, 79, 81, 83
12A..12I DATA001 entry 12, selected records 41, 45, 47, 61, 80, 81, 83, 84, 85
15A..15I DATA001 entry 15, selected records 20, 23, 31, 54, 59, 69, 79, 104, 114
```

The third probe changed menu/tutorial-help text but did not affect the live 0F overlay. This means the menu/help tutorial layer and in-stage tutorial layer are separate.

Fourth tutorial probe:

```text
local/rebuilt/tutorial_probe4_extracted/
```

This marks every glyph row in `DATA003` entry `1089` script sections `#start 01A`, `#start 02A`, and `#start 03A`:

```text
A00..A56 #start 01A
B00..B52 #start 02A
C00..C85 #start 03A
```

The local marker map is `local/work/tutorial_probe4_marker_map.json`.

Fifth tutorial probe after `01A-03A` missed:

```text
local/rebuilt/tutorial_probe5_extracted/
```

This marks the remaining `DATA003` entry `1089` script sections:

```text
D00..D0X #start 2F
E00..E0Y #start 3F
F00..F14 #start 4F
G00..G0O #start 5F
H00..H14 #start 6F
I00..I0N #start 7F
J00..J0H #start 8F
K00..K2F #start 04A
L00..L2X #start 05A
M00..M20 #start 06A
N00..N25 #start 07A
O00..O0P #start 08A
P00..P1V #start 09A
```

The local marker map is `local/work/tutorial_probe5_marker_map.json`.

Sixth tutorial probe after all `DATA003/1089` sections missed:

```text
local/rebuilt/tutorial_probe6_extracted/
```

This is a broad parsed-table probe. It marks every patchable glyph-code row in all currently parsed non-script text tables:

```text
Axx DATA001 entry 3
Bxx DATA001 entry 8
Cxx DATA001 entry 12
Dxx DATA001 entry 15
Exx DATA001 entry 16
Fxx DATA001 entry 17
Gxx DATA002 entry 65
```

The local marker map is `local/work/tutorial_probe6_marker_map.json`.

Confirmed `tutorial_probe6` result:

```text
DATA001 entry 8 owns the live in-stage tutorial/objective overlay.

B01 DATA001 entry 8, record 10: 0F bottom objective prompt state
B02 DATA001 entry 8, record 11: 0F bottom objective prompt state
B1C DATA001 entry 8, record 66: 1F attack tutorial title
B1D DATA001 entry 8, record 67: 1F attack tutorial body
B1E DATA001 entry 8, record 68: 1F lock-on tutorial title
B1F DATA001 entry 8, record 69: 1F lock-on tutorial body
B1G DATA001 entry 8, record 70: 0F movement tutorial title
B1H DATA001 entry 8, record 71: 0F movement tutorial body
```

The broad probe also changed start/menu/name-prompt strings via other marked tables, so use the focused tutorial test below for cleaner PPSSPP checks.

Other confirmed `tutorial_probe6` UI anchors:

```text
A00 DATA001 entry 3, record 0: init loading screen before the main title
E01 DATA001 entry 16, record 12: input-key info/help overlay
G1E DATA002 entry 65, record 82: new-game player-name input screen
G1F DATA002 entry 65, record 84: new-game player-name input screen
```

These are confirmed runtime surfaces, but they are separate from the live in-stage tutorial table.

Focused live tutorial English probe:

```text
local/rebuilt/live_tutorial_english_extracted/
```

This only replaces `DATA001` entry `8` in `DATA001.BIN`, with same-size or shorter ASCII glyph-code replacements:

```text
record 10, 11: USE TELEPORTER TO 1F
record 66: ATK!
record 67: attack tutorial body
record 68: LOCK!
record 69: lock-on tutorial body
record 70: MOVE
record 71: movement tutorial body
```

By default, import only supports same-size or shorter encoded strings. Shorter replacements are padded with null bytes. Longer strings require a known container format, pointer table, or relocation strategy and should be implemented format-by-format.

Encoded candidate scans are bounded to keep large binary files responsive. Once a real container format is identified, add a dedicated parser instead of relying on raw scanning.

## Testing

Create and activate a local virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

Run the standard-library test suite:

```powershell
python -m unittest discover -s tests
```

The tests generate synthetic binary files at runtime and do not require game data.
