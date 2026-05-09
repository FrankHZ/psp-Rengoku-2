from __future__ import annotations

import argparse
from pathlib import Path

from tdl import replace_tdl_children


def parse_replacement(value: str) -> tuple[int, Path]:
    child, separator, path = value.partition("=")
    if not separator:
        raise argparse.ArgumentTypeError("replacement must be CHILD_INDEX=PATH")
    try:
        child_index = int(child, 0)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"invalid child index: {child!r}") from error
    return child_index, Path(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Replace one or more same-size child resources in a .TDL container.")
    parser.add_argument("source", type=Path, help="Source .TDL file.")
    parser.add_argument("output", type=Path, help="Output .TDL file. The source is never modified in place.")
    parser.add_argument(
        "--replace",
        dest="replacements",
        action="append",
        type=parse_replacement,
        required=True,
        help="Replacement pair as CHILD_INDEX=PATH. May be repeated.",
    )
    args = parser.parse_args()

    replace_tdl_children(args.source, dict(args.replacements), args.output)
    print(f"replaced {len(args.replacements)} children into {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
