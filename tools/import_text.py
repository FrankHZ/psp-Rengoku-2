from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct
from typing import Any

from extract_offset_table_runs import initial_run_cursor, read_u16_values
from offset_table import read_offset_table
from text_codec import encode_replacement


def import_text(source_path: Path, json_path: Path, output_path: Path) -> int:
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    if payload.get("format") == "offset-table-runs-v1":
        return import_offset_table_runs(source_path, payload, output_path)

    data = bytearray(source_path.read_bytes())
    entries: list[dict[str, Any]] = payload.get("entries", [])

    applied = 0
    for entry in entries:
        offset = int(entry["offset"])
        length = int(entry["length"])
        encoding = str(entry["encoding"])
        replacement_text = str(entry.get("translation") or entry.get("text") or "")

        if offset < 0 or length < 0 or offset + length > len(data):
            raise ValueError(f"entry {entry.get('id', '?')} points outside source file")

        replacement = encode_replacement(replacement_text, encoding, length)
        data[offset : offset + length] = replacement
        applied += 1

    output_path.write_bytes(data)
    return applied


def import_offset_table_runs(source_path: Path, payload: dict[str, Any], output_path: Path) -> int:
    data = bytearray(source_path.read_bytes())
    table = read_offset_table(source_path)
    applied = 0

    for entry in payload.get("entries", []):
        record_index = int(entry["record"])
        run_index = int(entry["run"])
        if record_index < 0 or record_index >= len(table.entries):
            raise ValueError(f"entry {entry.get('id', '?')} has invalid record index {record_index}")

        replacement_values = replacement_values_for_entry(entry)
        if replacement_values is None:
            continue

        record = table.entries[record_index]
        relative_span = find_run_payload_span(data[record.offset : record.end_offset], run_index)
        start = record.offset + relative_span[0]
        end = record.offset + relative_span[1]
        original_units = (end - start) // 2
        if len(replacement_values) > original_units:
            raise ValueError(f"replacement for entry {entry.get('id', '?')} is too long")

        padded = replacement_values + [0] * (original_units - len(replacement_values))
        data[start:end] = struct.pack("<" + "H" * len(padded), *padded)
        applied += 1

    output_path.write_bytes(data)
    return applied


def replacement_values_for_entry(entry: dict[str, Any]) -> list[int] | None:
    kind = entry.get("kind")
    source_text = str(entry.get("text") or "")
    replacement_text = str(entry.get("translation") or "")
    replacement_codes = entry.get("translation_codes")

    if kind == "text":
        if not replacement_text or replacement_text == source_text:
            return None
        return encode_u16_ascii_text(replacement_text, max_units=int(entry["length"]))

    if kind == "glyph_codes":
        if not replacement_codes:
            return None
        values = parse_u16_code_list(replacement_codes)
        max_units = int(entry["length"])
        if len(values) > max_units:
            raise ValueError(f"replacement has {len(values)} code units, max is {max_units}")
        return values

    return None


def encode_u16_ascii_text(text: str, max_units: int) -> list[int]:
    values: list[int] = []
    for char in text:
        if char == "\n":
            value = 0x000A
        else:
            value = ord(char)
        if value > 0x7E or (value < 0x20 and value != 0x000A):
            raise ValueError(f"offset-table text importer only supports ASCII and newlines: {char!r}")
        values.append(value)
    if len(values) > max_units:
        raise ValueError(f"replacement has {len(values)} code units, max is {max_units}")
    return values


def parse_u16_code_list(codes: Any) -> list[int]:
    if isinstance(codes, str):
        raw_values = codes.replace(",", " ").split()
    elif isinstance(codes, list):
        raw_values = codes
    else:
        raise ValueError("translation_codes must be a list or whitespace/comma separated string")

    values = [int(str(value), 0) for value in raw_values]
    for value in values:
        if value < 0 or value > 0xFFFF:
            raise ValueError(f"code value outside u16 range: {value}")
    return values


def find_run_payload_span(record: bytes, target_run_index: int) -> tuple[int, int]:
    values = read_u16_values(record)
    cursor = initial_run_cursor(values)
    if cursor is None:
        raise ValueError("record does not have a recognized offset-table run prefix")

    run_index = 0
    while cursor < len(values):
        length = values[cursor]
        if length == 0:
            cursor += 1
            continue
        if length > len(values) - cursor - 1:
            break

        payload_start_unit = cursor + 1
        payload_end_unit = payload_start_unit + length
        trimmed_end_unit = payload_end_unit - 1 if values[payload_end_unit - 1] == 0 else payload_end_unit

        if trimmed_end_unit > payload_start_unit:
            if run_index == target_run_index:
                return payload_start_unit * 2, payload_end_unit * 2
            run_index += 1

        cursor = payload_end_unit

    raise ValueError(f"run index {target_run_index} not found in record")


def main() -> int:
    parser = argparse.ArgumentParser(description="Import edited JSON text into a copy of a source file.")
    parser.add_argument("source", type=Path, help="Original source binary file.")
    parser.add_argument("json", type=Path, help="Edited extraction JSON.")
    parser.add_argument("output", type=Path, help="Output binary file. The source is never modified in place.")
    args = parser.parse_args()

    applied = import_text(args.source, args.json, args.output)
    print(f"applied {applied} entries to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
