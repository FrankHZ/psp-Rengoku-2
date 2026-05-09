from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_ENCODINGS = ("utf-8", "shift_jis", "cp932", "euc_jp")


def main() -> int:
    parser = argparse.ArgumentParser(description="Search files for exact text phrases encoded with common encodings.")
    parser.add_argument("root", type=Path, help="File or directory to search.")
    parser.add_argument("phrases", nargs="+", help="Text phrases to encode and search for.")
    parser.add_argument("--encoding", action="append", dest="encodings", help="Encoding to try. Can be repeated.")
    args = parser.parse_args()

    encodings = tuple(args.encodings or DEFAULT_ENCODINGS)
    files = expand_files(args.root)
    any_hit = False

    for phrase in args.phrases:
        print(f"TEXT\t{phrase}")
        hits = search_phrase(files, phrase, encodings)
        if not hits:
            print("MISS")
            continue
        any_hit = True
        for hit in hits:
            print(f"HIT\t{hit['encoding']}\t{hit['path']}\t0x{hit['offset']:x}")

    return 0 if any_hit else 1


def search_phrase(files: list[Path], phrase: str, encodings: tuple[str, ...]) -> list[dict[str, object]]:
    hits: list[dict[str, object]] = []
    encoded_patterns: list[tuple[str, bytes]] = []
    for encoding in encodings:
        try:
            encoded_patterns.append((encoding, phrase.encode(encoding)))
        except UnicodeEncodeError:
            continue

    for path in files:
        data = path.read_bytes()
        for encoding, pattern in encoded_patterns:
            start = 0
            while True:
                offset = data.find(pattern, start)
                if offset < 0:
                    break
                hits.append({"path": path, "encoding": encoding, "offset": offset})
                start = offset + 1
    return hits


def expand_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    if root.is_dir():
        return sorted(path for path in root.rglob("*") if path.is_file())
    raise FileNotFoundError(root)


if __name__ == "__main__":
    raise SystemExit(main())
