# Chinese Patch Layout Rules

This file holds current text/layout rules. It is expected to change as new
PPSSPP observations come in.

## Key-Hint Overlay

Keep the original `?@` icon token at the beginning of key-hint strings:

```text
?@启动
```

Do not prefix it with `按`; the game draws the button token as a wide glyph and
the leading Chinese character overlaps it.

`tools/format_chs_manual_layout.py` currently applies this token fix to the
UI sheet.

## Help Manual Bodies

Use explicit `0x000a` line breaks only. Do not inject `0x0100` or `0x0105` as
newline helpers because they render as visible dots in this context.

Current v23 note: DATA001/0017 is translated in the broad build, and the queued
manual body pages have explicit layout overrides based on the Japanese line/page
shape and the aligned English reference. They still need PPSSPP visual checks,
but they are no longer known-provisional paragraph wraps.

The first confirmed fixed page was `A.角色状态 / 4. 技能点`:

```text
DATA001/0017 record 17 title: 4. 技能点
DATA001/0017 record 18 body:  skill-point page
```

The v15 manual-layout pass also covers these body records:

```text
DATA001/0017 body records:
16, 20, 22, 24, 26, 28, 30, 34, 36, 42, 44, 53, 57, 71, 73, 77, 85, 91
```

`tools/format_chs_manual_layout.py` now stores explicit overrides for these
manual bodies. Keep using the Japanese codes as the line/page-layout authority
and the aligned English text as the meaning/reference source for any future
manual edits.

Record 49 (`E. 操作 > 2. 攻击`) should not use the placeholder `·键` for the
four attack controls. Preserve the original JP key-icon glyph codes through
inline build tokens:

```text
<icon:0161>键：头部
<icon:015f>键：左臂
<icon:011a>键：右臂
<icon:013e>键：躯干
```

The build emits those numeric codes directly and reserves their physical source
font cells, so they do not get overwritten by CHS glyph assignments. Use the
same approach for other manual/tutorial button hints when the original JP row
exposes a clear source icon code.

## Manual Prose Layout

For prose-heavy help pages, prefer the generic prose wrapper before adding a
one-off translation override. `tools/format_chs_manual_layout.py` currently
uses token-aware 16-unit wrapping for:

```text
A2, C5, F1, F3, G1, G2, G7, G9, H1, H2, H4, H5, H7
```

That wrapper preserves ASCII words, restores known manual phrases such as
`Memory Stick Duo` and `Delete Save`, and breaks on Chinese sentence punctuation
instead of raw character count.

## Name Input

DATA002/0065 player-name confirmation should preserve the runtime user-name
token as a wildcard. Suggested visible rows:

```text
record 82: 用此名吗？
record 83: 确定
record 84: 取消
```

Treat the displayed player name, such as `GRAM`, as runtime input rather than a
literal string to translate.

`tools/make_chs_name_input_sheet.py` generates the current DATA002/0065 sheet
for these rows, and the v23 broad build includes them.
