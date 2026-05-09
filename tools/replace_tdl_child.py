from __future__ import annotations

import argparse
from pathlib import Path

from tdl import replace_tdl_child


def main() -> int:
    parser = argparse.ArgumentParser(description="Replace one same-size child resource in a .TDL container.")
    parser.add_argument("source", type=Path, help="Source .TDL file.")
    parser.add_argument("child_index", type=int, help="TDL child index to replace.")
    parser.add_argument("replacement", type=Path, help="Same-size replacement child payload.")
    parser.add_argument("output", type=Path, help="Output .TDL file. The source is never modified in place.")
    args = parser.parse_args()

    replace_tdl_child(args.source, args.child_index, args.replacement, args.output)
    print(f"replaced child {args.child_index} into {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
