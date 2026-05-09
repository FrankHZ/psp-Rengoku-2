# Assumptions and Unknowns

## Current Assumptions

- The user supplies a legally obtained PSP dump locally.
- Game files and extracted assets stay outside version control.
- Scripts operate on explicit input and output paths.
- Text may appear as ASCII, UTF-8, Shift-JIS, or game-specific encodings.
- Text containers, pointer tables, compression, archives, and checksums are unknown until documented.
- Reinserted text must not grow beyond its original byte allocation unless the surrounding format is understood.

## Unknowns To Resolve Per Game

- Which files contain user-facing text.
- Whether text is compressed, encrypted, archived, or packed with executable code.
- Whether strings are null-terminated, length-prefixed, table-driven, or pointer-referenced.
- Whether pointers are absolute, relative, sector-based, or virtual addresses.
- Whether modified files require checksums, alignment, or archive index updates.
- Which rebuild process produces a bootable ISO accepted by PPSSPP and real hardware.

## Safety Rules

- Never modify original dump files in place.
- Keep a byte-for-byte backup of every source file before import.
- Prefer copy-on-write outputs and inspect binary diffs.
- Record every detected format in `docs/formats.md`.
- Add tests before supporting a new container format.

