from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import struct


@dataclass(frozen=True)
class TdlEntry:
    index: int
    name: str
    size: int
    offset: int

    @property
    def end_offset(self) -> int:
        return self.offset + self.size


@dataclass(frozen=True)
class TdlFile:
    path: Path
    entry_count: int
    declared_data_size: int
    flags_or_reserved: int
    entries: tuple[TdlEntry, ...]


def read_tdl(path: Path) -> TdlFile:
    return read_tdl_bytes(path.read_bytes(), path)


def read_tdl_bytes(data: bytes, path: Path | None = None) -> TdlFile:
    if len(data) < 0x10:
        raise ValueError("file is too small for a TDL file")

    magic, entry_count, declared_data_size, flags_or_reserved = struct.unpack_from("<4sIII", data, 0)
    if magic != b".TDL":
        raise ValueError(f"expected .TDL magic, got {magic!r}")

    table_offset = 0x10
    entry_size = 0x18
    data_start = table_offset + entry_count * entry_size
    if len(data) < data_start:
        raise ValueError("TDL entry table is truncated")

    entries = []
    for index in range(entry_count):
        row_offset = table_offset + index * entry_size
        name = _decode_c_string(data[row_offset : row_offset + 16])
        size, offset = struct.unpack_from("<II", data, row_offset + 16)
        if offset + size > len(data):
            raise ValueError(f"TDL entry {index} extends past end of file")
        entries.append(TdlEntry(index=index, name=name, size=size, offset=offset))

    return TdlFile(
        path=path or Path("<bytes>"),
        entry_count=entry_count,
        declared_data_size=declared_data_size,
        flags_or_reserved=flags_or_reserved,
        entries=tuple(entries),
    )


def _decode_c_string(data: bytes) -> str:
    return data.split(b"\x00", 1)[0].decode("ascii", errors="replace")
