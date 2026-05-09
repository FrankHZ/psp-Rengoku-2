from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import struct

from tdl import TdlFile, read_tdl_bytes


@dataclass(frozen=True)
class MscrFile:
    path: Path
    declared_size: int
    section_count: int
    word4: int
    word5: int
    embedded_tdl: TdlFile | None


def read_mscr(path: Path) -> MscrFile:
    data = path.read_bytes()
    if len(data) < 0x30:
        raise ValueError("file is too small for MSCR")

    magic, word1, declared_size, section_count, word4, word5, word6, word7 = struct.unpack_from("<4sIIIIIII", data, 0)
    if magic != b"MSCR":
        raise ValueError(f"expected MSCR magic, got {magic!r}")
    if word1 != 0 or word6 != 0 or word7 != 0:
        raise ValueError("MSCR header has unexpected reserved values")

    embedded_tdl = None
    if data[0x30:0x34] == b".TDL":
        embedded_tdl = read_tdl_bytes(data[0x30:], path)

    return MscrFile(
        path=path,
        declared_size=declared_size,
        section_count=section_count,
        word4=word4,
        word5=word5,
        embedded_tdl=embedded_tdl,
    )

