from __future__ import annotations

import csv
from pathlib import Path


def read_glyph_map(path: Path) -> dict[int, str]:
    glyphs: dict[int, str] = {}
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            char = parse_glyph_char(row.get("char") or "")
            code = (row.get("code") or "").strip()
            if not char or not code:
                continue
            glyphs[int(code, 0)] = char
    return glyphs


def parse_glyph_char(raw: str) -> str:
    char = raw.strip()
    if char == r"\n":
        return "\n"
    if char == r"\t":
        return "\t"
    return char


def decode_glyph_values(values: list[int] | tuple[int, ...], glyphs: dict[int, str]) -> tuple[str, int]:
    decoded: list[str] = []
    known = 0
    for value in values:
        if value in glyphs:
            decoded.append(glyphs[value])
            known += 1
        elif value == 0:
            decoded.append(" ")
        elif value == 0x000A:
            decoded.append("\n")
        elif value in {0x000C, 0x0010, 0x0014}:
            decoded.append("|")
        elif 0x20 <= value < 0x7F:
            decoded.append(chr(value))
        elif value < 0x80:
            decoded.append(".")
        else:
            decoded.append("·")
    return compact_unknowns(decoded), known


def compact_unknowns(parts: list[str]) -> str:
    text = "".join(parts)
    while "····" in text:
        text = text.replace("····", "···")
    while "  " in text:
        text = text.replace("  ", " ")
    return text.strip()
