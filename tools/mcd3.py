from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import struct


@dataclass(frozen=True)
class Mcd3Entry:
    id: int
    archive_index: int | None
    archive_name: str | None
    selector: int
    size: int
    offset: int
    stored_size: int

    @property
    def is_empty(self) -> bool:
        return self.selector == 0 and self.size == 0 and self.offset == 0 and self.stored_size == 0

    @property
    def end_offset(self) -> int:
        return self.offset + self.size


@dataclass(frozen=True)
class Mcd3Index:
    path: Path
    header_size: int
    archive_count: int
    entry_count: int
    archive_names: tuple[str, ...]
    entries: tuple[Mcd3Entry, ...]


def read_mcd3(path: Path) -> Mcd3Index:
    data = path.read_bytes()
    if len(data) < 0x60:
        raise ValueError("file is too small for an MCD3 index")

    header_size, archive_count, entry_count = struct.unpack_from("<III", data, 0)
    magic = data[0x0C:0x10]
    if magic != b"MCD3":
        raise ValueError(f"expected MCD3 magic at 0x0C, got {magic!r}")

    name_table_offset = 0x10
    archive_names = tuple(
        _decode_c_string(data[name_table_offset + index * 16 : name_table_offset + (index + 1) * 16])
        for index in range(archive_count)
    )

    expected_size = header_size + entry_count * 16
    if len(data) < expected_size:
        raise ValueError(f"MCD3 table is truncated: expected at least {expected_size} bytes, got {len(data)}")

    entries = []
    for entry_id in range(entry_count):
        selector, size, offset, stored_size = struct.unpack_from("<IIII", data, header_size + entry_id * 16)
        archive_index = selector_to_archive_index(selector)
        archive_name = None
        if archive_index is not None and 0 <= archive_index < len(archive_names):
            archive_name = archive_names[archive_index]
        entries.append(
            Mcd3Entry(
                id=entry_id,
                archive_index=archive_index,
                archive_name=archive_name,
                selector=selector,
                size=size,
                offset=offset,
                stored_size=stored_size,
            )
        )

    return Mcd3Index(
        path=path,
        header_size=header_size,
        archive_count=archive_count,
        entry_count=entry_count,
        archive_names=archive_names,
        entries=tuple(entries),
    )


def selector_to_archive_index(selector: int) -> int | None:
    if selector == 0:
        return None
    if selector < 0x8000:
        return None
    remainder = selector - 0x8000
    if remainder % 0x10000 != 0:
        return None
    return remainder // 0x10000


def _decode_c_string(data: bytes) -> str:
    return data.split(b"\x00", 1)[0].decode("ascii", errors="replace")

