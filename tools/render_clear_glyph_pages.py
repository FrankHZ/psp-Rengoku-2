from __future__ import annotations

import argparse
import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from mig import decode_mig_indices


DEFAULT_INPUT = Path("local/work/tdl_DATA001_0002")
DEFAULT_OUTPUT = Path("local/work/jp_glyph_clear_pages_v1")

PAGE_SPECS = (
    {"child": 0, "source": "codeANK9x14_00_0", "file": "0000_codeANK9x14_00_0.bin", "cols": 14, "rows": 9, "cell_w": 9, "cell_h": 14, "base_low": 0x0000, "base_high": ""},
    {"child": 1, "source": "codeJAP14x14_00_", "file": "0001_codeJAP14x14_00_.bin", "cols": 9, "rows": 9, "cell_w": 14, "cell_h": 14, "base_low": 0x0100, "base_high": 0x0151},
    {"child": 2, "source": "codeJAP14x14_02_", "file": "0002_codeJAP14x14_02_.bin", "cols": 9, "rows": 9, "cell_w": 14, "cell_h": 14, "base_low": 0x01A2, "base_high": 0x01F3},
    {"child": 3, "source": "codeJAP14x14_04_", "file": "0003_codeJAP14x14_04_.bin", "cols": 9, "rows": 9, "cell_w": 14, "cell_h": 14, "base_low": 0x0244, "base_high": 0x0295},
    {"child": 4, "source": "codeJAP14x14_06_", "file": "0004_codeJAP14x14_06_.bin", "cols": 9, "rows": 9, "cell_w": 14, "cell_h": 14, "base_low": 0x02E6, "base_high": 0x0337},
    {"child": 5, "source": "codeJAP14x14_08_", "file": "0005_codeJAP14x14_08_.bin", "cols": 9, "rows": 9, "cell_w": 14, "cell_h": 14, "base_low": 0x0388, "base_high": 0x03D9},
    {"child": 6, "source": "codeJAP14x14_10_", "file": "0006_codeJAP14x14_10_.bin", "cols": 9, "rows": 9, "cell_w": 14, "cell_h": 14, "base_low": 0x042A, "base_high": 0x047B},
    {"child": 7, "source": "codeJAP14x14_12_", "file": "0007_codeJAP14x14_12_.bin", "cols": 9, "rows": 9, "cell_w": 14, "cell_h": 14, "base_low": 0x04CC, "base_high": 0x051D},
    {"child": 8, "source": "codeJAP14x14_14_", "file": "0008_codeJAP14x14_14_.bin", "cols": 9, "rows": 9, "cell_w": 14, "cell_h": 14, "base_low": 0x056E, "base_high": 0x05BF},
    {"child": 9, "source": "codeJAP14x14_16_", "file": "0009_codeJAP14x14_16_.bin", "cols": 9, "rows": 9, "cell_w": 14, "cell_h": 14, "base_low": 0x0610, "base_high": 0x0661},
    {"child": 10, "source": "codeJAP14x14_18_", "file": "0010_codeJAP14x14_18_.bin", "cols": 9, "rows": 9, "cell_w": 14, "cell_h": 14, "base_low": 0x06B2, "base_high": 0x0703},
    {"child": 11, "source": "codeJAP14x14_20_", "file": "0011_codeJAP14x14_20_.bin", "cols": 9, "rows": 9, "cell_w": 14, "cell_h": 14, "base_low": 0x0754, "base_high": 0x07A5},
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render clean high-res low/high glyph pages for OCR.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--scale", type=int, default=8)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if args.output_dir.exists() and not args.overwrite:
        raise FileExistsError(f"{args.output_dir} already exists; pass --overwrite")
    render_pages(args.input_dir, args.output_dir, args.scale)
    print(f"wrote {args.output_dir}")
    return 0


def render_pages(input_dir: Path, output_dir: Path, scale: int) -> None:
    pages_dir = output_dir / "pages"
    grid_dir = output_dir / "pages_grid"
    cells_dir = output_dir / "cells"
    original_dir = output_dir / "original_pages"
    original_scaled_dir = output_dir / "original_pages_scaled"
    original_2bpp_dir = output_dir / "original_pages_2bpp"
    original_4bpp_dir = output_dir / "original_pages_4bpp"
    pages_dir.mkdir(parents=True, exist_ok=True)
    grid_dir.mkdir(parents=True, exist_ok=True)
    cells_dir.mkdir(parents=True, exist_ok=True)
    original_dir.mkdir(parents=True, exist_ok=True)
    original_scaled_dir.mkdir(parents=True, exist_ok=True)
    original_2bpp_dir.mkdir(parents=True, exist_ok=True)
    original_4bpp_dir.mkdir(parents=True, exist_ok=True)

    manifest_rows: list[dict[str, str]] = []
    for spec in PAGE_SPECS:
        path = input_dir / str(spec["file"])
        width, _height, indices = decode_mig_indices(path)
        full_4bpp = render_4bpp_index_page(indices, width, scale=1)
        full_4bpp_scaled = full_4bpp.resize((full_4bpp.width * scale, full_4bpp.height * scale), Image.Resampling.NEAREST)
        full_stem = f"child{int(spec['child']):02d}_{spec['source']}_4bpp"
        full_4bpp.save(original_4bpp_dir / f"{full_stem}.png")
        full_4bpp_scaled.save(original_4bpp_dir / f"{full_stem}_scaled.png")
        for layer in ("low", "high"):
            base = spec["base_low"] if layer == "low" else spec["base_high"]
            page = render_page(
                indices,
                width,
                int(spec["cols"]),
                int(spec["rows"]),
                int(spec["cell_w"]),
                int(spec["cell_h"]),
                layer,
                scale,
                cropped=True,
            )
            original = render_page(
                indices,
                width,
                int(spec["cols"]),
                int(spec["rows"]),
                int(spec["cell_w"]),
                int(spec["cell_h"]),
                layer,
                scale=1,
                cropped=False,
            )
            stem = f"child{int(spec['child']):02d}_{spec['source']}_{layer}"
            original_2bpp = render_2bpp_page(indices, width, layer)
            page.save(pages_dir / f"{stem}.png")
            original.save(original_dir / f"{stem}.png")
            original.resize((original.width * scale, original.height * scale), Image.Resampling.NEAREST).save(
                original_scaled_dir / f"{stem}_scaled.png"
            )
            original_2bpp.save(original_2bpp_dir / f"{stem}_2bpp.png")
            original_2bpp.resize((original_2bpp.width * scale, original_2bpp.height * scale), Image.Resampling.NEAREST).save(
                original_2bpp_dir / f"{stem}_2bpp_scaled.png"
            )
            add_grid(page, int(spec["cols"]), int(spec["rows"]), scale).save(grid_dir / f"{stem}_grid.png")

            for cell in range(int(spec["cols"]) * int(spec["rows"])):
                crop = crop_cell(page, cell, int(spec["cols"]), int(spec["cell_w"]), int(spec["cell_h"]), scale)
                crop_name = f"{stem}_cell{cell:03d}.png"
                crop.save(cells_dir / crop_name)
                code = "" if base == "" else f"0x{int(base) + cell:04x}"
                manifest_rows.append(
                    {
                        "child": str(spec["child"]),
                        "source": str(spec["source"]),
                        "layer": layer,
                        "base": "" if base == "" else f"0x{int(base):04x}",
                        "cell": str(cell),
                        "row": str(cell // int(spec["cols"])),
                        "col": str(cell % int(spec["cols"])),
                        "code": code,
                        "page_png": f"pages/{stem}.png",
                        "original_page_png": f"original_pages/{stem}.png",
                        "original_scaled_page_png": f"original_pages_scaled/{stem}_scaled.png",
                        "original_2bpp_png": f"original_pages_2bpp/{stem}_2bpp.png",
                        "original_2bpp_scaled_png": f"original_pages_2bpp/{stem}_2bpp_scaled.png",
                        "original_4bpp_png": f"original_pages_4bpp/{full_stem}.png",
                        "original_4bpp_scaled_png": f"original_pages_4bpp/{full_stem}_scaled.png",
                        "grid_png": f"pages_grid/{stem}_grid.png",
                        "cell_png": f"cells/{crop_name}",
                    }
                )

    write_manifest(output_dir / "manifest.csv", manifest_rows)
    write_combined_images(output_dir, pages_dir, "combined_24_pages")
    write_combined_images(output_dir, original_scaled_dir, "combined_24_original_pages_scaled")
    write_combined_images(output_dir, original_2bpp_dir, "combined_24_original_pages_2bpp", suffix="_scaled.png")
    write_combined_images(output_dir, original_4bpp_dir, "combined_12_original_pages_4bpp", suffix="_scaled.png")
    write_readme(output_dir / "README.md", scale)


def render_page(
    indices: bytes,
    texture_width: int,
    cols: int,
    rows: int,
    cell_w: int,
    cell_h: int,
    layer: str,
    scale: int,
    cropped: bool,
) -> Image.Image:
    image = Image.new("L", (cols * cell_w if cropped else texture_width, rows * cell_h if cropped else len(indices) // texture_width), 255)
    pixels = image.load()
    for row in range(rows):
        for col in range(cols):
            for y in range(cell_h):
                for x in range(cell_w):
                    src_x = col * cell_w + x
                    src_y = row * cell_h + y
                    value = indices[src_y * texture_width + src_x]
                    visible = (value & 0x03) != 0 if layer == "low" else (value & 0x0C) != 0
                    if visible:
                        pixels[src_x, src_y] = 0
    return image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)


def render_2bpp_page(indices: bytes, texture_width: int, layer: str) -> Image.Image:
    height = len(indices) // texture_width
    image = Image.new("L", (texture_width, height), 255)
    pixels = image.load()
    levels = (255, 170, 85, 0)
    for y in range(height):
        for x in range(texture_width):
            value = indices[y * texture_width + x]
            two_bit = value & 0x03 if layer == "low" else (value >> 2) & 0x03
            pixels[x, y] = levels[two_bit]
    return image


def render_4bpp_index_page(indices: bytes, texture_width: int, scale: int) -> Image.Image:
    height = len(indices) // texture_width
    image = Image.new("L", (texture_width, height), 255)
    pixels = image.load()
    for y in range(height):
        for x in range(texture_width):
            value = indices[y * texture_width + x]
            pixels[x, y] = 255 - value * 17
    if scale == 1:
        return image
    return image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)


def add_grid(page: Image.Image, cols: int, rows: int, scale: int) -> Image.Image:
    grid = page.convert("RGB")
    draw = ImageDraw.Draw(grid)
    cell = 14 * scale
    for col in range(cols + 1):
        x = col * cell
        draw.line((x, 0, x, rows * cell), fill=(210, 210, 210))
    for row in range(rows + 1):
        y = row * cell
        draw.line((0, y, cols * cell, y), fill=(210, 210, 210))
    return grid


def crop_cell(page: Image.Image, cell: int, cols: int, cell_w: int, cell_h: int, scale: int) -> Image.Image:
    width = cell_w * scale
    height = cell_h * scale
    row = cell // cols
    col = cell % cols
    return page.crop((col * width, row * height, (col + 1) * width, (row + 1) * height))


def write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_combined_images(output_dir: Path, pages_dir: Path, output_stem: str, suffix: str = ".png") -> None:
    page_paths = sorted(pages_dir.glob(f"*{suffix}"))
    if not page_paths:
        return

    images = [(path, Image.open(path).convert("L")) for path in page_paths]
    tile_w = max(image.width for _path, image in images)
    tile_h = max(image.height for _path, image in images)
    columns = 4
    rows = (len(images) + columns - 1) // columns
    gap = 24
    label_h = 24

    mosaic = Image.new("L", (columns * tile_w + (columns - 1) * gap, rows * tile_h + (rows - 1) * gap), 255)
    labeled = Image.new(
        "RGB",
        (columns * tile_w + (columns - 1) * gap, rows * (tile_h + label_h) + (rows - 1) * gap),
        "white",
    )
    draw = ImageDraw.Draw(labeled)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", size=16)
    except OSError:
        font = ImageFont.load_default()

    for index, (path, image) in enumerate(images):
        col = index % columns
        row = index // columns
        x = col * (tile_w + gap)
        y = row * (tile_h + gap)
        mosaic.paste(image, (x, y))
        labeled_y = row * (tile_h + label_h + gap)
        labeled.paste(image.convert("RGB"), (x, labeled_y + label_h))
        draw.text((x, labeled_y + 3), path.stem, fill=(0, 0, 0), font=font)

    mosaic.save(output_dir / f"{output_stem}_unlabeled.png")
    labeled.save(output_dir / f"{output_stem}_labeled.png")


def write_readme(path: Path, scale: int) -> None:
    lines = [
        "# Clear JP Glyph Pages v1",
        "",
        "Clean black-on-white renders for OCR/API experiments.",
        "",
        "## Contents",
        "",
        "- `pages/`: 24 unlabeled high-res pages, one low/high layer per font child.",
        "- `original_pages/`: 24 native 128x128 low/high layer pages preserving the original canvas.",
        "- `original_pages_scaled/`: the same original-canvas pages scaled up for OCR/review.",
        "- `original_pages_2bpp/`: 24 native/scaled low/high 2bpp grayscale pages preserving 0-3 layer values.",
        "- `original_pages_4bpp/`: 12 native/scaled full 4bpp grayscale index pages preserving 0-15 values.",
        "- `pages_grid/`: the same 24 pages with faint grid lines for visual review.",
        "- `cells/`: individual high-res cell crops.",
        "- `combined_24_pages_unlabeled.png`: one label-free mosaic of all 24 pages.",
        "- `combined_24_pages_labeled.png`: one labeled review mosaic of all 24 pages.",
        "- `combined_24_original_pages_scaled_unlabeled.png`: one label-free mosaic preserving original page canvases.",
        "- `combined_24_original_pages_scaled_labeled.png`: labeled review mosaic preserving original page canvases.",
        "- `combined_24_original_pages_2bpp_unlabeled.png`: combined scaled low/high 2bpp grayscale pages.",
        "- `combined_12_original_pages_4bpp_unlabeled.png`: combined scaled full 4bpp index pages.",
        "- `manifest.csv`: child/layer/cell/code mapping for pages and crops.",
        "",
        "## Render Settings",
        "",
        f"- Scale: {scale}x nearest-neighbor from original 14x14 glyph cells.",
        "- Ink: black pixels on white background.",
        "- Binary OCR pages: low layer `value & 0x03 != 0`; high layer `value & 0x0c != 0`.",
        "- 2bpp pages: grayscale levels preserve each layer's values 0-3.",
        "- 4bpp pages: grayscale levels preserve full original index values 0-15.",
        "",
        "The main `pages/` images contain no labels or grid lines, so they are the",
        "best OCR inputs. Use `manifest.csv` to map OCR results back to codepoints.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
