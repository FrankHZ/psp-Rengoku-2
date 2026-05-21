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

The current CHS handoff is:

```text
local/rebuilt/combined_chs_v44_reviewed_token_extracted/
```

The build keeps the JP-first story baseline, applies the story-name glossary, promotes reviewer-edited DATA001/0015 equipment text with separate review/runtime layers, promotes the full reviewer JSON package including help/manual and DATA002 UI feedback, keeps standalone attack-attribute labels in English, and keeps DATA002/0065 rough UI rows cleared. It uses the full SemiBold 18px CJK font atlas, preserves original Latin/punctuation/symbol glyphs where source codes are known, patches the EBOOT ASCII advance table so halfwidth `1` aligns with the other digits, translates the EBOOT save-list metadata templates for new saves, preserves DATA003/1089 `#GRAM#` player-name tokens for custom-name runtime substitution, and keeps source-budget wrapping for long Chinese prose.

The current releasable v44 build keeps the in-game title textures clean, but uses the earlier PSP shell `PIC1.PNG` background with a small `小方 oid Codex 汉化` credit in the upper-left. A separate local experiment exists at `local/rebuilt/combined_chs_v43_title_logo_ank3_retry.iso`; it patches the in-game title logo layer, but the visual result is still considered experimental rather than part of the releasable baseline.

Current text review package:

```text
local/work/translation_review_slim_v12_reviewed_all/
translation_reviewed/
```

## Repository Layout

| Path | Purpose |
| --- | --- |
| `docs/` | Current plan, strategy, layout rules, format notes, runtime findings, tooling index, and local artifact policy. |
| `tools/` | Command-line utilities for extraction, decoding, font work, staging builds, and current CHS sheet generation. |
| `tests/` | Synthetic fixtures and unit tests for parsers/build helpers. Tests do not require game data. |
| `samples/` | Repo-safe seed/example files, including runtime glyph-map seeds. |
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
  fonts/
```

Keep pristine original ROMs outside this repository. Use `local/extracted/` for
unpacked ISO contents, `local/work/` for generated working files, and
`local/rebuilt/` for PPSSPP-ready extracted-folder builds.

## Documentation Map

| Document | Purpose |
| --- | --- |
| `docs/chs-plan.md` | Short current-stage handoff: current build, coverage, blockers, and next work. |
| `docs/chs-strategy.md` | Mutable CHS build strategy, translation policy, glyph-capacity model, and current review guidance. |
| `docs/chs-layout-rules.md` | Runtime layout rules for hard/soft breaks, source symbols, key hints, manual pages, and name input. |
| `docs/chs-glossary.json` | Machine-readable story terminology/name glossary, including Divine Comedy name forms. |
| `docs/local-artifacts.md` | Keep/remove policy for ignored `local/` outputs. |
| `docs/tooling.md` | Workflow-oriented index of maintained scripts in `tools/`. |
| `docs/runtime-observations.md` | Confirmed PPSSPP/runtime findings that still affect the current pipeline. |
| `docs/formats.md` | File/container format notes for MCD3, TDL, MIG, offset-table text, and related structures. |
| `docs/assumptions.md` | Project assumptions and safety constraints. |

Current reference seed files:

| File | Purpose |
| --- | --- |
| `samples/runtime_glyph_map_seed.csv` | Runtime glyph observations and inferred page-base seeds. |
| `samples/runtime_kana_map.csv` | Generated kana runtime map with seeded consistency checks. |
| `samples/glyph_map_seed.csv` | Older glyph-map seed used by extraction/debug flows. |
| `samples/story_glyph_map_seed.csv` | Story-table glyph-map seed used by story extraction/debug flows. |

## Tooling

Use `docs/tooling.md` as the source of truth for maintained scripts and build
commands. The current broad-build path is centered on:

```text
tools/build_chs_combined_data001.py
tools/build_chs_tutorial.py
tools/build_chs_offset_table.py
tools/stage_font_probe.py
tools/render_mig_font_cell.py
tools/report_chs_coverage.py
tools/export_chs_font_corpus.py
tools/build_full_jp_texts.py
tools/promote_reviewed_translation_package.py
tools/patch_savedata_sfo.py
tools/build_psp_iso.py
```

`tools/build_chs_combined_data001.py` has a legacy name, but the current staging
path can include DATA002 and DATA003 text patches as well as DATA001 entries.

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
