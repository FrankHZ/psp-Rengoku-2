from __future__ import annotations

import argparse
import csv
from itertools import combinations
from pathlib import Path

from PIL import Image

from map_runtime_font_pages import parse_dump_address, parse_dump_hashes
from mig import decode_mig_indices


GROUPS = {
    "idx01_03": {1, 2, 3},
    "idx04_07": {4, 5, 6, 7},
    "idx08_11": {8, 9, 10, 11},
    "idx12_15": {12, 13, 14, 15},
    "low2_nonzero": {1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15},
    "low2_gray_white": {2, 3, 6, 7, 10, 11, 14, 15},
    "high2_nonzero": set(range(4, 16)),
    "high2_gray_white": {8, 9, 10, 11, 12, 13, 14, 15},
    "idx01_07": {1, 2, 3, 4, 5, 6, 7},
    "idx08_15": {8, 9, 10, 11, 12, 13, 14, 15},
    "idx01_15": set(range(1, 16)),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Infer palette-index layer groups from clean PPSSPP runtime dumps.")
    parser.add_argument("--runtime-dir", type=Path, default=Path("local/work/dumped_textures"))
    parser.add_argument("--font-dir", type=Path, default=Path("local/work/tdl_DATA001_0002"))
    parser.add_argument("--output-dir", type=Path, default=Path("local/work/runtime_clut_layer_inference_v1"))
    parser.add_argument("--threshold", type=int, default=16)
    args = parser.parse_args()

    rows = infer_layers(args.runtime_dir, args.font_dir, args.threshold)
    write_outputs(args.output_dir, rows)
    print(f"wrote {args.output_dir}")
    return 0


def infer_layers(runtime_dir: Path, font_dir: Path, threshold: int) -> list[dict[str, str]]:
    font_pages = sorted(path for path in font_dir.glob("*.bin") if path.is_file())
    runtime_files = sorted(path for path in runtime_dir.glob("*.png") if path.is_file())
    base_address = min(parse_dump_address(path) for path in runtime_files)
    rows: list[dict[str, str]] = []

    for runtime_path in runtime_files:
        address = parse_dump_address(runtime_path)
        page_index = (address - base_address) // 0x2100
        if page_index < 0 or page_index >= len(font_pages):
            continue
        runtime_mask = runtime_visible_mask(runtime_path, threshold)
        _, _, static_indices = decode_mig_indices(font_pages[page_index])
        candidates = group_candidates(static_indices, runtime_mask)
        best = min(candidates, key=lambda item: item["diff_pixels"])
        clut_hash, texture_hash = parse_dump_hashes(runtime_path)
        rows.append(
            {
                "runtime_file": runtime_path.name,
                "address": f"0x{address:08x}",
                "page_index": str(page_index),
                "static_page": font_pages[page_index].name,
                "clut_hash": clut_hash,
                "texture_hash": texture_hash,
                "best_group": best["group"],
                "best_indexes": best["indexes"],
                "diff_pixels": str(best["diff_pixels"]),
                "runtime_ink_pixels": str(sum(runtime_mask)),
                "candidate_ink_pixels": str(best["candidate_ink_pixels"]),
                "overlap_pixels": str(best["overlap_pixels"]),
                "jaccard": f"{best['jaccard']:.6f}",
            }
        )
    return rows


def runtime_visible_mask(path: Path, threshold: int) -> list[int]:
    image = Image.open(path).convert("RGBA")
    mask: list[int] = []
    for red, green, blue, alpha in image.getdata():
        visible = alpha > 0 and max(red, green, blue) >= threshold
        mask.append(1 if visible else 0)
    return mask


def compare_masks(name: str, indexes: set[int], runtime_mask: list[int], candidate_mask: list[int]) -> dict[str, object]:
    diff = 0
    overlap = 0
    runtime_ink = 0
    candidate_ink = 0
    union = 0
    for runtime, candidate in zip(runtime_mask, candidate_mask):
        if runtime:
            runtime_ink += 1
        if candidate:
            candidate_ink += 1
        if runtime and candidate:
            overlap += 1
        if runtime or candidate:
            union += 1
        if runtime != candidate:
            diff += 1
    return {
        "group": name,
        "indexes": ",".join(str(index) for index in sorted(indexes)),
        "diff_pixels": diff,
        "runtime_ink_pixels": runtime_ink,
        "candidate_ink_pixels": candidate_ink,
        "overlap_pixels": overlap,
        "jaccard": overlap / union if union else 1.0,
    }


def group_candidates(static_indices: bytes, runtime_mask: list[int] | None = None) -> list[dict[str, object]]:
    dynamic_groups = dict(GROUPS)
    base_names = ["idx01_03", "idx04_07", "idx08_11", "idx12_15"]
    for left, right in combinations(base_names, 2):
        name = f"{left}+{right}"
        dynamic_groups[name] = GROUPS[left] | GROUPS[right]

    candidates = []
    for name, indexes in dynamic_groups.items():
        candidate_mask = [1 if value in indexes else 0 for value in static_indices]
        if runtime_mask is None:
            continue
        candidates.append(compare_masks(name, indexes, runtime_mask, candidate_mask))
    return candidates


def write_outputs(output_dir: Path, rows: list[dict[str, str]]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "runtime_clut_layer_inference.csv"
    if rows:
        with csv_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        csv_path.write_text("", encoding="utf-8")
    write_readme(output_dir / "README.md", rows)


def write_readme(path: Path, rows: list[dict[str, str]]) -> None:
    by_group: dict[str, int] = {}
    by_clut: dict[str, set[str]] = {}
    for row in rows:
        by_group[row["best_group"]] = by_group.get(row["best_group"], 0) + 1
        by_clut.setdefault(row["clut_hash"], set()).add(row["best_group"])
    lines = [
        "# Runtime CLUT Layer Inference",
        "",
        "Purpose: compare clean PPSSPP rendered pages against static MIG palette-index groups.",
        "",
        "This is heuristic. A good match suggests which index group a CLUT exposes, but PPSSPP observation/probe is still required before using it as capacity.",
        "",
        "## Summary",
        "",
        f"- Runtime observations scored: {len(rows)}",
        "",
        "Best-group counts:",
        "",
    ]
    for group, count in sorted(by_group.items()):
        lines.append(f"- `{group}`: {count}")
    lines.extend(["", "CLUT hash to best groups:", ""])
    for clut, groups in sorted(by_clut.items()):
        lines.append(f"- `{clut}`: {', '.join(sorted(groups))}")
    lines.extend(
        [
            "",
            "## Observations",
            "",
            "| File | Page | CLUT | Best group | Diff pixels | Jaccard |",
            "| --- | ---: | --- | --- | ---: | ---: |",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['runtime_file']}` | {row['page_index']} | `{row['clut_hash']}` | "
            f"`{row['best_group']}` | {row['diff_pixels']} | {row['jaccard']} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
