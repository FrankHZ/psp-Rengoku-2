from __future__ import annotations

import argparse
from pathlib import Path

from png_rgba import read_png_rgba


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare dumped runtime PNGs against rendered static PNGs.")
    parser.add_argument("runtime_dir", type=Path)
    parser.add_argument("static_dir", type=Path)
    parser.add_argument("--mode", choices=("rgba", "alpha", "coverage"), default="rgba")
    args = parser.parse_args()

    runtime_files = sorted(args.runtime_dir.glob("*.png"))
    static_files = sorted(args.static_dir.glob("*.png"))
    static_images = [(path, read_png_rgba(path)) for path in static_files]

    print("runtime\taddress\tbest_static\tmse")
    for runtime_path in runtime_files:
        runtime_image = read_png_rgba(runtime_path)
        best_path = None
        best_score = None
        for static_path, static_image in static_images:
            score = mse(runtime_image, static_image, args.mode)
            if best_score is None or score < best_score:
                best_score = score
                best_path = static_path
        print(f"{runtime_path.name}\t0x{runtime_path.name[:8]}\t{best_path.name if best_path else ''}\t{best_score:.2f}")
    return 0


def mse(left: tuple[int, int, bytes], right: tuple[int, int, bytes], mode: str) -> float:
    if left[0] != right[0] or left[1] != right[1]:
        return float("inf")
    left_data = left[2]
    right_data = right[2]
    total = 0
    values = zip(pixel_values(left_data, mode), pixel_values(right_data, mode))
    count = 0
    for left_value, right_value in values:
        diff = left_value - right_value
        total += diff * diff
        count += 1
    return total / count


def pixel_values(data: bytes, mode: str):
    if mode == "rgba":
        yield from data
        return

    for index in range(0, len(data), 4):
        red = data[index]
        green = data[index + 1]
        blue = data[index + 2]
        alpha = data[index + 3]
        if mode == "alpha":
            yield alpha
        elif mode == "coverage":
            yield 255 if alpha or red or green or blue else 0
        else:
            raise ValueError(mode)


if __name__ == "__main__":
    raise SystemExit(main())
