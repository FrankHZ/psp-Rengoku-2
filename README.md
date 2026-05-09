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
