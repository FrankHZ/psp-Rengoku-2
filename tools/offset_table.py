from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import struct


@dataclass(frozen=True)
class OffsetTableEntry:
    index: int
    offset: int
    end_offset: int
    size: int
    u16_preview: tuple[int, ...]


@dataclass(frozen=True)
class OffsetTable:
    path: Path
    word0: int
    count: int
    table_end: int
    entries: tuple[OffsetTableEntry, ...]


def read_offset_table(path: Path) -> OffsetTable:
    data = path.read_bytes()
    if len(data) < 8:
        raise ValueError(f"{path} is too small for an offset table")

    word0, count = struct.unpack_from("<II", data, 0)
    table_end = 8 + count * 4
    if count == 0 or table_end > len(data):
        raise ValueError(f"{path} has invalid offset count {count}")

    offsets = list(struct.unpack_from(f"<{count}I", data, 8))
    if any(offset < table_end or offset >= len(data) for offset in offsets):
        raise ValueError(f"{path} has offsets outside file data")
    if offsets != sorted(offsets):
        raise ValueError(f"{path} offsets are not sorted")

    entries: list[OffsetTableEntry] = []
    for index, offset in enumerate(offsets):
        end_offset = offsets[index + 1] if index + 1 < len(offsets) else len(data)
        record = data[offset:end_offset]
        preview = struct.unpack_from(f"<{min(len(record) // 2, 12)}H", record, 0) if len(record) >= 2 else ()
        entries.append(
            OffsetTableEntry(
                index=index,
                offset=offset,
                end_offset=end_offset,
                size=end_offset - offset,
                u16_preview=preview,
            )
        )

    return OffsetTable(path=path, word0=word0, count=count, table_end=table_end, entries=tuple(entries))
