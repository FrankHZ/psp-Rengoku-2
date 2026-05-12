from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from build_chs_tutorial import BITPLANE_SLOT_POOLS
from mig import decode_mig_indices


DEFAULT_OUTPUT = Path("local/work/jp_glyph_table_v1")
DEFAULT_SEEDS = (
    Path("samples/runtime_glyph_map_seed.csv"),
    Path("samples/runtime_kana_map.csv"),
)
FONT_CANDIDATES = (
    Path("C:/Windows/Fonts/msgothic.ttc"),
    Path("C:/Windows/Fonts/meiryo.ttc"),
    Path("C:/Windows/Fonts/YuGothM.ttc"),
    Path("C:/Windows/Fonts/YuGothR.ttc"),
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export the confirmed JP low/high logical font cells and make a first-pass OCR map."
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--seed", type=Path, action="append", default=list(DEFAULT_SEEDS))
    parser.add_argument("--font", type=Path, help="Optional TrueType/OpenType font for template OCR.")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    output_dir = args.output_dir
    if output_dir.exists() and not args.overwrite:
        raise FileExistsError(f"{output_dir} already exists; pass --overwrite to replace generated files")
    output_dir.mkdir(parents=True, exist_ok=True)

    seed_map = load_seed_map(args.seed)
    font_path = args.font or first_existing_font()
    candidates = build_candidate_chars(seed_map)
    templates = build_templates(candidates, font_path) if font_path else {}
    rows = build_rows(seed_map, templates)

    write_csv(output_dir / "jp_glyph_map.csv", rows)
    write_json(output_dir / "jp_glyph_map.json", rows)
    write_contact_sheets(output_dir / "contact_sheets", rows)
    write_readme(output_dir / "README.md", rows, font_path)
    print(f"wrote {output_dir}")
    return 0


def load_seed_map(paths: list[Path]) -> dict[int, dict[str, str]]:
    seeds: dict[int, dict[str, str]] = {}
    for path in paths:
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            for row in csv.DictReader(file):
                raw_code = str(row.get("code") or "").strip()
                char = str(row.get("char") or "")
                if not raw_code or not char:
                    continue
                code = int(raw_code, 16)
                existing = seeds.get(code)
                verification = str(row.get("verification") or row.get("confidence") or "seed")
                source = path.as_posix()
                notes = str(row.get("notes") or "")
                if existing and existing.get("char") != char:
                    existing["notes"] = (existing.get("notes", "") + f"; conflict {source}={char}").strip("; ")
                    existing["verification"] = "conflict"
                    continue
                seeds[code] = {
                    "char": char,
                    "verification": verification,
                    "source": source,
                    "notes": notes,
                }
    add_builtin_sequence_labels(seeds)
    return seeds


def add_builtin_sequence_labels(seeds: dict[int, dict[str, str]]) -> None:
    for index in range(94):
        char = decode_jis0208(1, index + 1)
        if char:
            add_inferred_seed(seeds, 0x0100 + index, char, "JIS X 0208 row 1 punctuation/symbol sequence")

    for index, char in enumerate("0123456789"):
        add_inferred_seed(seeds, 0x0193 + index, char, "visible contiguous digit sequence")
    for index, char in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        add_inferred_seed(seeds, 0x019D + index, char, "visible contiguous uppercase Latin sequence")
    for index, char in enumerate("abcdefghijklmnopqrstuvwxyz"):
        add_inferred_seed(seeds, 0x01B7 + index, char, "visible contiguous lowercase Latin sequence")


def add_inferred_seed(seeds: dict[int, dict[str, str]], code: int, char: str, notes: str) -> None:
    existing = seeds.get(code)
    if existing:
        if existing.get("char") == char:
            return
        existing["notes"] = (existing.get("notes", "") + f"; inferred conflict {char}: {notes}").strip("; ")
        existing["verification"] = "conflict"
        return
    seeds[code] = {
        "char": char,
        "verification": "inferred_sequence",
        "source": "builtin_sequence",
        "notes": notes,
    }


def first_existing_font() -> Path | None:
    return next((path for path in FONT_CANDIDATES if path.exists()), None)


def build_candidate_chars(seed_map: dict[int, dict[str, str]]) -> list[str]:
    chars = set("".join(chr(value) for value in range(0x21, 0x7F)))
    chars.update(" 　、。，．・：；？！゛゜´｀¨＾￣＿ヽヾゝゞ〃仝々〆〇ー―‐／＼～∥｜…‥‘’“”（）〔〕［］｛｝〈〉《》「」『』【】＋－±×÷＝≠＜＞≦≧∞∴♂♀°′″℃￥＄￠￡％＃＆＊＠§☆★○●◎◇◆□■△▲▽▼※〒→←↑↓")
    chars.update("ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをん")
    chars.update("ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶ")
    chars.update("ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρστυφχψω")
    chars.update("АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")
    for ku in range(1, 85):
        for ten in range(1, 95):
            char = decode_jis0208(ku, ten)
            if char:
                chars.add(char)
    chars.update(seed["char"] for seed in seed_map.values() if seed.get("char"))
    return sorted(chars)


def decode_jis0208(ku: int, ten: int) -> str | None:
    raw = bytes([0x1B, 0x24, 0x42, ku + 0x20, ten + 0x20, 0x1B, 0x28, 0x42])
    try:
        return raw.decode("iso2022_jp")
    except UnicodeDecodeError:
        return None


def build_templates(chars: list[str], font_path: Path) -> dict[str, tuple[int, int]]:
    templates: dict[str, tuple[int, int]] = {}
    for char in chars:
        best_mask = 0
        best_area = 0
        for size in (11, 12, 13, 14, 15, 16):
            try:
                font = ImageFont.truetype(str(font_path), size=size)
            except OSError:
                return {}
            mask, area = render_char_mask(char, font)
            if area > best_area:
                best_mask = mask
                best_area = area
        if best_area:
            templates[char] = (best_mask, best_area)
    return templates


def render_char_mask(char: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    scratch = Image.new("L", (32, 32), 0)
    draw = ImageDraw.Draw(scratch)
    bbox = draw.textbbox((0, 0), char, font=font)
    width = max(1, bbox[2] - bbox[0])
    height = max(1, bbox[3] - bbox[1])
    x = (14 - width) // 2 - bbox[0]
    y = (14 - height) // 2 - bbox[1]
    image = Image.new("L", (14, 14), 0)
    draw = ImageDraw.Draw(image)
    draw.text((x, y), char, font=font, fill=255)
    return pack_mask(image), count_ink(image)


def build_rows(seed_map: dict[int, dict[str, str]], templates: dict[str, tuple[int, int]]) -> list[dict[str, Any]]:
    rows = []
    for pool in BITPLANE_SLOT_POOLS:
        page = Path(pool["target_page"])
        width, _height, indices = decode_mig_indices(page)
        child = int(pool["child"])
        base = int(pool["base"])
        layer = str(pool["layer"])
        for cell in range(81):
            cell_row = cell // 9
            cell_col = cell % 9
            mask, ink_pixels = cell_layer_mask(indices, width, cell, layer)
            code = base + cell
            seed = seed_map.get(code)
            ocr = ocr_guess(mask, ink_pixels, templates)
            char = seed["char"] if seed else ""
            status = "empty_cell" if ink_pixels == 0 else "ocr_candidate"
            if seed:
                status = "inferred_sequence" if seed.get("source") == "builtin_sequence" else "seeded"
            rows.append(
                {
                    "code": f"0x{code:04x}",
                    "char": char,
                    "status": status,
                    "seed_source": seed.get("source", "") if seed else "",
                    "seed_confidence": seed.get("verification", "") if seed else "",
                    "ocr_guess": ocr["char"],
                    "ocr_score": f"{ocr['score']:.4f}" if ocr["char"] else "",
                    "ocr_confidence": ocr["confidence"],
                    "child": child,
                    "source": pool["source"],
                    "base": f"0x{base:04x}",
                    "layer": layer,
                    "cell": cell,
                    "row": cell_row,
                    "col": cell_col,
                    "runtime_texture": runtime_texture_for_child(child),
                    "ink_pixels": ink_pixels,
                    "mask_hex": f"0x{mask:050x}",
                    "notes": seed.get("notes", "") if seed else "",
                }
            )
    return rows


def cell_layer_mask(indices: bytes, texture_width: int, cell: int, layer: str) -> tuple[int, int]:
    cell_w = 14
    cell_h = 14
    col = cell % 9
    row = cell // 9
    mask = 0
    bit = 0
    ink_pixels = 0
    for y in range(row * cell_h, row * cell_h + cell_h):
        for x in range(col * cell_w, col * cell_w + cell_w):
            value = indices[y * texture_width + x]
            visible = (value & 0x03) != 0 if layer == "low" else (value & 0x0C) != 0
            if visible:
                mask |= 1 << bit
                ink_pixels += 1
            bit += 1
    return mask, ink_pixels


def ocr_guess(mask: int, ink_pixels: int, templates: dict[str, tuple[int, int]]) -> dict[str, Any]:
    if ink_pixels == 0 or not templates:
        return {"char": "", "score": 0.0, "confidence": ""}
    best_char = ""
    best_score = -1.0
    for char, (template_mask, template_area) in templates.items():
        intersection = (mask & template_mask).bit_count()
        union = (mask | template_mask).bit_count()
        if union == 0:
            continue
        score = intersection / union
        score -= abs(ink_pixels - template_area) / 500.0
        if score > best_score:
            best_char = char
            best_score = score
    if best_score >= 0.64:
        confidence = "medium"
    elif best_score >= 0.50:
        confidence = "low"
    else:
        confidence = "very_low"
    return {"char": best_char, "score": max(best_score, 0.0), "confidence": confidence}


def pack_mask(image: Image.Image) -> int:
    mask = 0
    bit = 0
    for value in image.convert("L").tobytes():
        if value >= 96:
            mask |= 1 << bit
        bit += 1
    return mask


def count_ink(image: Image.Image) -> int:
    return sum(1 for value in image.convert("L").tobytes() if value >= 96)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_contact_sheets(output_dir: Path, rows: list[dict[str, Any]]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    grouped: dict[tuple[int, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((int(row["child"]), str(row["layer"])), []).append(row)

    try:
        label_font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", size=11)
    except OSError:
        label_font = ImageFont.load_default()
    try:
        char_font = ImageFont.truetype("C:/Windows/Fonts/msgothic.ttc", size=18)
    except OSError:
        char_font = ImageFont.load_default()

    for (child, layer), page_rows in sorted(grouped.items()):
        tile_w = 82
        tile_h = 104
        sheet = Image.new("RGB", (9 * tile_w, 9 * tile_h), "white")
        draw = ImageDraw.Draw(sheet)
        for row in page_rows:
            cell = int(row["cell"])
            x = (cell % 9) * tile_w
            y = (cell // 9) * tile_h
            draw.rectangle((x, y, x + tile_w - 1, y + tile_h - 1), outline=(180, 180, 180))
            draw.text((x + 3, y + 2), str(row["code"]), fill=(0, 0, 0), font=label_font)
            glyph = mask_to_image(int(str(row["mask_hex"]), 16), scale=3)
            sheet.paste(glyph, (x + 20, y + 18))
            label = str(row["char"] or row["ocr_guess"] or "")
            confidence = str(row["status"] if row["char"] else row["ocr_confidence"])
            draw.text((x + 3, y + 62), label, fill=(0, 80, 0) if row["char"] else (160, 80, 0), font=char_font)
            draw.text((x + 3, y + 84), confidence[:11], fill=(80, 80, 80), font=label_font)
            draw.text((x + 3, y + 96), f"ink {row['ink_pixels']}", fill=(80, 80, 80), font=label_font)
        sheet.save(output_dir / f"child{child:02d}_{layer}_map.png")


def mask_to_image(mask: int, scale: int) -> Image.Image:
    image = Image.new("RGB", (14, 14), "white")
    pixels = image.load()
    bit = 0
    for y in range(14):
        for x in range(14):
            if mask & (1 << bit):
                pixels[x, y] = (0, 0, 0)
            bit += 1
    return image.resize((14 * scale, 14 * scale), Image.Resampling.NEAREST)


def write_readme(path: Path, rows: list[dict[str, Any]], font_path: Path | None) -> None:
    seeded = sum(1 for row in rows if row["status"] == "seeded")
    inferred_sequence = sum(1 for row in rows if row["status"] == "inferred_sequence")
    empty = sum(1 for row in rows if row["status"] == "empty_cell")
    medium = sum(1 for row in rows if row["ocr_confidence"] == "medium")
    low = sum(1 for row in rows if row["ocr_confidence"] == "low")
    very_low = sum(1 for row in rows if row["ocr_confidence"] == "very_low")
    lines = [
        "# JP Glyph Table v1",
        "",
        "This is a first-pass full logical-cell map for the confirmed JP low/high",
        "bitplane font windows. It is not yet a trusted translation map.",
        "",
        "## Inputs",
        "",
        "- Confirmed low/high base windows from `tools/build_chs_tutorial.py`.",
        "- Seed labels from `samples/runtime_glyph_map_seed.csv` and `samples/runtime_kana_map.csv`.",
        f"- Template OCR font: `{font_path.as_posix() if font_path else 'none found'}`",
        "",
        "## Summary",
        "",
        f"- Logical cells exported: {len(rows)}",
        f"- Seeded labels: {seeded}",
        f"- Inferred sequence labels: {inferred_sequence}",
        f"- Empty cells by layer mask: {empty}",
        f"- OCR medium confidence: {medium}",
        f"- OCR low confidence: {low}",
        f"- OCR very low confidence: {very_low}",
        "",
        "## Files",
        "",
        "- `jp_glyph_map.csv`: main machine-readable table.",
        "- `jp_glyph_map.json`: JSON mirror of the same rows.",
        "- `contact_sheets/`: one labeled PNG per child/layer.",
        "",
        "Use `char` directly when `status=seeded`; `status=inferred_sequence` is",
        "low-risk but still distinct from a PPSSPP-confirmed seed. Treat",
        "`ocr_guess` as a review queue unless a later pass promotes it with visual",
        "confirmation.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def runtime_texture_for_child(child: int) -> str:
    return f"0x{0x040DC200 + child * 0x2100:08x}"


if __name__ == "__main__":
    raise SystemExit(main())
