from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from stage_font_probe import stage_font_probe


DEFAULT_FONT = Path("C:/Windows/Fonts/simsun.ttc")

PAGE_SOURCES = {
    1: ("codeJAP14x14_00_", "local/work/tdl_DATA001_0002/0001_codeJAP14x14_00_.bin"),
    2: ("codeJAP14x14_02_", "local/work/tdl_DATA001_0002/0002_codeJAP14x14_02_.bin"),
    3: ("codeJAP14x14_04_", "local/work/tdl_DATA001_0002/0003_codeJAP14x14_04_.bin"),
    5: ("codeJAP14x14_08_", "local/work/tdl_DATA001_0002/0005_codeJAP14x14_08_.bin"),
    6: ("codeJAP14x14_10_", "local/work/tdl_DATA001_0002/0006_codeJAP14x14_10_.bin"),
    7: ("codeJAP14x14_12_", "local/work/tdl_DATA001_0002/0007_codeJAP14x14_12_.bin"),
}

PROBES = (
    {
        "id": "punc-0100",
        "label": "0100",
        "code": 0x0100,
        "candidates": (
            {"marker": "A", "child": 1, "cell": 0, "base": 0x0100, "formula": "page100"},
            {"marker": "B", "child": 2, "cell": 49, "base": 0x00CF, "formula": "contiguous"},
        ),
    },
    {
        "id": "punc-0101",
        "label": "0101",
        "code": 0x0101,
        "candidates": (
            {"marker": "C", "child": 1, "cell": 1, "base": 0x0100, "formula": "page100"},
            {"marker": "D", "child": 2, "cell": 50, "base": 0x00CF, "formula": "contiguous"},
        ),
    },
    {
        "id": "long-011b",
        "label": "011B",
        "code": 0x011B,
        "candidates": (
            {"marker": "E", "child": 1, "cell": 27, "base": 0x0100, "formula": "page100"},
            {"marker": "F", "child": 2, "cell": 76, "base": 0x00CF, "formula": "contiguous"},
        ),
    },
    {
        "id": "kana-01fe",
        "label": "01FE",
        "code": 0x01FE,
        "candidates": (
            {"marker": "G", "child": 5, "cell": 60, "base": 0x01C2, "formula": "contiguous"},
        ),
    },
    {
        "id": "kana-01fb",
        "label": "01FB",
        "code": 0x01FB,
        "candidates": (
            {"marker": "H", "child": 5, "cell": 57, "base": 0x01C2, "formula": "contiguous"},
        ),
    },
    {
        "id": "kana-01d4",
        "label": "01D4",
        "code": 0x01D4,
        "candidates": (
            {"marker": "I", "child": 5, "cell": 18, "base": 0x01C2, "formula": "contiguous"},
        ),
    },
    {
        "id": "ambig-021b",
        "label": "021B",
        "code": 0x021B,
        "candidates": (
            {"marker": "J", "child": 2, "cell": 40, "base": 0x01F3, "formula": "observed-overlay"},
            {"marker": "K", "child": 2, "cell": 27, "base": 0x0200, "formula": "page100"},
        ),
    },
    {
        "id": "ambig-0222",
        "label": "0222",
        "code": 0x0222,
        "candidates": (
            {"marker": "L", "child": 6, "cell": 15, "base": 0x0213, "formula": "contiguous"},
            {"marker": "M", "child": 2, "cell": 34, "base": 0x0200, "formula": "page100"},
        ),
    },
    {
        "id": "ambig-023c",
        "label": "023C",
        "code": 0x023C,
        "candidates": (
            {"marker": "N", "child": 3, "cell": 73, "base": 0x01F3, "formula": "observed-overlay"},
            {"marker": "O", "child": 2, "cell": 60, "base": 0x0200, "formula": "page100"},
        ),
    },
    {
        "id": "kana-0276",
        "label": "0276",
        "code": 0x0276,
        "candidates": (
            {"marker": "P", "child": 7, "cell": 18, "base": 0x0264, "formula": "contiguous"},
        ),
    },
    {
        "id": "kana-026e",
        "label": "026E",
        "code": 0x026E,
        "candidates": (
            {"marker": "Q", "child": 7, "cell": 10, "base": 0x0264, "formula": "contiguous"},
        ),
    },
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build one PPSSPP artifact that probes multiple candidate glyph page bases.")
    parser.add_argument("--work-root", type=Path, default=Path("local/work/page_base_probe_v1"))
    parser.add_argument("--output-root", type=Path, default=Path("local/rebuilt/page_base_probe_v1_extracted"))
    parser.add_argument("--font", type=Path, default=DEFAULT_FONT)
    parser.add_argument("--font-index", type=int, default=0)
    parser.add_argument("--font-size", type=int, default=12)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    build_page_base_probe(
        work_root=args.work_root,
        output_root=args.output_root,
        font_path=args.font,
        font_index=args.font_index,
        font_size=args.font_size,
        overwrite=args.overwrite,
    )
    print(f"staged {args.output_root}")
    return 0


def build_page_base_probe(
    work_root: Path,
    output_root: Path,
    font_path: Path = DEFAULT_FONT,
    font_index: int = 0,
    font_size: int = 12,
    overwrite: bool = False,
) -> None:
    work_root.mkdir(parents=True, exist_ok=True)
    text_payload = build_text_payload()
    text_json = work_root / "DATA001_0008_page_base_probe.json"
    text_json.write_text(json.dumps(text_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    write_probe_manifest(work_root / "probe_manifest.csv")
    write_readme(work_root / "README.md", output_root)

    stage_config = {
        "extracted_root": "local/extracted/Rengoku 2",
        "entries_root": "local/work/mcd3_entries",
        "work_root": str(work_root / "stage"),
        "output_root": str(output_root),
        "font_patches": build_font_patches(work_root / "previews", font_path, font_index, font_size),
        "text_patch": {
            "entry_id": 8,
            "source_entry": "local/work/mcd3_entries/DATA001/0008_bin.bin",
            "json": str(text_json),
        },
        "overwrite": overwrite,
    }
    (work_root / "stage_page_base_probe.json").write_text(
        json.dumps(stage_config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    stage_font_probe(stage_config)


def build_text_payload() -> dict[str, Any]:
    rows = [
        (10, "BASE PROBE"),
        (11, "LOOK AT BODY ROWS"),
        (67, "B0", PROBES[0:3]),
        (69, "B1", PROBES[3:6]),
        (71, "B2", PROBES[6:]),
    ]
    entries = []
    for index, row in enumerate(rows):
        record = int(row[0])
        if len(row) == 2:
            codes = encode_ascii(str(row[1]))
        else:
            codes = encode_probe_line(str(row[1]), row[2])
        entries.append(
            {
                "id": f"page-base-probe-{index:02d}",
                "record": record,
                "run": 0,
                "kind": "glyph_codes",
                "length": max(len(codes), 1),
                "translation": "",
                "translation_codes": [f"0x{code:04x}" for code in codes],
                "notes": "generated by tools/build_page_base_probe.py",
            }
        )
    return {
        "format": "offset-table-runs-v1",
        "source": "local/work/mcd3_entries/DATA001/0008_bin.bin",
        "entries": entries,
    }


def encode_probe_line(prefix: str, probes: tuple[dict[str, Any], ...]) -> list[int]:
    codes = encode_ascii(prefix + " ")
    for probe in probes:
        codes.extend(encode_ascii(str(probe["label"]) + "="))
        codes.append(int(probe["code"]))
        codes.append(ord(" "))
    return codes


def encode_ascii(text: str) -> list[int]:
    return [0x000A if char == "\n" else ord(char) for char in text]


def build_font_patches(preview_dir: Path, font_path: Path, font_index: int, font_size: int) -> list[dict[str, Any]]:
    patches = []
    seen_slots: set[tuple[int, int]] = set()
    for probe in PROBES:
        for candidate in probe["candidates"]:
            child = int(candidate["child"])
            cell = int(candidate["cell"])
            slot = (child, cell)
            if slot in seen_slots:
                continue
            seen_slots.add(slot)
            source, target_page = PAGE_SOURCES[child]
            marker = str(candidate["marker"])
            patches.append(
                {
                    "mode": "render",
                    "target_page": target_page,
                    "target_child": child,
                    "target_cell": cell,
                    "char": marker,
                    "font": str(font_path),
                    "font_index": font_index,
                    "font_size": font_size,
                    "render_mode": "binary",
                    "threshold": 64,
                    "gray_threshold": 176,
                    "stroke_radius": 0,
                    "preview": str(preview_dir / f"child{child}_cell{cell:02d}_{marker}.png"),
                    "source": source,
                }
            )
    return patches


def write_probe_manifest(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["probe_id", "display_label", "display_code", "marker", "child", "source", "cell", "base", "formula"],
        )
        writer.writeheader()
        for probe in PROBES:
            for candidate in probe["candidates"]:
                source = PAGE_SOURCES[int(candidate["child"])][0]
                writer.writerow(
                    {
                        "probe_id": probe["id"],
                        "display_label": probe["label"],
                        "display_code": f"0x{int(probe['code']):04x}",
                        "marker": candidate["marker"],
                        "child": candidate["child"],
                        "source": source,
                        "cell": candidate["cell"],
                        "base": f"0x{int(candidate['base']):04x}",
                        "formula": candidate["formula"],
                    }
                )


def write_readme(path: Path, output_root: Path) -> None:
    lines = [
        "# Page Base Probe v1",
        "",
        f"PPSSPP-ready artifact: `{output_root.as_posix()}/`",
        "",
        "This build patches `DATA001/0008` overlay/body rows so multiple raw",
        "glyph-code bases can be checked in one run. Each displayed code has one or more",
        "candidate font cells patched with marker letters. The marker that appears",
        "in game identifies the active runtime page/cell route for that code.",
        "",
        "Patched overlay/body rows:",
        "",
        "- record `10`: overlay/body hint line `BASE PROBE`",
        "- record `11`: overlay/body hint line `LOOK AT BODY ROWS`",
        "- record `67`: `B0 0100=<mark> 0101=<mark> 011B=<mark>`",
        "- record `69`: `B1 01FE=<mark> 01FB=<mark> 01D4=<mark>`",
        "- record `71`: `B2 021B=<mark> 0222=<mark> 023C=<mark> 0276=<mark> 026E=<mark>`",
        "",
        "Read `probe_manifest.csv` to map marker letters back to candidate bases.",
        "",
        "Example interpretation: if `0100=` shows `A`, candidate `child 1 cell 0",
        "base 0x0100` won. If it shows `B`, candidate `child 2 cell 49 base",
        "0x00cf` won.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
