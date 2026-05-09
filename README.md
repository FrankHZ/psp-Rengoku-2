# PSP ROM Translation Workspace

This repository contains scripts, tests, and notes for analyzing and translating text from a legally obtained PSP game dump.

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
- `tools/inspect_pack0001.py` inspects `PACK0001` resource containers.
- `tools/inspect_mig.py` inspects `MIG.00.1PSP` resources.
- `tools/export_mig_png.py` exports supported `MIG.00.1PSP` textures to PNG.
- `tools/export_glyph_cells.py` exports font atlas cells and glyph ID hypotheses for mapping work.
- `tools/extract_offset_table_runs.py` extracts length-prefixed text/glyph-code runs from confirmed offset-table containers.
- `tools/decode_offset_table_text.py` applies a seed glyph map to offset-table records for survey/debug output.
- `tools/inspect_mscr.py` inspects `MSCR` map/scene resource bundles.
- `tools/runtime_texture_inventory.py` inventories PPSSPP dumped texture PNGs.
- `tools/map_runtime_font_pages.py` maps PPSSPP dumped font texture addresses back to extracted font pages.

For the current Rengoku 2 UI table lead, export a partial translator-facing JSON with:

```powershell
python tools/extract_text.py --format offset-table-runs --glyph-map samples/glyph_map_seed.csv local/work/mcd3_entries/DATA001/0016_bin.bin local/work/extract_text_DATA001_0016_seeded.json
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
