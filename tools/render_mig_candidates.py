from __future__ import annotations

import argparse
import csv
from pathlib import Path

from PIL import Image, ImageDraw

from mig import decode_palette_color, unswizzle_texture_bytes, write_png_rgba
from tdl import read_tdl


MIG_MAGIC = b"MIG.00.1PSP"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render same-size MIG candidates as forced 128x128 CLUT4 pages.")
    parser.add_argument("--entries-root", type=Path, default=Path("local/work/mcd3_entries"))
    parser.add_argument("--output-dir", type=Path, default=Path("local/work/rendered_mig_candidates_v1"))
    parser.add_argument("--size", type=lambda value: int(value, 0), default=0x2110)
    parser.add_argument("--debug-contrast", action="store_true")
    args = parser.parse_args()

    rows = collect_same_size_mig_candidates(args.entries_root, args.size)
    render_candidates(rows, args.output_dir, args.debug_contrast)
    print(f"wrote {args.output_dir}")
    return 0


def collect_same_size_mig_candidates(entries_root: Path, size: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for path in sorted(entries_root.rglob("*_mig.bin")):
        data = path.read_bytes()
        if len(data) == size and data.startswith(MIG_MAGIC):
            rows.append(
                {
                    "source": str(path.relative_to(entries_root)),
                    "child": "",
                    "name": path.stem,
                    "size": size,
                    "data": data,
                }
            )

    for path in sorted(entries_root.rglob("*_tdl.bin")):
        data = path.read_bytes()
        try:
            tdl = read_tdl(path)
        except Exception:
            continue
        for entry in tdl.entries:
            child = data[entry.offset : entry.end_offset]
            if entry.size == size and child.startswith(MIG_MAGIC):
                rows.append(
                    {
                        "source": str(path.relative_to(entries_root)),
                        "child": str(entry.index),
                        "name": entry.name,
                        "size": entry.size,
                        "data": child,
                    }
                )
    return rows


def render_candidates(rows: list[dict[str, object]], output_dir: Path, debug_contrast: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered = []
    manifest_rows = []
    for index, row in enumerate(rows):
        data = bytes(row["data"])
        width, height, rgba = render_forced_128_clut4(data, debug_contrast)
        safe_name = safe_filename(str(row["name"]))
        png_name = f"{index:04d}_{safe_name}.png"
        output_path = output_dir / png_name
        write_png_rgba(output_path, width, height, rgba)
        rendered.append((row, output_path))
        manifest_rows.append(
            {
                "index": str(index),
                "source": str(row["source"]),
                "child": str(row["child"]),
                "name": str(row["name"]),
                "size": f"0x{int(row['size']):x}",
                "png": png_name,
                "looks_like_code_font": str("code" in str(row["name"]).lower() or "font" in str(row["name"]).lower()),
            }
        )

    write_manifest(output_dir / "manifest.csv", manifest_rows)
    write_contact_sheet(rendered, output_dir / "contact_sheet.png")
    write_readme(output_dir / "README.md", manifest_rows, debug_contrast)


def render_forced_128_clut4(data: bytes, debug_contrast: bool = False) -> tuple[int, int, bytes]:
    width = 128
    height = 128
    palette = data[0x80 : 0x80 + 16 * 4]
    packed = data[0x110 : 0x110 + width * height // 2]
    if len(palette) != 64 or len(packed) != width * height // 2:
        raise ValueError("candidate does not contain enough data for forced 128x128 CLUT4 rendering")

    unswizzled = unswizzle_texture_bytes(packed, width_bytes=width // 2, height=height)
    rgba = bytearray()
    for byte in unswizzled:
        for index in (byte & 0x0F, byte >> 4):
            base = index * 4
            red, green, blue, alpha = decode_palette_color(palette[base : base + 4], "rgba")
            if debug_contrast:
                red, green, blue, alpha = debug_contrast_color(index, alpha)
            rgba.extend((red, green, blue, alpha))
    return width, height, bytes(rgba)


def debug_contrast_color(index: int, alpha: int) -> tuple[int, int, int, int]:
    if index == 0:
        return 0, 0, 0, 0
    value = min(255, 32 + index * 14)
    return value, value, value, 255 if alpha else 180


def write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_contact_sheet(rendered: list[tuple[dict[str, object], Path]], output_path: Path) -> None:
    if not rendered:
        return
    columns = 4
    tile_w = 128
    label_h = 34
    rows = (len(rendered) + columns - 1) // columns
    sheet = Image.new("RGBA", (columns * tile_w, rows * (128 + label_h)), (20, 20, 20, 255))
    draw = ImageDraw.Draw(sheet)
    for index, (row, path) in enumerate(rendered):
        image = Image.open(path).convert("RGBA")
        x = (index % columns) * tile_w
        y = (index // columns) * (128 + label_h)
        sheet.alpha_composite(image, (x, y))
        draw.text((x + 2, y + 130), f"{index:02d} {str(row['name'])[:16]}", fill=(255, 255, 255, 255))
    sheet.save(output_path)


def write_readme(path: Path, rows: list[dict[str, str]], debug_contrast: bool) -> None:
    code_like = [row for row in rows if row["looks_like_code_font"] == "True"]
    lines = [
        "# Rendered MIG Candidates",
        "",
        "Forced render of every canonical extracted MIG resource whose stored size matches the known font page size `0x2110`.",
        "",
        "This is a discovery view only. A non-code texture rendering as 128x128 does not prove it is routed as a font page.",
        "",
        "## Summary",
        "",
        f"- Rendered candidates: {len(rows)}",
        f"- Code/font-named candidates: {len(code_like)}",
        f"- Debug contrast: {debug_contrast}",
        "",
        "## Files",
        "",
        "- `manifest.csv`: source and child for each rendered candidate.",
        "- `contact_sheet.png`: visual overview.",
        "",
        "## Candidates",
        "",
        "| # | Name | Source | Child | Code/font name | PNG |",
        "| ---: | --- | --- | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['index']} | `{row['name']}` | `{row['source']}` | {row['child'] or ''} | "
            f"{row['looks_like_code_font']} | `{row['png']}` |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def safe_filename(value: str) -> str:
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in value)


if __name__ == "__main__":
    raise SystemExit(main())
