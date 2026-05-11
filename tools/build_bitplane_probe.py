from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from stage_font_probe import stage_font_probe


DEFAULT_FONT = Path("C:/Windows/Fonts/simsun.ttc")
DEFAULT_EXTRACTED_ROOT = Path("local/extracted/Rengoku 2")
DEFAULT_ENTRIES_ROOT = Path("local/work/mcd3_entries")
DEFAULT_SOURCE_ENTRY = Path("local/work/mcd3_entries/DATA001/0008_bin.bin")

PAGE_SOURCES = {
    1: ("codeJAP14x14_00_", "local/work/tdl_DATA001_0002/0001_codeJAP14x14_00_.bin"),
    2: ("codeJAP14x14_02_", "local/work/tdl_DATA001_0002/0002_codeJAP14x14_02_.bin"),
    3: ("codeJAP14x14_04_", "local/work/tdl_DATA001_0002/0003_codeJAP14x14_04_.bin"),
    4: ("codeJAP14x14_06_", "local/work/tdl_DATA001_0002/0004_codeJAP14x14_06_.bin"),
    5: ("codeJAP14x14_08_", "local/work/tdl_DATA001_0002/0005_codeJAP14x14_08_.bin"),
    6: ("codeJAP14x14_10_", "local/work/tdl_DATA001_0002/0006_codeJAP14x14_10_.bin"),
    7: ("codeJAP14x14_12_", "local/work/tdl_DATA001_0002/0007_codeJAP14x14_12_.bin"),
    8: ("codeJAP14x14_14_", "local/work/tdl_DATA001_0002/0008_codeJAP14x14_14_.bin"),
    9: ("codeJAP14x14_16_", "local/work/tdl_DATA001_0002/0009_codeJAP14x14_16_.bin"),
    10: ("codeJAP14x14_18_", "local/work/tdl_DATA001_0002/0010_codeJAP14x14_18_.bin"),
    11: ("codeJAP14x14_20_", "local/work/tdl_DATA001_0002/0011_codeJAP14x14_20_.bin"),
}

PROBES = (
    {"child": 1, "cell": 0, "low_code": 0x0100, "low_marker": "A", "high_code": 0x0151, "high_marker": "B"},
    {"child": 2, "cell": 0, "low_code": 0x01A2, "low_marker": "C", "high_code": 0x01F3, "high_marker": "D"},
    {"child": 3, "cell": 0, "low_code": 0x0244, "low_marker": "E", "high_code": 0x0295, "high_marker": "F"},
    {"child": 4, "cell": 0, "low_code": 0x02E6, "low_marker": "G", "high_code": 0x0337, "high_marker": "H"},
    {"child": 5, "cell": 0, "low_code": 0x0388, "low_marker": "I", "high_code": 0x03D9, "high_marker": "J"},
    {"child": 6, "cell": 0, "low_code": 0x042A, "low_marker": "K", "high_code": 0x047B, "high_marker": "L"},
    {"child": 9, "cell": 0, "low_code": 0x0610, "low_marker": "M", "high_code": 0x0661, "high_marker": "N"},
    {"child": 10, "cell": 0, "low_code": 0x06B2, "low_marker": "O", "high_code": 0x0703, "high_marker": "P"},
)

ROWS = (
    (10, "BITPLANE PROBE"),
    (11, "LOW HIGH SAME CELL"),
    (67, "P1", PROBES[0:3]),
    (69, "P2", PROBES[3:6]),
    (71, "P3", PROBES[6:8]),
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a PPSSPP-ready probe for split low/high font bitplanes.")
    parser.add_argument("--work-root", type=Path, default=Path("local/work/bitplane_probe_v1"))
    parser.add_argument("--output-root", type=Path, default=Path("local/rebuilt/bitplane_probe_v1_extracted"))
    parser.add_argument("--font", type=Path, default=DEFAULT_FONT)
    parser.add_argument("--font-index", type=int, default=0)
    parser.add_argument("--font-size", type=int, default=12)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    build_bitplane_probe(
        work_root=args.work_root,
        output_root=args.output_root,
        font_path=args.font,
        font_index=args.font_index,
        font_size=args.font_size,
        overwrite=args.overwrite,
    )
    print(f"staged {args.output_root}")
    return 0


def build_bitplane_probe(
    work_root: Path,
    output_root: Path,
    font_path: Path = DEFAULT_FONT,
    font_index: int = 0,
    font_size: int = 12,
    overwrite: bool = False,
) -> None:
    work_root.mkdir(parents=True, exist_ok=True)
    text_json = work_root / "DATA001_0008_bitplane_probe.json"
    text_json.write_text(json.dumps(build_text_payload(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    write_probe_manifest(work_root / "probe_manifest.csv")
    write_readme(work_root / "README.md", output_root)

    stage_config = {
        "extracted_root": str(DEFAULT_EXTRACTED_ROOT),
        "entries_root": str(DEFAULT_ENTRIES_ROOT),
        "work_root": str(work_root / "stage"),
        "output_root": str(output_root),
        "font_patches": build_font_patches(work_root / "previews", font_path, font_index, font_size),
        "text_patch": {
            "entry_id": 8,
            "source_entry": str(DEFAULT_SOURCE_ENTRY),
            "json": str(text_json),
        },
        "overwrite": overwrite,
    }
    (work_root / "stage_bitplane_probe.json").write_text(
        json.dumps(stage_config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    stage_font_probe(stage_config)


def build_text_payload() -> dict[str, Any]:
    entries = []
    for index, row in enumerate(ROWS):
        record = int(row[0])
        codes = encode_ascii(str(row[1])) if len(row) == 2 else encode_probe_line(str(row[1]), row[2])
        entries.append(
            {
                "id": f"bitplane-probe-{index:02d}",
                "record": record,
                "run": 0,
                "kind": "glyph_codes",
                "length": max(len(codes), 1),
                "translation": "",
                "translation_codes": [f"0x{code:04x}" for code in codes],
                "notes": "generated by tools/build_bitplane_probe.py",
            }
        )
    return {
        "format": "offset-table-runs-v1",
        "source": str(DEFAULT_SOURCE_ENTRY),
        "entries": entries,
    }


def encode_probe_line(prefix: str, probes: tuple[dict[str, Any], ...]) -> list[int]:
    codes = encode_ascii(prefix + " ")
    for probe in probes:
        codes.extend(encode_ascii(f"{probe['low_code']:03X}="))
        codes.append(int(probe["low_code"]))
        codes.append(ord(" "))
        codes.extend(encode_ascii(f"{probe['high_code']:03X}="))
        codes.append(int(probe["high_code"]))
        codes.append(ord(" "))
    return codes


def encode_ascii(text: str) -> list[int]:
    return [0x000A if char == "\n" else ord(char) for char in text]


def build_font_patches(
    preview_dir: Path,
    font_path: Path,
    font_index: int,
    font_size: int,
) -> list[dict[str, Any]]:
    patches = []
    for probe in PROBES:
        child = int(probe["child"])
        cell = int(probe["cell"])
        source, target_page = PAGE_SOURCES[child]
        for layer, marker in (("low", probe["low_marker"]), ("high", probe["high_marker"])):
            patches.append(
                {
                    "mode": "render_bitplane",
                    "target_page": target_page,
                    "target_child": child,
                    "target_cell": cell,
                    "layer": layer,
                    "char": marker,
                    "font": str(font_path),
                    "font_index": font_index,
                    "font_size": font_size,
                    "render_mode": "binary",
                    "threshold": 64,
                    "gray_threshold": 176,
                    "stroke_radius": 0,
                    "preview": str(preview_dir / f"child{child:02d}_cell{cell:02d}_{layer}_{marker}.png"),
                    "source": source,
                }
            )
    return patches


def write_probe_manifest(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["child", "source", "cell", "layer", "display_code", "marker", "expected"],
        )
        writer.writeheader()
        for probe in PROBES:
            source = PAGE_SOURCES[int(probe["child"])][0]
            for layer, code_key, marker_key in (
                ("low", "low_code", "low_marker"),
                ("high", "high_code", "high_marker"),
            ):
                writer.writerow(
                    {
                        "child": probe["child"],
                        "source": source,
                        "cell": probe["cell"],
                        "layer": layer,
                        "display_code": f"0x{int(probe[code_key]):04x}",
                        "marker": probe[marker_key],
                        "expected": f"{int(probe[code_key]):03X}={probe[marker_key]}",
                    }
                )


def write_readme(path: Path, output_root: Path) -> None:
    expected = []
    for probe in PROBES:
        expected.append(f"- `{probe['low_code']:03X}={probe['low_marker']}` and `{probe['high_code']:03X}={probe['high_marker']}`")
    lines = [
        "# Bitplane Probe v1",
        "",
        f"PPSSPP-ready artifact: `{output_root.as_posix()}/`",
        "",
        "This build tests whether paired low/high code windows can share one physical",
        "font cell. Each pair writes two marker letters into the same child/cell:",
        "one in the low two bits and one in the high two bits.",
        "",
        "Expected visible markers:",
        "",
        *expected,
        "",
        "If a pair shows both expected markers, that physical cell can likely carry",
        "two logical glyphs for those code windows. If either marker is missing or",
        "both codes show the same marker, that route needs a different model.",
        "",
        "Patched text rows are in DATA001/0008 records 10, 11, 67, 69, and 71.",
        "Read `probe_manifest.csv` for the child/cell/layer mapping.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
