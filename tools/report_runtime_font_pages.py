from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path

from PIL import Image, ImageDraw

from map_runtime_font_pages import parse_dump_address, parse_dump_hashes


def main() -> int:
    parser = argparse.ArgumentParser(description="Report distinct PPSSPP dumped runtime font-page observations.")
    parser.add_argument("dump_dir", type=Path, help="Directory containing PPSSPP dumped texture PNG files.")
    parser.add_argument("--output-dir", type=Path, default=Path("local/work/runtime_font_page_scan_v1"))
    parser.add_argument("--cell-width", type=int, default=14)
    parser.add_argument("--cell-height", type=int, default=14)
    parser.add_argument("--columns", type=int, default=9)
    parser.add_argument("--rows", type=int, default=9)
    args = parser.parse_args()

    rows = scan_runtime_font_pages(
        args.dump_dir,
        args.cell_width,
        args.cell_height,
        args.columns,
        args.rows,
    )
    write_report(rows, args.output_dir, args.dump_dir, args.columns, args.rows)
    print(f"wrote {args.output_dir}")
    return 0


def scan_runtime_font_pages(
    dump_dir: Path,
    cell_width: int = 14,
    cell_height: int = 14,
    columns: int = 9,
    rows: int = 9,
) -> list[dict[str, object]]:
    files = sorted(path for path in dump_dir.glob("*.png") if path.is_file())
    observations: list[dict[str, object]] = []
    for index, path in enumerate(files):
        image = Image.open(path).convert("RGBA")
        width, height = image.size
        rgba = image.tobytes()
        first_row = image.crop((0, 0, min(width, columns * cell_width), min(height, cell_height))).tobytes()
        cell_counts = first_row_cell_ink_counts(image, cell_width, cell_height, columns)
        full_grid_counts = grid_ink_counts(image, cell_width, cell_height, columns, rows)
        clut_hash, texture_hash = parse_dump_hashes(path)
        observations.append(
            {
                "index": index,
                "file": path.name,
                "address": f"0x{parse_dump_address(path):08x}",
                "clut_hash": clut_hash,
                "texture_hash": texture_hash,
                "width": width,
                "height": height,
                "rgba_sha1": hashlib.sha1(rgba).hexdigest(),
                "first_row_sha1": hashlib.sha1(first_row).hexdigest(),
                "first_row_counts": " ".join(str(value) for value in cell_counts),
                "grid_counts": " ".join(str(value) for value in full_grid_counts),
            }
        )

    assign_group_ids(observations, "rgba_sha1", "pixel_group")
    assign_group_ids(observations, "first_row_sha1", "first_row_group")
    return observations


def first_row_cell_ink_counts(image: Image.Image, cell_width: int, cell_height: int, columns: int) -> list[int]:
    return grid_ink_counts(image, cell_width, cell_height, columns, 1)


def grid_ink_counts(image: Image.Image, cell_width: int, cell_height: int, columns: int, rows: int) -> list[int]:
    pixels = image.load()
    counts: list[int] = []
    for row in range(rows):
        for column in range(columns):
            x0 = column * cell_width
            y0 = row * cell_height
            count = 0
            for y in range(y0, min(y0 + cell_height, image.height)):
                for x in range(x0, min(x0 + cell_width, image.width)):
                    red, green, blue, alpha = pixels[x, y]
                    if alpha and (red or green or blue):
                        count += 1
            counts.append(count)
    return counts


def assign_group_ids(rows: list[dict[str, object]], key: str, output_key: str) -> None:
    groups: dict[object, int] = {}
    for row in rows:
        value = row[key]
        if value not in groups:
            groups[value] = len(groups) + 1
        row[output_key] = groups[value]


def write_report(rows: list[dict[str, object]], output_dir: Path, dump_dir: Path, columns: int, grid_rows: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "runtime_font_pages.csv"
    fieldnames = [
        "index",
        "file",
        "address",
        "clut_hash",
        "texture_hash",
        "width",
        "height",
        "pixel_group",
        "first_row_group",
        "rgba_sha1",
        "first_row_sha1",
        "first_row_counts",
        "grid_counts",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row[key] for key in fieldnames})

    write_contact_sheet(rows, dump_dir, output_dir / "runtime_font_pages_contact_sheet.png")
    write_markdown(rows, output_dir / "README.md", columns, grid_rows)


def write_contact_sheet(rows: list[dict[str, object]], dump_dir: Path, output_path: Path) -> None:
    if not rows:
        return
    images = [(row, Image.open(dump_dir / str(row["file"])).convert("RGBA")) for row in rows]
    tile_width = 128
    label_height = 34
    sheet_columns = 3
    sheet_rows = (len(images) + sheet_columns - 1) // sheet_columns
    sheet = Image.new("RGBA", (sheet_columns * tile_width, sheet_rows * (128 + label_height)), (20, 20, 20, 255))
    draw = ImageDraw.Draw(sheet)
    for index, (row, image) in enumerate(images):
        x = (index % sheet_columns) * tile_width
        y = (index // sheet_columns) * (128 + label_height)
        sheet.alpha_composite(image, (x, y))
        label = f"{row['index']:02d} {str(row['file'])[:18]}"
        draw.text((x + 2, y + 130), label, fill=(255, 255, 255, 255))
    sheet.save(output_path)


def write_markdown(rows: list[dict[str, object]], output_path: Path, columns: int, grid_rows: int) -> None:
    unique_pixels = len({row["rgba_sha1"] for row in rows})
    unique_first_rows = len({row["first_row_sha1"] for row in rows})
    addresses = sorted({row["address"] for row in rows})
    lines = [
        "# Runtime Font Page Scan",
        "",
        "Purpose: inventory PPSSPP dumped font-page PNGs without collapsing same-address CLUT variants.",
        "",
        "## Summary",
        "",
        f"- Dumped PNG observations: {len(rows)}",
        f"- Unique full RGBA pages: {unique_pixels}",
        f"- Unique first-row fingerprints: {unique_first_rows}",
        f"- Runtime address slots: {len(addresses)}",
        f"- Assumed grid for fingerprints: {columns} x {grid_rows} cells",
        "",
        "Same address does not imply same rendered page in these dumps. Treat each PNG as a separate runtime observation until a patch probe proves storage/routing behavior.",
        "",
        "## Files",
        "",
        "- `runtime_font_pages.csv`: per-PNG hashes, address/hash fields, and cell ink-count fingerprints.",
        "- `runtime_font_pages_contact_sheet.png`: visual overview of all dumped observations.",
        "",
        "## Observations",
        "",
        "| # | File | Address | CLUT | Texture | Pixel group | First-row group | First-row counts |",
        "| ---: | --- | --- | --- | --- | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['index']} | `{row['file']}` | `{row['address']}` | `{row['clut_hash']}` | "
            f"`{row['texture_hash']}` | {row['pixel_group']} | {row['first_row_group']} | "
            f"`{row['first_row_counts']}` |"
        )
    lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
