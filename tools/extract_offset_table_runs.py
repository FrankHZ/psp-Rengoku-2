from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct

from offset_table import read_offset_table


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract length-prefixed text/code runs from offset-table records.")
    parser.add_argument("input", type=Path, nargs="+", help="Offset-table files or directories.")
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    parser.add_argument("--limit", type=int, default=40)
    args = parser.parse_args()

    rows = []
    for path in expand_inputs(args.input):
        try:
            rows.extend(extract_file_runs(path))
        except ValueError:
            continue

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    print("file\tentry\trun\tkind\tlength\ttext_or_codes")
    for row in rows[: args.limit]:
        value = row["text"] if row["kind"] == "text" else " ".join(row["codes"])
        print(f"{row['file']}\t{row['entry']}\t{row['run']}\t{row['kind']}\t{row['length']}\t{value}")
    return 0


def extract_file_runs(path: Path) -> list[dict[str, object]]:
    table = read_offset_table(path)
    data = path.read_bytes()
    rows: list[dict[str, object]] = []
    for entry in table.entries:
        record = data[entry.offset : entry.end_offset]
        values = read_u16_values(record)
        for run_index, run in enumerate(parse_record_runs(values)):
            rows.append(
                {
                    "file": path.name,
                    "entry": entry.index,
                    "entry_offset": entry.offset,
                    "run": run_index,
                    "kind": classify_run(run),
                    "length": len(run),
                    "text": decode_ascii_run(run),
                    "codes": [f"0x{value:04x}" for value in run],
                }
            )
    return rows


def parse_record_runs(values: tuple[int, ...]) -> list[tuple[int, ...]]:
    cursor = initial_run_cursor(values)
    if cursor is None:
        return []

    runs: list[tuple[int, ...]] = []
    while cursor < len(values):
        length = values[cursor]
        if length == 0:
            cursor += 1
            continue
        if length > len(values) - cursor - 1:
            break
        run = values[cursor + 1 : cursor + 1 + length]
        if not run:
            break
        trimmed = trim_terminator(run)
        if trimmed:
            runs.append(trimmed)
        cursor += 1 + length
    return runs


def initial_run_cursor(values: tuple[int, ...]) -> int | None:
    if len(values) < 13:
        return None
    if values[:8] != (1, 0, 1, 0, 0x000C, 0, 2, 0):
        return None
    if len(values) >= 13 and values[8:12] == (1, 0, 0x000C, 0):
        return 12
    if len(values) >= 15 and values[8:12] == (2, 0, 0x0010, 0):
        return 14
    return None


def trim_terminator(run: tuple[int, ...]) -> tuple[int, ...]:
    if run and run[-1] == 0:
        return run[:-1]
    return run


def classify_run(run: tuple[int, ...]) -> str:
    if run and all(value in {0x000A, 0x000D} or 0x20 <= value < 0x7F for value in run):
        return "text"
    return "glyph_codes"


def decode_ascii_run(run: tuple[int, ...]) -> str:
    if classify_run(run) != "text":
        return ""
    return "".join("\n" if value == 0x000A else chr(value) for value in run)


def read_u16_values(data: bytes) -> tuple[int, ...]:
    even_size = len(data) - (len(data) % 2)
    if even_size == 0:
        return ()
    return struct.unpack(f"<{even_size // 2}H", data[:even_size])


def expand_inputs(paths: list[Path]) -> list[Path]:
    expanded: list[Path] = []
    for path in paths:
        if path.is_dir():
            expanded.extend(sorted(child for child in path.glob("*.bin") if child.is_file()))
        elif path.is_file():
            expanded.append(path)
        else:
            raise FileNotFoundError(path)
    return expanded


if __name__ == "__main__":
    raise SystemExit(main())
