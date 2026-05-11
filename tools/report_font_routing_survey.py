from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_chs_tutorial import DEFAULT_SLOT_POOLS
from tdl import read_tdl


DEFAULT_TEXT_SOURCES = [
    ("DATA001/0003", Path("local/work/extract_text_DATA001_0003_seeded.json")),
    ("DATA001/0008", Path("local/work/extract_text_DATA001_0008_seeded.json")),
    ("DATA001/0012", Path("local/work/extract_text_DATA001_0012_seeded.json")),
    ("DATA001/0015", Path("local/work/extract_text_DATA001_0015_seeded.json")),
    ("DATA001/0016", Path("local/work/extract_text_DATA001_0016_seeded.json")),
    ("DATA001/0017", Path("local/work/extract_text_DATA001_0017_seeded.json")),
    ("DATA002/0065", Path("local/work/extract_text_DATA002_0065_seeded.json")),
    ("DATA003/1089", Path("local/work/extract_text_1089_bin_dialogue_seeded.json")),
]

SEED_SOURCES = [
    Path("samples/runtime_glyph_map_seed.csv"),
    Path("samples/runtime_kana_map.csv"),
    Path("samples/glyph_map_seed.csv"),
    Path("samples/story_glyph_map_seed.csv"),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Survey font routing from clean runtime dumps and glyph-code usage.")
    parser.add_argument("--runtime-scan", type=Path, default=Path("local/work/runtime_font_page_scan_v1/runtime_font_pages.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("local/work/font_routing_survey_v1"))
    args = parser.parse_args()

    usage = collect_glyph_code_usage(DEFAULT_TEXT_SOURCES)
    seeds = read_seed_maps(SEED_SOURCES)
    runtime_rows = read_runtime_scan(args.runtime_scan)
    archive_rows = collect_archive_mig_candidates(Path("local/work/mcd3_entries"))
    rows = build_usage_rows(usage, seeds)
    write_outputs(args.output_dir, rows, runtime_rows, archive_rows, usage, seeds)
    print(f"wrote {args.output_dir}")
    return 0


def collect_glyph_code_usage(sources: list[tuple[str, Path]]) -> dict[int, dict[str, Any]]:
    usage: dict[int, dict[str, Any]] = {}
    for table, path in sources:
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for entry in data.get("entries", []):
            if entry.get("kind") != "glyph_codes":
                continue
            location = f"{table}:r{entry.get('record')}/run{entry.get('run')}"
            for code_text in entry.get("codes", []):
                code = int(str(code_text), 16)
                row = usage.setdefault(
                    code,
                    {
                        "count": 0,
                        "tables": Counter(),
                        "locations": [],
                    },
                )
                row["count"] += 1
                row["tables"][table] += 1
                if len(row["locations"]) < 8:
                    row["locations"].append(location)
    return usage


def read_seed_maps(paths: list[Path]) -> dict[int, list[dict[str, str]]]:
    seeds: dict[int, list[dict[str, str]]] = defaultdict(list)
    for path in paths:
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            for row in csv.DictReader(file):
                code_text = row.get("code")
                if not code_text:
                    continue
                try:
                    code = int(code_text, 16)
                except ValueError:
                    continue
                seed = {key: (value or "") for key, value in row.items()}
                seed["seed_file"] = path.name
                seeds[code].append(seed)
    return dict(seeds)


def read_runtime_scan(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def collect_archive_mig_candidates(root: Path) -> list[dict[str, str]]:
    magic = b"MIG.00.1PSP"
    rows: list[dict[str, str]] = []

    for path in sorted(root.rglob("*_mig.bin")):
        data = path.read_bytes()
        if data.startswith(magic):
            rows.append(mig_resource_row(root, path, "", path.stem, len(data), data))

    for path in sorted(root.rglob("*_tdl.bin")):
        data = path.read_bytes()
        try:
            tdl = read_tdl(path)
        except Exception:
            continue
        for entry in tdl.entries:
            child = data[entry.offset : entry.end_offset]
            if child.startswith(magic):
                rows.append(mig_resource_row(root, path, str(entry.index), entry.name, entry.size, child))

    return rows


def mig_resource_row(root: Path, path: Path, child: str, name: str, size: int, data: bytes) -> dict[str, str]:
    width = ""
    height = ""
    if len(data) >= 0xDC:
        width = str(int.from_bytes(data[0xD8:0xDA], "little"))
        height = str(int.from_bytes(data[0xDA:0xDC], "little"))
    lower_name = name.lower()
    return {
        "source": str(path.relative_to(root)),
        "child": child,
        "name": name,
        "size": f"0x{size:x}",
        "width_hint": width,
        "height_hint": height,
        "is_code_font_name": str("code" in lower_name or "font" in lower_name),
        "is_font_page_size": str(size == 0x2110),
    }


def build_usage_rows(usage: dict[int, dict[str, Any]], seeds: dict[int, list[dict[str, str]]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for code, item in sorted(usage.items()):
        seed_rows = seeds.get(code, [])
        routed = route_by_current_bases(code)
        chars = sorted({seed.get("char", "") for seed in seed_rows if seed.get("char")})
        verifications = sorted({seed.get("verification", "") for seed in seed_rows if seed.get("verification")})
        confidences = sorted({seed.get("confidence", "") for seed in seed_rows if seed.get("confidence")})
        seed_files = sorted({seed.get("seed_file", "") for seed in seed_rows if seed.get("seed_file")})
        explicit_routes = [seed for seed in seed_rows if seed.get("child") or seed.get("cell") or seed.get("base")]
        rows.append(
            {
                "code": f"0x{code:04x}",
                "decimal": str(code),
                "count": str(item["count"]),
                "tables": format_counter(item["tables"]),
                "sample_locations": "; ".join(item["locations"]),
                "seed_chars": "".join(chars),
                "seed_files": "; ".join(seed_files),
                "verification": "; ".join(verifications),
                "confidence": "; ".join(confidences),
                "current_base_routes": "; ".join(format_route(route) for route in routed),
                "explicit_seed_routes": "; ".join(format_seed_route(seed) for seed in explicit_routes),
                "mapping_status": mapping_status(code, seed_rows, routed),
            }
        )
    return rows


def route_by_current_bases(code: int) -> list[dict[str, Any]]:
    routes = []
    for page in DEFAULT_SLOT_POOLS:
        base = int(page["base"])
        cell = code - base
        if 0 <= cell <= 80:
            routes.append(
                {
                    "child": page["child"],
                    "source": page["source"],
                    "base": base,
                    "cell": cell,
                }
            )
    return routes


def mapping_status(code: int, seed_rows: list[dict[str, str]], routed: list[dict[str, Any]]) -> str:
    if code <= 0x00FF:
        return "ascii_or_control"
    if any(seed.get("verification") == "confirmed" for seed in seed_rows):
        return "confirmed_seed"
    if any(seed.get("child") and seed.get("cell") for seed in seed_rows):
        return "seed_route"
    if routed:
        return "current_base_window"
    if seed_rows:
        return "char_seed_only"
    return "unknown"


def format_counter(counter: Counter[str]) -> str:
    return "; ".join(f"{key}:{value}" for key, value in sorted(counter.items()))


def format_route(route: dict[str, Any]) -> str:
    return f"child {route['child']} {route['source']} base 0x{route['base']:04x} cell {route['cell']}"


def format_seed_route(seed: dict[str, str]) -> str:
    parts = []
    if seed.get("child"):
        parts.append(f"child {seed['child']}")
    if seed.get("source"):
        parts.append(seed["source"])
    if seed.get("base"):
        parts.append(f"base {seed['base']}")
    if seed.get("cell"):
        parts.append(f"cell {seed['cell']}")
    if seed.get("runtime_texture"):
        parts.append(f"tex {seed['runtime_texture']}")
    if seed.get("seed_file"):
        parts.append(seed["seed_file"])
    return " ".join(parts)


def write_outputs(
    output_dir: Path,
    rows: list[dict[str, str]],
    runtime_rows: list[dict[str, str]],
    archive_rows: list[dict[str, str]],
    usage: dict[int, dict[str, Any]],
    seeds: dict[int, list[dict[str, str]]],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "glyph_code_usage_routes.csv", rows)

    unknown_rows = [row for row in rows if row["mapping_status"] == "unknown"]
    unknown_rows.sort(key=lambda row: int(row["count"]), reverse=True)
    write_csv(output_dir / "unknown_glyph_codes_top.csv", unknown_rows[:200])

    with (output_dir / "runtime_pages_clean_baseline.csv").open("w", encoding="utf-8", newline="") as file:
        if runtime_rows:
            writer = csv.DictWriter(file, fieldnames=list(runtime_rows[0].keys()))
            writer.writeheader()
            writer.writerows(runtime_rows)

    write_csv(output_dir / "archive_mig_candidates.csv", archive_rows)

    write_markdown(output_dir / "README.md", rows, runtime_rows, archive_rows, usage, seeds, unknown_rows)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(
    path: Path,
    rows: list[dict[str, str]],
    runtime_rows: list[dict[str, str]],
    archive_rows: list[dict[str, str]],
    usage: dict[int, dict[str, Any]],
    seeds: dict[int, list[dict[str, str]]],
    unknown_rows: list[dict[str, str]],
) -> None:
    status_counts = Counter(row["mapping_status"] for row in rows)
    runtime_addresses = sorted({row.get("address", "") for row in runtime_rows if row.get("address")})
    runtime_pixels = sorted({row.get("rgba_sha1", "") for row in runtime_rows if row.get("rgba_sha1")})
    code_font_rows = [row for row in archive_rows if row.get("is_code_font_name") == "True"]
    same_size_rows = [row for row in archive_rows if row.get("is_font_page_size") == "True"]
    lines = [
        "# Font Routing Survey",
        "",
        "Purpose: survey what can be known autonomously about glyph-code routing before PPSSPP patch probes.",
        "",
        "## Scope",
        "",
        "The PPSSPP texture dump directory is treated as a clean original baseline only for the 18 PNGs currently in `local/work/dumped_textures/`. Later PPSSPP dumps may contain font textures already edited by this patch and must not be mixed into this baseline unless they are archived separately as original captures.",
        "",
        "This survey does not claim extra patchable capacity. It separates observed rendered pages, static font resources, and glyph-code mappings.",
        "",
        "## Summary",
        "",
        f"- Clean runtime rendered page observations: {len(runtime_rows)}",
        f"- Unique runtime rendered pages by RGBA hash: {len(runtime_pixels)}",
        f"- Runtime address slots in clean baseline: {len(runtime_addresses)}",
        f"- Current static code pages: {len(DEFAULT_SLOT_POOLS)} JP pages, 891 physical JP cells",
        f"- Archive MIG resources surveyed: {len(archive_rows)}",
        f"- Archive code/font-named MIG resources: {len(code_font_rows)}",
        f"- Archive MIG resources with font-page size `0x2110`: {len(same_size_rows)}",
        f"- Unique glyph codes used in detected text sources: {len(usage)}",
        f"- Glyph codes with any seed label/route: {len([code for code in usage if code in seeds])}",
        "",
        "## Mapping Status",
        "",
    ]
    for status, count in sorted(status_counts.items()):
        lines.append(f"- `{status}`: {count}")
    lines.extend(
        [
            "",
            "Status meanings:",
            "",
            "- `ascii_or_control`: direct ASCII/control value inside a glyph-code run; not a JP page routing gap.",
            "- `confirmed_seed`: seed row says the code was confirmed in PPSSPP or by a direct probe.",
            "- `seed_route`: seed row includes child/cell/base routing but is not marked confirmed.",
            "- `current_base_window`: code falls inside one of the current build base windows.",
            "- `char_seed_only`: code has a character label but no route.",
            "- `unknown`: no current route or seed label.",
            "",
            "## Files",
            "",
            "- `glyph_code_usage_routes.csv`: all used glyph codes joined to seed/current-base routing.",
            "- `unknown_glyph_codes_top.csv`: most frequent unmapped glyph codes.",
            "- `runtime_pages_clean_baseline.csv`: copy of the clean 18-page runtime scan.",
            "- `archive_mig_candidates.csv`: top-level and TDL-child MIG resources from the canonical extraction.",
            "",
            "## Archive Notes",
            "",
            "The code/font-named archive resources are the known `codeANK9x14_00_0` page plus `codeJAP14x14_00_` through `codeJAP14x14_20_`. Other `0x2110` MIG resources exist, but their names are UI texture-like rather than code-page-like; they are candidates for future routing hacks, not currently known font storage.",
            "",
            "## Next Autonomous Steps",
            "",
            "1. Derive candidate routes for `char_seed_only` and high-frequency `unknown` codes by matching seed characters to static/runtime cell images.",
            "2. Keep any new PPSSPP dumps in a separate original-capture directory before running patched builds.",
            "3. After route candidates are exhausted, build small marker probes for unresolved page/layer/code windows.",
            "",
            "## Top Unmapped Codes",
            "",
            "| Code | Count | Tables | Sample locations |",
            "| --- | ---: | --- | --- |",
        ]
    )
    for row in unknown_rows[:25]:
        lines.append(f"| `{row['code']}` | {row['count']} | `{row['tables']}` | `{row['sample_locations']}` |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
