from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from runtime_texture_inventory import png_color_type_name, png_info


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Map PPSSPP dumped font texture addresses to extracted static font pages."
    )
    parser.add_argument("dump_dir", type=Path, help="Directory containing PPSSPP dumped texture PNG files.")
    parser.add_argument("static_dir", type=Path, help="Directory containing rendered static MIG page PNG files.")
    parser.add_argument(
        "--base-address",
        type=lambda value: int(value, 0),
        help="Address for static page 0. Defaults to the lowest dumped texture address.",
    )
    parser.add_argument("--page-size", type=lambda value: int(value, 0), default=0x2100)
    args = parser.parse_args()

    rows = map_runtime_pages(args.dump_dir, args.static_dir, args.base_address, args.page_size)

    print("runtime_address\tpage_index\tstatic_page\tcount\tpng_format\tfiles")
    for row in rows:
        print(
            f"0x{row['address']:08x}\t{row['page_index']}\t{row['static_page']}\t{row['count']}\t"
            f"{row['png_format']}\t{row['files']}"
        )
    return 0


def map_runtime_pages(
    dump_dir: Path,
    static_dir: Path,
    base_address: int | None = None,
    page_size: int = 0x2100,
) -> list[dict[str, object]]:
    runtime_files = sorted(path for path in dump_dir.glob("*.png") if path.is_file())
    static_files = sorted(path for path in static_dir.glob("*.png") if path.is_file())
    by_address: dict[int, list[Path]] = defaultdict(list)

    for path in runtime_files:
        by_address[parse_dump_address(path)].append(path)

    if not by_address:
        return []

    resolved_base = min(by_address) if base_address is None else base_address
    rows: list[dict[str, object]] = []
    for address, paths in sorted(by_address.items()):
        delta = address - resolved_base
        page_index = delta // page_size if delta >= 0 else -1
        exact_stride = delta >= 0 and delta % page_size == 0
        static_page = static_files[page_index].name if exact_stride and page_index < len(static_files) else ""
        width, height, bit_depth, color_type = png_info(paths[0])
        rows.append(
            {
                "address": address,
                "page_index": page_index if exact_stride else "",
                "static_page": static_page,
                "count": len(paths),
                "png_format": f"{width}x{height} {png_color_type_name(color_type, bit_depth)}",
                "files": ", ".join(path.name for path in paths),
            }
        )
    return rows


def parse_dump_address(path: Path) -> int:
    stem_prefix = path.name[:8]
    try:
        return int(stem_prefix, 16)
    except ValueError as error:
        raise ValueError(f"{path.name} does not start with an 8-digit hex texture address") from error


if __name__ == "__main__":
    raise SystemExit(main())
