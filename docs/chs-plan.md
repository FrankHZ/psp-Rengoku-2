# Chinese Patch Current Plan

This is the short, current-stage handoff. Older experiment details live in the
runtime observation docs, seed CSVs, local work summaries, and git history.
Mutable strategy and layout rules live in:

```text
docs/chs-strategy.md
docs/chs-layout-rules.md
```

## Current State

Current PPSSPP-ready broad build:

```text
local/rebuilt/combined_chs_v12_manual_skillpoints_0003_0008_0012anchored_0015full_0016full_0017full_extracted/
```

Current work root:

```text
local/work/combined_chs_v12_manual_skillpoints_0003_0008_0012anchored_0015full_0016full_0017full/
```

This build covers:

```text
DATA001/0003 boot/init UI
DATA001/0008 tutorial/objective overlay
DATA001/0012 anchored story slice
DATA001/0015 full equipment/catalog table
DATA001/0016 full UI/menu table
DATA001/0017 full help/manual table
```

The build has 1113 translated rows and currently uses 849 assigned glyphs.
With the 11 physical font pages available in the current route, practical
capacity is 891 cells, so the remaining headroom is about 42 cells.

## Active Findings

Confirmed runtime page bases now include:

```text
child 1  base 0x0100 / 0x0151
child 2  base 0x01a2 / 0x01f3
child 3  base 0x0244 / 0x0295
child 4  base 0x02e6 / 0x0337
child 5  base 0x0388 / 0x03d9
child 6  base 0x042a / 0x047b
child 7  base 0x04cc / 0x051d
child 8  base 0x056e / 0x05bf
child 9  base 0x0610 / 0x0661
child 10 base 0x06b2 / 0x0703
child 11 base 0x0754 provisional
```

Important caveat: alternate bases on the same child are alternate runtime code
windows, not extra storage. For example, child 9 / base `0x0610` and child 9 /
base `0x0661` both use the same 81 physical cells. The alternate bases improve
decoding and code routing, but do not increase glyph capacity.

Most recent page-base evidence:

```text
0x0689 -> 暗, child 9,  cell 40, base 0x0661
0x06b2 -> L,  child 10, cell 0,  base 0x06b2
0x0702 -> E,  child 10, cell 80, base 0x06b2
```

Seed/reference files:

```text
samples/runtime_glyph_map_seed.csv
samples/runtime_kana_map.csv
local/work/page_base_candidates/
```

## Current Blockers

The main blocker is glyph capacity, not text discovery. A single broad build
can fit catalog/UI/help plus a small story slice, but full story + full
catalog/UI/help is still too tight unless we reduce unique glyph use or split
the deliverable. See `docs/chs-strategy.md` for the current capacity strategy.

## Next Deliverable

Target: a larger PPSSPP build with better glyph fit and fewer untranslated
visible records.

See `docs/chs-strategy.md` for the recommended order and
`docs/chs-layout-rules.md` for current layout/name-input rules.

## Current Local Artifacts

Keep these current generated outputs:

```text
local/work/combined_chs_v12_manual_skillpoints_0003_0008_0012anchored_0015full_0016full_0017full/
local/rebuilt/combined_chs_v12_manual_skillpoints_0003_0008_0012anchored_0015full_0016full_0017full_extracted/
local/work/combined_chs_story_full_v1_0003_0008_0012full/
local/rebuilt/combined_chs_story_full_v1_0003_0008_0012full_extracted/
local/work/page_base_probe_help0017_gap66_v2/
local/rebuilt/page_base_probe_help0017_gap66_v2_extracted/
```

Older generated combined/probe builds were removed during cleanup. If a stale
local build is recreated, either document why it is useful or remove it.
