from __future__ import annotations

import argparse
import csv
from pathlib import Path


HIRAGANA = "ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをん"
KATAKANA = "ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶ"

RUNTIME_RANGES = (
    {"start": 0x0100, "end": 0x0150, "child": 1, "source": "codeJAP14x14_00_", "base": 0x0100, "texture": "0x040de300"},
    {"start": 0x0151, "end": 0x01A1, "child": 1, "source": "codeJAP14x14_00_", "base": 0x0151, "texture": "0x040de300"},
    {"start": 0x01A2, "end": 0x01F2, "child": 2, "source": "codeJAP14x14_02_", "base": 0x01A2, "texture": "0x040e0400"},
    {"start": 0x01F3, "end": 0x0243, "child": 2, "source": "codeJAP14x14_02_", "base": 0x01F3, "texture": "0x040e0400"},
    {"start": 0x0244, "end": 0x0294, "child": 3, "source": "codeJAP14x14_04_", "base": 0x0244, "texture": "0x040e2500"},
)

SEED_POINTS = {
    0x01D4: "い",
    0x01DB: "か",
    0x01EF: "た",
    0x01F6: "て",
    0x01FB: "に",
    0x01FE: "の",
    0x020E: "ま",
    0x021B: "る",
    0x021C: "れ",
    0x0225: "ア",
    0x0227: "イ",
    0x0229: "ウ",
    0x022D: "オ",
    0x023C: "ス",
    0x0246: "ッ",
    0x026E: "ル",
    0x0275: "ヲ",
    0x0276: "ン",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the inferred runtime kana mapping.")
    parser.add_argument("--output", type=Path, default=Path("samples/runtime_kana_map.csv"))
    args = parser.parse_args()
    write_kana_map(args.output)
    print(f"wrote {args.output}")
    return 0


def write_kana_map(path: Path) -> None:
    rows = []
    rows.extend(build_block("hiragana", HIRAGANA, 0x01D1))
    rows.extend(build_block("katakana", KATAKANA, 0x0224))

    mismatches = [
        f"0x{row['code']:04x}: expected {SEED_POINTS[row['code']]} got {row['char']}"
        for row in rows
        if row["code"] in SEED_POINTS and row["char"] != SEED_POINTS[row["code"]]
    ]
    if mismatches:
        raise ValueError("kana seed mismatch: " + "; ".join(mismatches))

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "code",
                "char",
                "block",
                "index",
                "child",
                "source",
                "cell",
                "runtime_texture",
                "base",
                "confidence",
                "notes",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "code": f"0x{row['code']:04x}",
                    "char": row["char"],
                    "block": row["block"],
                    "index": row["index"],
                    "child": row["child"],
                    "source": row["source"],
                    "cell": row["cell"],
                    "runtime_texture": row["runtime_texture"],
                    "base": f"0x{row['base']:04x}",
                    "confidence": row["confidence"],
                    "notes": row["notes"],
                }
            )


def build_block(block: str, chars: str, start_code: int) -> list[dict[str, object]]:
    rows = []
    for index, char in enumerate(chars):
        code = start_code + index
        route = runtime_route(code)
        seeded = code in SEED_POINTS
        rows.append(
            {
                "code": code,
                "char": char,
                "block": block,
                "index": index,
                "child": route["child"],
                "source": route["source"],
                "cell": code - int(route["base"]),
                "runtime_texture": route["texture"],
                "base": route["base"],
                "confidence": "seeded" if seeded else "inferred",
                "notes": "matches existing seed point" if seeded else "inferred from contiguous JIS kana order and confirmed runtime base ranges",
            }
        )
    return rows


def runtime_route(code: int) -> dict[str, object]:
    for route in RUNTIME_RANGES:
        if int(route["start"]) <= code <= int(route["end"]):
            return route
    raise ValueError(f"no runtime route for 0x{code:04x}")


if __name__ == "__main__":
    raise SystemExit(main())
