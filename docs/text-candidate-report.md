# Japanese Text Candidate Report

Date: 2026-05-09

Purpose: identify the Japanese text record/table candidates that are already visible in the extracted `MCD3` entries, and give future CHS work a planning map. This report intentionally avoids copying JP/USA prose from ignored local extraction or alignment JSONs.

## Scope

Patch target is the Japanese dump. USA data and wiki material are reference/alignment sources only.

Optional future lore/dialogue reference: the Japanese Rengoku 2 atwiki (`https://w.atwiki.jp/rengoku2/`) includes boss-event dialogue pages such as `pages/11.html`. Use it only for future translation improvement/cross-checking, not as the current translation source.

Generated extraction, alignment, and rebuilt artifacts remain under ignored `local/` paths. The repo-safe tracking layer should be docs, tools, tests, and small hand-built mapping seeds.

## Candidate Tables

The current offset-table parser recognizes eight text-like tables across the extracted `MCD3` tree:

| JP table | Size | Records | Runs | Glyph runs | ASCII runs | Role | Confidence |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `DATA001/0003` | `1000` | 15 | 14 | 14 | 0 | Boot/init UI | High |
| `DATA001/0008` | `11504` | 86 | 66 | 63 | 3 | Live in-stage tutorial/objective overlay | Very high |
| `DATA001/0012` | `26696` | 420 | 229 | 227 | 2 | Story/dialogue text table | Very high |
| `DATA001/0015` | `51956` | 336 | 672 | 670 | 2 | Equipment/item/attack catalog names and descriptions | Very high |
| `DATA001/0016` | `18360` | 328 | 328 | 160 | 168 | Menu/UI labels and floor names | Very high |
| `DATA001/0017` | `26076` | 105 | 103 | 100 | 3 | Help/manual pages | Very high |
| `DATA002/0065` | `27980` | 702 | 225 | 218 | 7 | Name-input/game UI candidate | Medium-high |
| `DATA003/1089` | `87500` | 1499 | 1174 | 855 | 319 | Story script command/control table | High |

These tables share the same broad structure: `u32 word0`, `u32 count`, then `count` little-endian record offsets. Records contain repeated control-looking prefixes followed by length-prefixed `u16` runs. Some runs are direct ASCII stored as `u16`; most Japanese-visible rows are glyph-code streams.

## Known JP/USA Reference Pairings

The following local alignments exist and should drive translator-facing sheets. They match record/run IDs between the JP target table and the USA reference table; they are not direct binary patch inputs.

| JP target | USA reference | Alignment rows | Fits current same-size budget | Does not fit | Local alignment file |
| --- | --- | ---: | ---: | ---: | --- |
| `DATA001/0003` | `DATA001/0009` | 14 | 0 | 14 | `local/work/align_JP0003_USA0009_boot_ui.json` |
| `DATA001/0008` | `DATA001/0017` | 8 | 0 | 8 | `local/work/align_JP0008_USA0017_tutorial.json` |
| `DATA001/0012` | `DATA001/0022` | 226 | 4 | 222 | `local/work/align_JP0012_USA0022_story.json` |
| `DATA001/0015` | `DATA001/0026` | 672 | 207 | 465 | `local/work/align_JP0015_USA0026_ui.json` |
| `DATA001/0016` | `DATA001/0027` | 297 | 145 | 152 | `local/work/align_JP0016_USA0027_ui.json` |
| `DATA001/0017` | `DATA001/0028` | 103 | 14 | 89 | `local/work/align_JP0017_USA0028_help.json` |

Current update: `DATA002/0065` aligns strongly to USA `DATA002/0066`, and
`DATA003/1089` has a readable USA extraction with 1175 rows. Treat
`DATA002/0065` as a mixed multiplayer/gallery UI table with some control rows.
Treat `DATA003/1089` as a visible script/story candidate bank with command rows
mixed in; it is not part of v19, but it is counted in
`local/work/actual_cjk_requirement_v1/`.

## Runtime-Confirmed Ownership

These records have direct runtime evidence from PPSSPP marker probes or completed prototype work:

| Table | Records | Ownership evidence | Planning note |
| --- | --- | --- | --- |
| `DATA001/0008` | `10`, `11`, `66`-`71` | Owns live tutorial/objective overlays and has a completed CHS prototype path | Best first production target |
| `DATA001/0016` | At least `12`, plus menu/UI rows from prior probes | Owns input-key info/help overlay and menu/UI labels | Good second target after tutorial text |
| `DATA001/0017` | Help-page rows including known embedded labels | Owns help/manual pages | Good structured UI/manual target |
| `DATA001/0012` | `140`-`143`, `160`-`174` anchored by the 4F boss scene | Primary story/prose table | Needs broader glyph map and line-budget planning |
| `DATA001/0003` | `0` | Init/loading UI before title | Small but visible UI target |
| `DATA002/0065` | `82`, `84` | New-game player-name input screen markers | Needs classification before broad translation |
| `DATA003/1089` | Script sections are readable by `#start` records and command rows | Contains scene/script commands and visible story rows | Count visible non-command rows in full CJK requirement; build separately until patch safety is proven |

## Item, Equipment, And Attack-Name Candidates

The first version of this report underweighted item/equipment text. Follow-up inspection shows the strongest candidate is `DATA001/0015`, not `PACK0001` or `OMG` resource names.

### Primary Candidate: `DATA001/0015`

Status: very high-confidence equipment/item/attack catalog table.

Evidence:
- `local/work/align_JP0015_USA0026_ui.json` aligns all 336 JP records to USA `DATA001/0026`.
- Every aligned record has exactly two runs.
- Run `0` is short: 336 rows, average JP source budget about 9 code units, average USA reference length about 13 code units. This matches visible equipment/item names.
- Run `1` is longer: 336 rows, average JP source budget about 48 code units, average USA reference length about 113 code units. This matches item/equipment descriptions.
- The screenshot examples map into this table by USA alignment: short-name rows include records around `73`-`81` for names like the visible sword/saw examples, records around `94`-`97` for handgun examples including the SAA/Dragoon screenshot family, and many description rows mention attack behavior.
- Name/description-like clusters appear at records `4`-`34`, `47`-`81`, `94`-`196`, `201`-`203`, `241`-`261`, `269`-`278`, and `280`-`305`.

Interpretation:
- Treat `DATA001/0015` as the main item/equipment catalog: weapons, shields, armor, body-part equipment, attack-name-like entries, and item descriptions.
- It should no longer be described only as a generic large UI/system table.
- The current same-size importer can patch concise CHS rows, but many USA reference descriptions exceed the JP source budget. CHS may still fit better than English, but this table needs a budget-aware translation sheet before patching.

Concrete next steps:
1. Generate a translator-facing `DATA001/0015` sheet with `record`, `run`, JP max units, partial/source codes, USA reference summary, CHS name, CHS description, and notes.
2. Add a small classifier column for `weapon`, `shield`, `armor`, `body`, `consumable/system`, and `unknown`; initialize it from record ranges, then refine by screenshots.
3. Make a focused runtime marker build for a few known equipment-list rows from the screenshot, especially the rows corresponding to records around `73`-`81` and `94`-`97`.
4. Translate and patch a tiny vertical slice first: visible item-list names plus the right-side description/stat panel for one equipment screen.
5. Only after that, expand by catalog cluster and measure CHS unique-glyph pressure.

### Supporting Candidate: `DATA001/0016`

Status: high-confidence shared equipment/menu label table.

Evidence:
- `local/work/align_JP0016_USA0027_ui.json` contains short UI/stat/action labels that match equipment screens: body-part names, slot labels, heat-resistance labels, upgrade labels, recover actions, attack labels, and defense labels.
- This table is already runtime-confirmed for menu/UI ownership.

Interpretation:
- Use `DATA001/0016` for equipment-screen chrome and stat labels, not item catalog entries.
- This likely owns labels like body parts, upgrade menu actions, and some right-side stat/action captions around the equipment UI.

Concrete next steps:
1. Add `DATA001/0016` rows for equipment/stat labels to the same terminology sheet as `DATA001/0015`.
2. Patch shared labels before broad item descriptions so terminology stays consistent.

### Lower-Confidence Resource Leads: `PACK0001` / `OMG`

Status: asset/model support, low confidence for user-facing item text.

Evidence:
- `DATA001/0010` and `DATA001/0011` are `PACK0001` containers.
- `DATA001/0011` contains `OMG.00.1PSP` child resources with ASCII names like `item_obj001`.
- These look like model/object resource identifiers, not the visible localized names. The identifiers explain item models, but they are not aligned to the screenshot name text.

Interpretation:
- Keep `PACK0001`/`OMG` in the asset bucket unless a future screen needs model-to-text cross-reference.
- Do not spend translation effort here before exhausting `DATA001/0015` and `DATA001/0016`.

Concrete next steps:
1. If model-to-item lookup becomes necessary, create a local cross-reference between `DATA001/0011` child index/resource name and `DATA001/0015` catalog records.
2. Avoid editing `PACK0001`/`OMG` for text until a real user-facing string is found there.

## Table Notes

### `DATA001/0008` - Tutorial/Objective Overlay

Status: completed first CHS workflow target.

Why it matters:
- Runtime-confirmed owner for live tutorial/objective overlays.
- First full CHS prototype already exercises extraction, translation drafting, glyph assignment, font patching, exact glyph-code insertion, and same-size archive replacement.

Local planning inputs:
- `local/work/extract_text_DATA001_0008_seeded_fresh.json`
- `local/work/align_JP0008_USA0017_tutorial.json`
- `local/work/chs_tutorial_draft_DATA001_0008.json`
- `local/work/tutorial_chs_full_v1/DATA001_0008_chs_full.json`
- `local/work/tutorial_chs_full_v1/runtime_glyph_assignments.csv`

Recommended next action: keep this as the regression target while improving font quality. Any future text pipeline change should be able to rebuild the tutorial CHS artifact.

### `DATA001/0016` - Menu/UI Labels

Status: editable and runtime-confirmed.

Why it matters:
- Contains many direct ASCII labels and mixed glyph-code rows.
- Prior smoke tests confirmed same-size replacement for visible UI labels.
- USA alignment coverage is strong and many rows fit the current same-size budget.

Local planning inputs:
- `local/work/extract_text_DATA001_0016_seeded.json`
- `local/work/extract_text_DATA001_0016_dialogue_seeded.json`
- `local/work/align_JP0016_USA0027_ui.json`

Recommended next action: create a translator-facing sheet for high-value menu/UI rows, then assign CHS glyphs only for the selected rows.

### `DATA001/0017` - Help/Manual Pages

Status: editable and runtime-confirmed.

Why it matters:
- Confirmed help/manual ownership through prior `HELP` label replacement.
- The table is smaller than the big UI/story tables and likely has stable page-like structure.

Local planning inputs:
- `local/work/extract_text_DATA001_0017_seeded.json`
- `local/work/extract_text_DATA001_0017_dialogue_seeded.json`
- `local/work/align_JP0017_USA0028_help.json`

Recommended next action: translate after the UI label set, because help text likely benefits from finalized terminology.

### `DATA001/0012` - Story/Dialogue

Status: primary story text candidate.

Why it matters:
- Confirmed story prose table with anchored boss-scene slices.
- USA alignment exists for 226 rows.
- This table is likely the main story translation workload currently reachable without executable work.

Local planning inputs:
- `local/work/extract_text_DATA001_0012_story_seeded.json`
- `local/work/extract_text_DATA001_0012_dialogue_seeded.json`
- `local/work/align_JP0012_USA0022_story.json`
- `samples/story_glyph_map_seed.csv`

Recommended next action: build a scene-index report from `DATA001/0012` plus
`DATA003/1089` script sections, then decide whether `DATA003/1089` should be a
separate story-script deliverable. The current actual requirement report already
counts 851 visible non-command `DATA003/1089` rows.

### `DATA001/0015` - Equipment/Item Catalog

Status: very high-confidence equipment/item/attack-name table.

Why it matters:
- Largest aligned equipment catalog table by run count.
- Alignment coverage is complete for the currently exported rows.
- Run `0` is short-name-like and run `1` is description-like for every aligned record.
- It covers the class of screenshot text that includes item/equipment names and attack descriptions.

Local planning inputs:
- `local/work/extract_text_DATA001_0015_seeded.json`
- `local/work/extract_text_DATA001_0015_dialogue_seeded.json`
- `local/work/align_JP0015_USA0026_ui.json`

Recommended next action: create a budget-aware catalog sheet and probe a screenshot-visible equipment slice before trying a full catalog translation.

### `DATA001/0003` - Boot/Init UI

Status: small confirmed UI target.

Why it matters:
- Runtime marker confirmed record `0` on the init/loading screen before the title.
- Small enough to translate opportunistically once the glyph set includes needed UI characters.

Local planning inputs:
- `local/work/extract_text_DATA001_0003_seeded.json`
- `local/work/extract_text_DATA001_0003_dialogue_seeded.json`
- `local/work/align_JP0003_USA0009_boot_ui.json`

Recommended next action: batch with menu/UI work, not with story.

### `DATA002/0065` - Name-Input/Game UI Candidate

Status: medium-high confidence UI target without USA alignment.

Why it matters:
- Runtime markers confirmed records `82` and `84` on the new-game player-name input screen.
- It has many records but fewer extracted runs than `DATA001/0015` or `DATA003/1089`; it may mix UI labels, data labels, and non-text control rows.

Local planning inputs:
- `local/work/extract_text_DATA002_0065_seeded.json`
- `local/work/extract_text_0065_bin_dialogue_seeded.json`

Recommended next action: make a focused marker probe for clusters around confirmed records before translating broadly.

### `DATA003/1089` - Story Script/Control Table

Status: high-confidence script/control table.

Why it matters:
- Contains many direct ASCII command rows and glyph rows.
- Command rows give scene/floor section boundaries and layout commands.
- Useful for ordering and contextualizing `DATA001/0012` dialogue, but current evidence says visible prose is not owned solely by this table.

Local planning inputs:
- `local/work/script_DATA003_1089_dialogue_seeded.json`
- `local/work/script_DATA003_1089_6f_known.json`
- `local/work/extract_text_1089_bin_dialogue_seeded.json`
- `local/work/dialogue_glyph_map.csv`

Recommended next action: use it to generate a scene/context index for translators. Preserve command rows exactly until the command language is better documented.

## Prioritized CHS Work Queue

1. `DATA001/0008`: keep polishing the tutorial build and use it as the end-to-end regression test.
2. `DATA001/0015` plus `DATA001/0016`: equipment/item names, descriptions, and shared equipment-screen labels, because the screenshot shows this as the next visible gap.
3. `DATA001/0017`: help/manual pages, after terminology stabilizes from menu/UI and equipment work.
4. `DATA001/0003` and `DATA002/0065`: small boot/name-input UI targets, batched with UI terminology.
5. `DATA001/0012`: story/dialogue, once font quality and glyph-budget strategy are stronger.
6. `DATA003/1089`: treat as a separate visible script/story candidate bank; build a dedicated scene/script deliverable before mixing it into the broad UI/catalog artifact.

## Open Planning Questions

- Which `DATA001/0015` catalog records correspond to each visible equipment-list category and sort order?
- Does `DATA002/0065` have a USA counterpart hidden outside the current alignment set, or should it be mapped by runtime probes/manual screenshots?
- How should `DATA003/1089` script sections be joined to `DATA001/0012` dialogue records for final story presentation and patch packaging?
- When full-length CHS exceeds the current same-size run budget, should the project prioritize concise writing or table/archive resizing?
- How many Japanese glyph cells can be reclaimed safely once a target table is fully translated?

## Reproduction Commands

Inspect offset-table candidates:

```powershell
python tools/inspect_offset_table.py local/work/mcd3_entries/DATA001 local/work/mcd3_entries/DATA002 local/work/mcd3_entries/DATA003
```

Extract runs from a confirmed table:

```powershell
python tools/extract_text.py --format offset-table-runs --glyph-map samples/story_glyph_map_seed.csv local/work/mcd3_entries/DATA001/0012_bin.bin local/work/extract_text_DATA001_0012_story_seeded.json
```

Create a JP/USA alignment report under ignored local work:

```powershell
python tools/align_reference_text.py local/work/extract_text_DATA001_0012_story_seeded.json local/work/usa_extract_text_DATA001_0022.json local/work/align_JP0012_USA0022_story.json
```
