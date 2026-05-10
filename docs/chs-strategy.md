# Chinese Patch Strategy

This file holds current project strategy. It is expected to change as the patch
workflow evolves.

## Build Strategy

Prioritize PPSSPP-ready builds that validate a broad slice of the game. The
current broad build should be treated as the baseline until superseded:

```text
local/rebuilt/combined_chs_v12_manual_skillpoints_0003_0008_0012anchored_0015full_0016full_0017full_extracted/
```

The main blocker is glyph capacity. Do not assume alternate runtime bases add
storage; bases like child 9 / `0x0610` and child 9 / `0x0661` are alternate code
windows over the same physical 81 cells.

When capacity is tight, prefer:

```text
reuse existing ASCII and preserved button/input symbols
keep stylized equipment names in English
use shorter Simplified Chinese wording
split full-story and full-catalog deliverables when needed
```

## Translation Policy

Use Simplified Chinese for tutorial, UI, help, and ordinary prose.

For equipment names, prefer a hybrid policy:

```text
keep proper nouns/model names/stylized names in English
translate short generic functional names when the glyph cost is reasonable
keep descriptions concise and Chinese unless capacity requires an English mode
```

Examples that should usually stay English:

```text
Dante
C-K.O.D
Dragoon
Gladiator
SAA Magnum 88
Raijin
```

Runtime user input such as the player name is a variable token. Treat it as a
wildcard, for example `@GRAM@`/`#GRAM#`, not as literal translatable text.

## Glyph Capacity

Current v12 broad build:

```text
assigned glyphs: 849
physical capacity: 891
headroom: about 42
```

Equipment savings estimate:

```text
current v12 global unique glyphs:          849
if all equipment names stay English:       about 773  (-76)
if all equipment text stays English:       about 624  (-225)
```

Use the equipment-name-English variant as the first capacity recovery step.

## Next Deliverable

Target: a larger PPSSPP build with better glyph fit and fewer untranslated
visible records.

Recommended order:

```text
1. Create an equipment-name-English variant and measure glyph savings.
2. Apply the manual layout helper and fix queued manual pages as needed.
3. Add DATA002/0065 name-input confirmation support.
4. Build a new broad PPSSPP artifact.
5. Update docs/local-artifacts.md, docs/chs-plan.md, and this strategy file.
```
