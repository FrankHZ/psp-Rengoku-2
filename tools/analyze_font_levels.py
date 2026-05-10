from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
import sys

from analyze_font_grid import parse_cell_size
from mig import decode_mig_indices, decode_palette_color, read_mig


def analyze_page(path: Path) -> dict[str, object]:
    cell_w, cell_h = parse_cell_size(path.stem)
    image_w, image_h, indices = decode_mig_indices(path)
    cols = image_w // cell_w
    capacity = cols * (image_h // cell_h)
    cell_level_hist: Counter[int] = Counter()
    pixel_hist: Counter[int] = Counter()
    level_sets: Counter[tuple[int, ...]] = Counter()
    occupied = 0

    for cell in range(capacity):
        x0 = (cell % cols) * cell_w
        y0 = (cell // cols) * cell_h
        hist: Counter[int] = Counter()
        for y in range(cell_h):
            hist.update(indices[(y0 + y) * image_w + x0 : (y0 + y) * image_w + x0 + cell_w])
        nonzero = {level: count for level, count in hist.items() if level}
        if not nonzero:
            continue
        occupied += 1
        cell_level_hist.update(nonzero.keys())
        pixel_hist.update(nonzero)
        level_sets.update([tuple(sorted(nonzero.keys()))])

    return {
        "page": path.name,
        "occupied_cells": occupied,
        "cell_level_hist": cell_level_hist,
        "pixel_hist": pixel_hist,
        "level_sets": level_sets,
        "palette": read_palette(path),
    }


def read_palette(path: Path) -> list[tuple[int, int, int, int]]:
    mig = read_mig(path)
    if mig.palette_offset is None:
        return []
    data = path.read_bytes()
    palette = data[mig.palette_offset : mig.palette_offset + 16 * 4]
    return [decode_palette_color(palette[index * 4 : index * 4 + 4], "rgba") for index in range(16)]


def write_reports(root: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = [analyze_page(path) for path in sorted(root.glob("*.bin"))]

    with (output_dir / "font_level_summary.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["page", "occupied_cells", "levels_used_by_cells", "pixel_hist", "palette_rgb_classes"],
        )
        writer.writeheader()
        for page in pages:
            palette = page["palette"]
            writer.writerow(
                {
                    "page": page["page"],
                    "occupied_cells": page["occupied_cells"],
                    "levels_used_by_cells": format_counter(page["cell_level_hist"]),
                    "pixel_hist": format_counter(page["pixel_hist"]),
                    "palette_rgb_classes": format_palette_classes(palette),
                }
            )

    global_cells: Counter[int] = Counter()
    global_pixels: Counter[int] = Counter()
    global_sets: Counter[tuple[int, ...]] = Counter()
    for page in pages:
        global_cells.update(page["cell_level_hist"])
        global_pixels.update(page["pixel_hist"])
        global_sets.update(page["level_sets"])

    lines = [
        "# Font Level Analysis",
        "",
        f"Source: `{root}`",
        "",
        "The font textures are 4bpp, but the CLUT does not expose sixteen distinct visible shades.",
        "For the sampled `codeJAP14x14`/`codeANK9x14` pages, palette entries repeat as black, black, gray, white.",
        "",
        "## Global Index Usage",
        "",
        f"- Occupied cells: `{sum(int(page['occupied_cells']) for page in pages)}`",
        f"- Nonzero levels seen by cell: `{format_counter(global_cells)}`",
        f"- Nonzero pixel histogram: `{format_counter(global_pixels)}`",
        f"- Most common level sets: `{global_sets.most_common(8)}`",
        "",
        "## Recommendation",
        "",
        "- Keep the atlas writer 4bpp, because original glyph cells do use indices across `1..15`.",
        "- Render CHS glyphs with `render_mode=palette3`, `threshold=64`, `gray_threshold=176`, `ink_index=15` as the current default.",
        "- Use `binary` only for maximum crispness tests; it is less faithful because it writes only white ink.",
        "",
        "Per-page CSV: `font_level_summary.csv`",
        "",
    ]
    (output_dir / "font_level_report.md").write_text("\n".join(lines), encoding="utf-8")


def format_counter(counter: Counter[int]) -> str:
    return " ".join(f"{key}:{counter[key]}" for key in sorted(counter))


def format_palette_classes(palette: list[tuple[int, int, int, int]]) -> str:
    return " ".join(f"{index}:{color[0]},{color[1]},{color[2]},{color[3]}" for index, color in enumerate(palette))


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze original MIG font index/palette usage.")
    parser.add_argument("root", type=Path, nargs="?", default=Path("local/work/tdl_DATA001_0002"))
    parser.add_argument("--output-dir", type=Path, default=Path("local/work/font_level_analysis"))
    args = parser.parse_args()

    write_reports(args.root, args.output_dir)
    print(f"wrote {args.output_dir / 'font_level_report.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
