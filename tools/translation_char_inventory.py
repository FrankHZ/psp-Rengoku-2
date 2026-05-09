from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def collect_translation_chars(paths: list[Path], fields: tuple[str, ...]) -> dict[str, Any]:
    chars: set[str] = set()
    cjk_chars: set[str] = set()
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        for entry in payload.get("entries", []):
            for field in fields:
                text = entry.get(field)
                if not isinstance(text, str):
                    continue
                for char in text:
                    if char in {"\r", "\n", "\t", " "}:
                        continue
                    chars.add(char)
                    if is_cjk(char):
                        cjk_chars.add(char)
    return {
        "fields": list(fields),
        "total_unique": len(chars),
        "cjk_unique": len(cjk_chars),
        "chars": "".join(sorted(chars, key=ord)),
        "cjk_chars": "".join(sorted(cjk_chars, key=ord)),
    }


def is_cjk(char: str) -> bool:
    codepoint = ord(char)
    return (
        0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xF900 <= codepoint <= 0xFAFF
        or 0x20000 <= codepoint <= 0x2EBEF
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Count unique characters needed by local translation JSON drafts.")
    parser.add_argument("input", type=Path, nargs="+", help="JSON files with an entries array.")
    parser.add_argument("--field", action="append", default=None, help="Text field to scan. Defaults to chs_translation.")
    parser.add_argument("--output", type=Path, help="Optional JSON report path.")
    args = parser.parse_args()

    fields = tuple(args.field) if args.field else ("chs_translation",)
    report = collect_translation_chars(args.input, fields)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"fields\t{','.join(fields)}")
    print(f"total_unique\t{report['total_unique']}")
    print(f"cjk_unique\t{report['cjk_unique']}")
    print(f"chars\t{report['chars']}")
    print(f"cjk_chars\t{report['cjk_chars']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
