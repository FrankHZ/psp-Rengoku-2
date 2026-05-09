from __future__ import annotations

import argparse
from pathlib import Path

from mig import read_mig


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a MIG.00.1PSP resource.")
    parser.add_argument("input", type=Path, nargs="+", help="MIG files to inspect.")
    args = parser.parse_args()

    print("path\tsize\trecords\twidth\theight\tbpp\tpalette_offset\tpixel_offset\tpixel_size")
    for path in args.input:
        mig = read_mig(path)
        records = "; ".join(
            f"{record.kind}:{record.offset_or_size}:{record.size_or_width}:{record.alignment_or_height}"
            for record in mig.records
        )
        print(
            f"{path}\t{path.stat().st_size}\t{records}\t{mig.width or ''}\t{mig.height or ''}\t"
            f"{mig.bits_per_pixel or ''}\t{mig.palette_offset if mig.palette_offset is not None else ''}\t"
            f"{mig.pixel_offset if mig.pixel_offset is not None else ''}\t{mig.pixel_size or ''}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

