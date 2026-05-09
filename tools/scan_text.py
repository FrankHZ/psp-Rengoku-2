from __future__ import annotations

import argparse
import sys
from pathlib import Path

from text_codec import find_candidate_spans, has_japanese


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan a binary file for candidate text strings.")
    parser.add_argument("input", type=Path, help="File to scan.")
    parser.add_argument("--min-length", type=int, default=4, help="Minimum decoded character length.")
    parser.add_argument(
        "--encoding",
        action="append",
        choices=("ascii", "utf-8", "shift_jis"),
        help="Encoding to scan. May be repeated. Defaults to all supported encodings.",
    )
    parser.add_argument("--require-japanese", action="store_true", help="Only print spans containing Japanese text.")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

    data = args.input.read_bytes()
    encodings = tuple(args.encoding) if args.encoding else ("ascii", "utf-8", "shift_jis")
    try:
        for span in find_candidate_spans(data, args.min_length, encodings=encodings):
            if args.require_japanese and not has_japanese(span.text):
                continue
            preview = span.text.replace("\n", "\\n").replace("\r", "\\r")
            print(f"0x{span.offset:08X}\t{span.length}\t{span.encoding}\t{preview}")
    except OSError:
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
