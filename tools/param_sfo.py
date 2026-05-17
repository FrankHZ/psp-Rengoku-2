from __future__ import annotations

import struct
from dataclasses import dataclass


MAGIC = b"\x00PSF"
HEADER = struct.Struct("<4sIIII")
INDEX_ENTRY = struct.Struct("<HHIII")

FORMAT_BINARY = 0x0004
FORMAT_UTF8 = 0x0204
FORMAT_INT32 = 0x0404


@dataclass(frozen=True)
class SfoEntry:
    key: str
    format: int
    length: int
    max_length: int
    data_offset: int
    index_offset: int


class ParamSfo:
    def __init__(self, data: bytes | bytearray) -> None:
        if len(data) < HEADER.size:
            raise ValueError("PARAM.SFO is too small")
        self.data = bytearray(data)
        magic, version, key_table_offset, data_table_offset, entry_count = HEADER.unpack_from(self.data, 0)
        if magic != MAGIC:
            raise ValueError("not a PARAM.SFO file")
        self.version = version
        self.key_table_offset = key_table_offset
        self.data_table_offset = data_table_offset
        self.entry_count = entry_count
        self.entries = self._parse_entries()

    def _parse_entries(self) -> dict[str, SfoEntry]:
        entries: dict[str, SfoEntry] = {}
        for index in range(self.entry_count):
            index_offset = HEADER.size + index * INDEX_ENTRY.size
            if index_offset + INDEX_ENTRY.size > len(self.data):
                raise ValueError("PARAM.SFO index table extends past end of file")
            key_offset, fmt, length, max_length, data_offset = INDEX_ENTRY.unpack_from(self.data, index_offset)
            key_start = self.key_table_offset + key_offset
            key_end = self.data.find(b"\x00", key_start)
            if key_end < 0 or key_end >= self.data_table_offset:
                raise ValueError(f"unterminated PARAM.SFO key at index {index}")
            key = self.data[key_start:key_end].decode("ascii")
            value_start = self.data_table_offset + data_offset
            value_end = value_start + max_length
            if value_end > len(self.data):
                raise ValueError(f"PARAM.SFO value for {key} extends past end of file")
            entries[key] = SfoEntry(key, fmt, length, max_length, data_offset, index_offset)
        return entries

    def has_key(self, key: str) -> bool:
        return key in self.entries

    def raw_value(self, key: str) -> bytes:
        entry = self.entries[key]
        start = self.data_table_offset + entry.data_offset
        return bytes(self.data[start : start + entry.length])

    def value(self, key: str) -> str | int | bytes:
        entry = self.entries[key]
        raw = self.raw_value(key)
        if entry.format == FORMAT_UTF8:
            return raw.split(b"\x00", 1)[0].decode("utf-8")
        if entry.format == FORMAT_INT32:
            if len(raw) < 4:
                raise ValueError(f"integer field {key} is shorter than 4 bytes")
            return struct.unpack_from("<I", raw, 0)[0]
        return raw

    def string_value(self, key: str) -> str:
        entry = self.entries[key]
        if entry.format != FORMAT_UTF8:
            raise ValueError(f"{key} is not a UTF-8 string field")
        value = self.value(key)
        assert isinstance(value, str)
        return value

    def set_string(self, key: str, value: str) -> None:
        entry = self.entries[key]
        if entry.format != FORMAT_UTF8:
            raise ValueError(f"{key} is not a UTF-8 string field")
        encoded = value.encode("utf-8") + b"\x00"
        if len(encoded) > entry.max_length:
            raise ValueError(
                f"{key} is {len(encoded)} bytes with terminator, exceeding fixed capacity {entry.max_length}"
            )
        start = self.data_table_offset + entry.data_offset
        self.data[start : start + entry.max_length] = b"\x00" * entry.max_length
        self.data[start : start + len(encoded)] = encoded
        INDEX_ENTRY.pack_into(
            self.data,
            entry.index_offset,
            self._key_offset(entry),
            entry.format,
            len(encoded),
            entry.max_length,
            entry.data_offset,
        )
        self.entries[key] = SfoEntry(
            key=entry.key,
            format=entry.format,
            length=len(encoded),
            max_length=entry.max_length,
            data_offset=entry.data_offset,
            index_offset=entry.index_offset,
        )

    def _key_offset(self, entry: SfoEntry) -> int:
        key_start = self.key_table_offset
        key_bytes = entry.key.encode("ascii") + b"\x00"
        cursor = key_start
        while cursor < self.data_table_offset:
            next_cursor = self.data.find(b"\x00", cursor)
            if next_cursor < 0:
                break
            if self.data[cursor : next_cursor + 1] == key_bytes:
                return cursor - self.key_table_offset
            cursor = next_cursor + 1
        raise ValueError(f"could not relocate key {entry.key}")

    def to_bytes(self) -> bytes:
        return bytes(self.data)


def load_param_sfo(path) -> ParamSfo:
    with open(path, "rb") as source:
        return ParamSfo(source.read())
