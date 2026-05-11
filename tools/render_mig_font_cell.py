from __future__ import annotations

import argparse
from pathlib import Path

from analyze_font_grid import parse_cell_size
from mig import decode_mig_indices, replace_mig_indices, write_png_rgba

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError:  # pragma: no cover - exercised when dependency is missing.
    Image = ImageDraw = ImageFilter = ImageFont = None


def require_pillow() -> None:
    if Image is None or ImageDraw is None or ImageFilter is None or ImageFont is None:
        raise SystemExit("render_mig_font_cell.py requires Pillow. Install with: pip install Pillow")


def has_pillow() -> bool:
    return Image is not None and ImageDraw is not None and ImageFilter is not None and ImageFont is not None


def render_font_cell(
    source_path: Path,
    output_path: Path,
    cell_index: int,
    char: str,
    font_path: Path,
    font_index: int = 0,
    font_size: int = 14,
    ink_index: int = 15,
    x_offset: int = 0,
    y_offset: int = 0,
    threshold: int = 0,
    gray_threshold: int = 176,
    render_mode: str = "grayscale",
    stroke_radius: int = 0,
    preview_path: Path | None = None,
) -> None:
    if len(char) != 1:
        raise ValueError("char must be exactly one Unicode character")
    if ink_index < 1 or ink_index > 15:
        raise ValueError("ink index must be in range 1..15")
    if threshold < 0 or threshold > 255:
        raise ValueError("threshold must be in range 0..255")
    if gray_threshold < 0 or gray_threshold > 255:
        raise ValueError("gray threshold must be in range 0..255")
    if render_mode not in {"grayscale", "binary", "palette3"}:
        raise ValueError("render mode must be 'grayscale', 'binary', or 'palette3'")
    if stroke_radius < 0 or stroke_radius > 3:
        raise ValueError("stroke radius must be in range 0..3")

    cell_w, cell_h = parse_cell_size(source_path.stem)
    image_w, image_h, original = decode_mig_indices(source_path)
    cols = image_w // cell_w
    capacity = cols * (image_h // cell_h)
    if cell_index < 0 or cell_index >= capacity:
        raise ValueError(f"cell index {cell_index} is outside page capacity {capacity}")

    mask = render_glyph_mask(char, font_path, font_index, font_size, cell_w, cell_h, x_offset, y_offset, stroke_radius)
    glyph_indices = mask_to_indices(mask, ink_index, threshold, render_mode, gray_threshold)

    indices = bytearray(original)
    x0 = (cell_index % cols) * cell_w
    y0 = (cell_index // cols) * cell_h
    for y in range(cell_h):
        source_start = y * cell_w
        target_start = (y0 + y) * image_w + x0
        indices[target_start : target_start + cell_w] = glyph_indices[source_start : source_start + cell_w]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    replace_mig_indices(source_path, bytes(indices), output_path)

    if preview_path is not None:
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        write_png_rgba(preview_path, cell_w, cell_h, indices_to_preview_rgba(glyph_indices))


def render_font_cell_bitplane(
    source_path: Path,
    output_path: Path,
    cell_index: int,
    char: str,
    font_path: Path,
    layer: str,
    font_index: int = 0,
    font_size: int = 14,
    x_offset: int = 0,
    y_offset: int = 0,
    threshold: int = 0,
    gray_threshold: int = 176,
    render_mode: str = "palette3",
    stroke_radius: int = 0,
    preview_path: Path | None = None,
) -> None:
    if len(char) != 1:
        raise ValueError("char must be exactly one Unicode character")
    if layer not in {"low", "high"}:
        raise ValueError("layer must be 'low' or 'high'")
    if threshold < 0 or threshold > 255:
        raise ValueError("threshold must be in range 0..255")
    if gray_threshold < 0 or gray_threshold > 255:
        raise ValueError("gray threshold must be in range 0..255")
    if render_mode not in {"binary", "palette3"}:
        raise ValueError("render mode must be 'binary' or 'palette3'")
    if stroke_radius < 0 or stroke_radius > 3:
        raise ValueError("stroke radius must be in range 0..3")

    cell_w, cell_h = parse_cell_size(source_path.stem)
    image_w, image_h, original = decode_mig_indices(source_path)
    cols = image_w // cell_w
    capacity = cols * (image_h // cell_h)
    if cell_index < 0 or cell_index >= capacity:
        raise ValueError(f"cell index {cell_index} is outside page capacity {capacity}")

    mask = render_glyph_mask(char, font_path, font_index, font_size, cell_w, cell_h, x_offset, y_offset, stroke_radius)
    glyph_indices = mask_to_two_bit_indices(mask, threshold, render_mode, gray_threshold)

    indices = bytearray(original)
    x0 = (cell_index % cols) * cell_w
    y0 = (cell_index // cols) * cell_h
    for y in range(cell_h):
        source_start = y * cell_w
        target_start = (y0 + y) * image_w + x0
        for x, value in enumerate(glyph_indices[source_start : source_start + cell_w]):
            target = target_start + x
            if layer == "low":
                indices[target] = (indices[target] & 0x0C) | value
            else:
                indices[target] = (indices[target] & 0x03) | (value << 2)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    replace_mig_indices(source_path, bytes(indices), output_path)

    if preview_path is not None:
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        write_png_rgba(preview_path, cell_w, cell_h, indices_to_preview_rgba(glyph_indices))


def render_glyph_mask(
    char: str,
    font_path: Path,
    font_index: int,
    font_size: int,
    cell_w: int,
    cell_h: int,
    x_offset: int,
    y_offset: int,
    stroke_radius: int = 0,
) -> bytes:
    require_pillow()
    font = ImageFont.truetype(str(font_path), font_size, index=font_index)
    canvas = Image.new("L", (cell_w, cell_h), 0)
    draw = ImageDraw.Draw(canvas)
    bbox = draw.textbbox((0, 0), char, font=font)
    glyph_w = bbox[2] - bbox[0]
    glyph_h = bbox[3] - bbox[1]
    x = (cell_w - glyph_w) // 2 - bbox[0] + x_offset
    y = (cell_h - glyph_h) // 2 - bbox[1] + y_offset
    draw.text((x, y), char, fill=255, font=font)
    if stroke_radius:
        canvas = canvas.filter(ImageFilter.MaxFilter(stroke_radius * 2 + 1))
    return canvas.tobytes()


def mask_to_indices(
    mask: bytes,
    ink_index: int,
    threshold: int,
    render_mode: str = "grayscale",
    gray_threshold: int = 176,
) -> bytes:
    if render_mode not in {"grayscale", "binary", "palette3"}:
        raise ValueError("render mode must be 'grayscale', 'binary', or 'palette3'")
    if gray_threshold < 0 or gray_threshold > 255:
        raise ValueError("gray threshold must be in range 0..255")

    indices = bytearray()
    for value in mask:
        if value <= threshold:
            indices.append(0)
        elif render_mode == "binary":
            indices.append(ink_index)
        elif render_mode == "palette3":
            indices.append(14 if value <= gray_threshold else 15)
        else:
            indices.append(max(1, round(value * ink_index / 255)))
    return bytes(indices)


def mask_to_two_bit_indices(
    mask: bytes,
    threshold: int,
    render_mode: str = "palette3",
    gray_threshold: int = 176,
) -> bytes:
    if render_mode not in {"binary", "palette3"}:
        raise ValueError("render mode must be 'binary' or 'palette3'")
    if threshold < 0 or threshold > 255:
        raise ValueError("threshold must be in range 0..255")
    if gray_threshold < 0 or gray_threshold > 255:
        raise ValueError("gray threshold must be in range 0..255")

    indices = bytearray()
    for value in mask:
        if value <= threshold:
            indices.append(0)
        elif render_mode == "binary":
            indices.append(3)
        else:
            indices.append(2 if value <= gray_threshold else 3)
    return bytes(indices)


def indices_to_preview_rgba(indices: bytes) -> bytes:
    rgba = bytearray()
    for index in indices:
        if index == 0:
            rgba.extend((0, 0, 0, 0))
        else:
            value = round(index * 255 / 15)
            rgba.extend((255, 255, 255, value))
    return bytes(rgba)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render one TrueType/OpenType glyph into a MIG font atlas cell.")
    parser.add_argument("source", type=Path, help="Source MIG font page.")
    parser.add_argument("output", type=Path, help="Output MIG font page.")
    parser.add_argument("--cell", type=int, required=True, help="Target cell index.")
    parser.add_argument("--char", required=True, help="Single Unicode character to render.")
    parser.add_argument("--font", type=Path, required=True, help="TrueType/OpenType font path.")
    parser.add_argument("--font-index", type=int, default=0, help="Face index for TTC/collection fonts.")
    parser.add_argument("--font-size", type=int, default=14)
    parser.add_argument("--ink-index", type=int, default=15)
    parser.add_argument("--x-offset", type=int, default=0)
    parser.add_argument("--y-offset", type=int, default=0)
    parser.add_argument("--threshold", type=int, default=0)
    parser.add_argument(
        "--gray-threshold",
        type=int,
        default=176,
        help="For palette3 mode, mask values up to this value become the original gray palette index.",
    )
    parser.add_argument(
        "--render-mode",
        choices=("grayscale", "binary", "palette3"),
        default="grayscale",
        help="Use grayscale antialiasing, crisp binary ink, or original-palette gray/white quantization.",
    )
    parser.add_argument(
        "--stroke-radius",
        type=int,
        default=0,
        help="Optional MaxFilter dilation radius before thresholding. 0 preserves the original glyph weight.",
    )
    parser.add_argument("--preview", type=Path, help="Optional PNG preview of the rendered cell.")
    args = parser.parse_args()

    render_font_cell(
        args.source,
        args.output,
        cell_index=args.cell,
        char=args.char,
        font_path=args.font,
        font_index=args.font_index,
        font_size=args.font_size,
        ink_index=args.ink_index,
        x_offset=args.x_offset,
        y_offset=args.y_offset,
        threshold=args.threshold,
        gray_threshold=args.gray_threshold,
        render_mode=args.render_mode,
        stroke_radius=args.stroke_radius,
        preview_path=args.preview,
    )
    print(f"rendered {args.char} into {args.output} cell {args.cell}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
