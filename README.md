# PSP ROM Translation Workspace

This repository contains scripts, tests, and notes for analyzing and translating
text from a legally obtained PSP game dump.

Current project target: a Simplified Chinese patch for Rengoku 2 PSP JP. English
text from the USA release is used only as ignored local reference material for
alignment and translation drafting.

Do not commit copyrighted game files, extracted assets, rebuilt images, or
generated binary patches. Keep those files under ignored local paths such as
`local/`.

## Current State

The current CHS handoff lives in:

```text
docs/chs-plan.md
docs/chs-strategy.md
docs/chs-layout-rules.md
docs/local-artifacts.md
docs/tooling.md
```

The current PPSSPP-ready broad build is documented in `docs/chs-plan.md` and
`docs/local-artifacts.md`. Local generated builds are intentionally ignored by
git.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `docs/` | Current plan, strategy, layout rules, format notes, survey history, runtime observations, tooling index, and local artifact policy. |
| `tools/` | Small command-line utilities for extraction, decoding, font work, staging builds, and current CHS sheet generation. |
| `tests/` | Synthetic fixtures and unit tests for parsers/build helpers. Tests do not require game data. |
| `samples/` | Non-copyrighted seed/example files, including runtime glyph-map seeds. |
| `patch/` | Placeholder notes for future patch packaging workflow. |
| `local/` | Ignored local workspace for extracted game files, generated sheets, PPSSPP-ready folders, emulator helpers, and rebuilt images. |

Recommended local-only layout:

```text
local/
  emulators/
  tools/
  roms/
  extracted/
  work/
  rebuilt/
```

Keep pristine original ROMs outside this repository. Use `local/extracted/` for
unpacked ISO contents, `local/work/` for generated working files, and
`local/rebuilt/` for PPSSPP-ready extracted-folder builds.

## Documentation Map

| Document | Purpose |
| --- | --- |
| `docs/chs-plan.md` | Short current-stage handoff: current build, current blocker, confirmed runtime bases, and next deliverable. |
| `docs/chs-strategy.md` | Mutable CHS build strategy, translation policy, and glyph-capacity approach. |
| `docs/chs-layout-rules.md` | Runtime layout rules for key-hint overlays, manual/help pages, and name-input confirmation text. |
| `docs/local-artifacts.md` | Keep/remove policy for ignored `local/` outputs, including current PPSSPP-ready builds and useful generated inputs. |
| `docs/tooling.md` | Workflow-oriented index of scripts in `tools/`, grouped by current build path, extraction/import, archive utilities, font work, probes, and verification. |
| `docs/runtime-observations.md` | PPSSPP/runtime findings and confirmed behavior that should not clutter the short plan. |
| `docs/formats.md` | File/container format notes for MCD3, TDL, MIG, offset-table text, and related structures. |
| `docs/text-candidate-report.md` | Candidate text-table findings and ownership notes from the broader survey. |
| `docs/survey-report.md` | Historical survey summary and confirmed table mappings/probe results. |
| `docs/survey-targets.md` | Survey target list and investigation priorities. |
| `docs/early-stage-report.md` | Early project observations retained for historical context. |
| `docs/assumptions.md` | Project assumptions and constraints captured during reverse-engineering. |

Current reference seed files:

| File | Purpose |
| --- | --- |
| `samples/runtime_glyph_map_seed.csv` | Runtime glyph observations and inferred page-base seeds. |
| `samples/runtime_kana_map.csv` | Generated kana runtime map with seeded consistency checks. |
| `samples/glyph_map_seed.csv` | Older glyph-map seed used by extraction/debug flows. |
| `samples/story_glyph_map_seed.csv` | Story-table glyph-map seed used by story extraction/debug flows. |

## Tooling

Use `docs/tooling.md` as the source of truth for scripts and build commands.
The current broad-build path is centered on:

```text
tools/make_equipment_name_english_variant.py
tools/make_chs_name_input_sheet.py
tools/format_chs_manual_layout.py
tools/promote_tutorial_usa_alignments.py
tools/build_chs_combined_data001.py
tools/stage_font_probe.py
```

`tools/build_chs_combined_data001.py` has a legacy name, but the current staging
path can include DATA002 text patches as well as DATA001 entries.

## Testing

Create and activate a local virtual environment if needed:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

Run the standard test suite after tooling changes:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

The tests generate synthetic binary files at runtime and do not require game
data.
