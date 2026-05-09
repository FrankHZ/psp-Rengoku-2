from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Placeholder for patch generation from clean source image to rebuilt translated image."
    )
    parser.add_argument("source", type=Path, help="Clean source image path.")
    parser.add_argument("modified", type=Path, help="Rebuilt modified image path.")
    parser.add_argument("output", type=Path, help="Patch output path.")
    parser.add_argument(
        "--format",
        choices=("xdelta", "ppf", "bps"),
        default="xdelta",
        help="Patch format to generate once implemented.",
    )
    args = parser.parse_args()

    raise SystemExit(
        "patch generation is not implemented yet. "
        f"Requested {args.format} patch from {args.source} to {args.modified} at {args.output}."
    )


if __name__ == "__main__":
    raise SystemExit(main())

