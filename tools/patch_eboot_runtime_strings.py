from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimeStringPatch:
    offset: int
    encoding: str
    old: str
    new: str


PATCHES = (
    RuntimeStringPatch(
        offset=0x11C1F0,
        encoding="utf-16le",
        old="名前を入力してください",
        new="请输入名称",
    ),
    RuntimeStringPatch(
        offset=0x11C310,
        encoding="utf-8",
        old="煉獄弐 The Stairway to H.E.A.V.E.N.",
        new="炼狱贰 The Stairway to H.E.A.V.E.N.",
    ),
    RuntimeStringPatch(
        offset=0x11C337,
        encoding="utf-8",
        old=(
            "ペテロの門を押し開きし魂共よ。\r\n"
            "淑女の許しを得、汝等の罪を浄化せよ。\r\n"
            "クリア回数：000 死亡回数：000 撃破数：00000\r\n"
            "ⓒ2006 HUDSON SOFT ⓒSUEMI JUN 2006"
        ),
        new=(
            "推开彼得之门的众魂啊。\r\n"
            "得淑女之宽恕，净化汝等之罪。                        \r\n"
            "通关总次数：000 死亡次数：000 击破数：00000\r\n"
            "ⓒ2006 HUDSON SOFT ⓒSUEMI JUN 2006"
        ),
    ),
    RuntimeStringPatch(
        offset=0x11C401,
        encoding="utf-8",
        old="プレイ時間 ",
        new="游戏时间 ",
    ),
)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    parser = argparse.ArgumentParser(description="Patch verified Rengoku 2 runtime strings in a decrypted EBOOT ELF.")
    parser.add_argument("input", type=Path, help="Input decrypted EBOOT ELF.")
    parser.add_argument("output", type=Path, help="Output patched decrypted EBOOT ELF.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and report changes without writing.")
    args = parser.parse_args()

    data = bytearray(args.input.read_bytes())
    changes = apply_runtime_string_patches(data)
    for patch, old_len, new_len, capacity in changes:
        print(
            f"0x{patch.offset:06x} {patch.encoding}: "
            f"{old_len}->{new_len}/{capacity} bytes {patch.old!r} -> {patch.new!r}"
        )
    if args.dry_run:
        print("dry run: no file written")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)
    print(f"wrote {args.output}")
    return 0


def apply_runtime_string_patches(data: bytearray) -> list[tuple[RuntimeStringPatch, int, int, int]]:
    changes: list[tuple[RuntimeStringPatch, int, int, int]] = []
    for patch in PATCHES:
        old_bytes = patch.old.encode(patch.encoding)
        new_bytes = patch.new.encode(patch.encoding)
        terminator = b"\x00\x00" if patch.encoding == "utf-16le" else b"\x00"
        start = patch.offset
        end = find_terminator(data, start, terminator, patch.encoding)
        capacity = end - start
        actual = bytes(data[start:end])
        if actual != old_bytes:
            raise ValueError(
                f"unexpected bytes at 0x{start:06x}: "
                f"expected {old_bytes.hex(' ')}, got {actual.hex(' ')}"
            )
        if len(new_bytes) > capacity:
            raise ValueError(
                f"replacement at 0x{start:06x} needs {len(new_bytes)} bytes, "
                f"but only {capacity} bytes are available"
            )
        data[start:end] = new_bytes + b"\x00" * (capacity - len(new_bytes))
        changes.append((patch, len(old_bytes), len(new_bytes), capacity))
    return changes


def find_terminator(data: bytearray, start: int, terminator: bytes, encoding: str) -> int:
    if encoding == "utf-16le":
        cursor = start
        while cursor + 1 < len(data):
            if data[cursor : cursor + 2] == terminator and (cursor - start) % 2 == 0:
                return cursor
            cursor += 2
        raise ValueError(f"unterminated UTF-16LE string at 0x{start:06x}")
    end = data.find(terminator, start)
    if end < 0:
        raise ValueError(f"unterminated string at 0x{start:06x}")
    return end


if __name__ == "__main__":
    raise SystemExit(main())
