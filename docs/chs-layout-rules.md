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

The confirmed skill-point page is:

```text
DATA001/0017 record 18
```

Manual pages still queued for later layout review:

```text
DATA001/0017 body records:
16, 20, 22, 24, 26, 28, 30, 34, 36, 42, 44, 53, 57, 71, 73, 77, 85, 91
```

`tools/format_chs_manual_layout.py` preserves the confirmed skill-point page
layout and provides a basic wrapping helper for other manual bodies.

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
