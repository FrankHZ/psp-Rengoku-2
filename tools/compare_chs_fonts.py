from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import sys

from render_mig_font_cell import (
    has_pillow,
    indices_to_preview_rgba,
    mask_to_indices,
    render_glyph_mask,
)

if has_pillow():
    from PIL import Image, ImageDraw, ImageFont
else:  # pragma: no cover - exercised when dependency is missing.
    Image = ImageDraw = ImageFont = None


TITLE_SAMPLE = "移动方式"
DENSE_SAMPLE = "方向键上下左右按住R可保持朝向平移。"


@dataclass(frozen=True)
class FontCandidate:
    label: str
    path: Path
    index: int = 0


DEFAULT_CANDIDATES = (
    FontCandidate("SimSun", Path("C:/Windows/Fonts/simsun.ttc"), 0),
    FontCandidate("NSimSun", Path("C:/Windows/Fonts/simsun.ttc"), 1),
    FontCandidate("SimSun-ExtB", Path("C:/Windows/Fonts/simsunb.ttf"), 0),
    FontCandidate("SimHei", Path("C:/Windows/Fonts/simhei.ttf"), 0),
    FontCandidate("KaiTi", Path("C:/Windows/Fonts/simkai.ttf"), 0),
    FontCandidate("FangSong", Path("C:/Windows/Fonts/simfang.ttf"), 0),
    FontCandidate("Microsoft-YaHei", Path("C:/Windows/Fonts/msyh.ttc"), 0),
    FontCandidate("Microsoft-YaHei-Bold", Path("C:/Windows/Fonts/msyhbd.ttc"), 0),
    FontCandidate("Noto-Sans-SC", Path("C:/Windows/Fonts/NotoSansSC-VF.ttf"), 0),
    FontCandidate("MS-Gothic", Path("C:/Windows/Fonts/msgothic.ttc"), 0),
    FontCandidate("MS-Mincho", Path("C:/Windows/Fonts/msmincho.ttc"), 0),
    FontCandidate("Meiryo", Path("C:/Windows/Fonts/meiryo.ttc"), 0),
    FontCandidate("BIZ-UD-Gothic", Path("C:/Windows/Fonts/BIZ-UDGothicR.ttc"), 0),
    FontCandidate("Yu-Mincho", Path("C:/Windows/Fonts/yumin.ttf"), 0),
)


def available_candidates() -> list[FontCandidate]:
    return [candidate for candidate in DEFAULT_CANDIDATES if candidate.path.exists()]


def render_text_strip(
    text: str,
    font_path: Path,
    font_index: int,
    font_size: int,
    render_mode: str,
    threshold: int,
    gray_threshold: int,
    stroke_radius: int,
    scale: int,
) -> Image.Image:
    cell_w = 14
    cell_h = 14
    strip = Image.new("RGBA", (cell_w * len(text), cell_h), (0, 0, 0, 0))
    for index, char in enumerate(text):
        if char == " ":
            continue
        mask = render_glyph_mask(char, font_path, font_index, font_size, cell_w, cell_h, 0, 0, stroke_radius)
        indices = mask_to_indices(mask, 15, threshold, render_mode, gray_threshold)
        cell = Image.frombytes("RGBA", (cell_w, cell_h), indices_to_preview_rgba(indices))
        strip.paste(cell, (index * cell_w, 0))
    return strip.resize((strip.width * scale, strip.height * scale), Image.Resampling.NEAREST)


def make_contact_sheet(
    candidates: list[FontCandidate],
    output_dir: Path,
    font_size: int,
    render_mode: str,
    threshold: int,
    gray_threshold: int,
    stroke_radius: int,
    scale: int,
) -> list[dict[str, str]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    label_font = ImageFont.load_default()
    rows = []
    rendered_rows = []

    for candidate in candidates:
        try:
            title = render_text_strip(
                TITLE_SAMPLE,
                candidate.path,
                candidate.index,
                font_size,
                render_mode,
                threshold,
                gray_threshold,
                stroke_radius,
                scale,
            )
            dense = render_text_strip(
                DENSE_SAMPLE,
                candidate.path,
                candidate.index,
                font_size,
                render_mode,
                threshold,
                gray_threshold,
                stroke_radius,
                scale,
            )
            font = ImageFont.truetype(str(candidate.path), font_size, index=candidate.index)
            family, style = font.getname()
            face_name = f"{family} {style}".strip()
        except Exception as error:  # pragma: no cover - protects batch comparison.
            rows.append(
                {
                    "label": candidate.label,
                    "font": str(candidate.path),
                    "font_index": str(candidate.index),
                    "face_name": "",
                    "title_preview": "",
                    "dense_preview": "",
                    "notes": f"render failed: {error}",
                }
            )
            continue

        title_path = output_dir / f"{safe_name(candidate.label)}_title.png"
        dense_path = output_dir / f"{safe_name(candidate.label)}_dense.png"
        title.save(title_path)
        dense.save(dense_path)

        row = {
            "label": candidate.label,
            "font": str(candidate.path),
            "font_index": str(candidate.index),
            "face_name": face_name,
            "title_preview": str(title_path),
            "dense_preview": str(dense_path),
            "notes": "",
        }
        rows.append(row)
        rendered_rows.append((row, title, dense))

    if rendered_rows:
        label_w = 180
        gap = 16
        row_h = max(title.height + dense.height + 14, 84)
        width = label_w + gap + max(title.width + gap + dense.width for _, title, dense in rendered_rows)
        sheet = Image.new("RGBA", (width, row_h * len(rendered_rows)), (24, 24, 24, 255))
        draw = ImageDraw.Draw(sheet)
        for row_index, (row, title, dense) in enumerate(rendered_rows):
            y = row_index * row_h
            draw.text((8, y + 8), row["label"], fill=(255, 255, 255, 255), font=label_font)
            draw.text((8, y + 24), row["face_name"], fill=(180, 180, 180, 255), font=label_font)
            x = label_w + gap
            sheet.alpha_composite(title, (x, y + 8))
            sheet.alpha_composite(dense, (x + title.width + gap, y + 8))
        sheet.save(output_dir / "contact_sheet.png")

    return rows


def write_report(output_dir: Path, rows: list[dict[str, str]], settings: dict[str, str]) -> None:
    csv_path = output_dir / "font_compare.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["label", "font", "font_index", "face_name", "title_preview", "dense_preview", "notes"],
        )
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# CHS 14x14 Font Comparison",
        "",
        "Generated local preview report. Local Windows font files are referenced for evaluation only.",
        "",
        "## Settings",
        "",
    ]
    for key, value in settings.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Recommendation", ""])
    lines.extend(
        [
            "- Start visual QA with `SimSun` / `C:/Windows/Fonts/simsun.ttc` / `font_index=0` at 13px, `palette3`, threshold 64, gray threshold 176.",
            "- If the title looks too thin in PPSSPP, try the same SimSun face with `--stroke-radius 1` before switching fonts.",
            "- Keep `NotoSansSC-VF.ttf` as the clean sans fallback; it is readable, but less PSP-era and less close to the original UI texture.",
        ]
    )
    lines.extend(["", "## Candidates", ""])
    lines.append("| Label | Face | Font index | Preview | Notes |")
    lines.append("| --- | --- | ---: | --- | --- |")
    for row in rows:
        preview = Path(row["title_preview"]).name if row["title_preview"] else ""
        preview_link = f"[title]({preview})" if preview else ""
        lines.append(
            f"| {row['label']} | {row['face_name']} | {row['font_index']} | {preview_link} | {row['notes']} |"
        )
    lines.append("")
    lines.append("Open `contact_sheet.png` in this folder for the side-by-side title and dense-string comparison.")
    (output_dir / "font_compare_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def safe_name(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "_" for char in value).strip("_")


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare local CJK fonts as 14x14 CHS glyph previews.")
    parser.add_argument("--output-dir", type=Path, default=Path("local/work/font_compare"))
    parser.add_argument("--font-size", type=int, default=13)
    parser.add_argument("--render-mode", choices=("grayscale", "binary", "palette3"), default="palette3")
    parser.add_argument("--threshold", type=int, default=64)
    parser.add_argument("--gray-threshold", type=int, default=176)
    parser.add_argument("--stroke-radius", type=int, default=0)
    parser.add_argument("--scale", type=int, default=4)
    args = parser.parse_args()

    if not has_pillow():
        raise SystemExit("compare_chs_fonts.py requires Pillow. Install with: pip install Pillow")

    candidates = available_candidates()
    rows = make_contact_sheet(
        candidates,
        args.output_dir,
        args.font_size,
        args.render_mode,
        args.threshold,
        args.gray_threshold,
        args.stroke_radius,
        args.scale,
    )
    settings = {
        "title_sample": TITLE_SAMPLE,
        "dense_sample": DENSE_SAMPLE,
        "font_size": str(args.font_size),
        "render_mode": args.render_mode,
        "threshold": str(args.threshold),
        "gray_threshold": str(args.gray_threshold),
        "stroke_radius": str(args.stroke_radius),
        "scale": str(args.scale),
    }
    write_report(args.output_dir, rows, settings)
    print(f"wrote {args.output_dir / 'font_compare_report.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
