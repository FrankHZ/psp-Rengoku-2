from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import struct


@dataclass(frozen=True)
class PackEntry:
    index: int
    offset: int
    size: int

    @property
    def end_offset(self) -> int:
        return self.offset + self.size


@dataclass(frozen=True)
class PackFile:
    path: Path
    entry_count: int
    table_offset: int
    entries: tuple[PackEntry, ...]


def read_pack0001(path: Path) -> PackFile:
    data = path.read_bytes()
    if len(data) < 0x20:
        raise ValueError("file is too small for PACK0001")

    magic, entry_count, table_offset = struct.unpack_from("<8sII", data, 0)
    if magic != b"PACK0001":
        raise ValueError(f"expected PACK0001 magic, got {magic!r}")

    row_size = 0x10
    table_end = table_offset + entry_count * row_size
    if len(data) < table_end:
        raise ValueError("PACK0001 entry table is truncated")

    entries = []
    for index in range(entry_count):
        row_offset = table_offset + index * row_size
        offset, reserved0, size, reserved1 = struct.unpack_from("<IIII", data, row_offset)
        if reserved0 != 0 or reserved1 != 0:
            raise ValueError(f"PACK0001 entry {index} has unexpected reserved values")
        if offset + size > len(data):
            raise ValueError(f"PACK0001 entry {index} extends past end of file")
        entries.append(PackEntry(index=index, offset=offset, size=size))

    return PackFile(path=path, entry_count=entry_count, table_offset=table_offset, entries=tuple(entries))

