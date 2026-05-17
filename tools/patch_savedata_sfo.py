from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from param_sfo import FORMAT_BINARY, FORMAT_INT32, FORMAT_UTF8, ParamSfo, load_param_sfo


R2_TITLE = "炼狱贰 The Stairway to H.E.A.V.E.N."


def rengoku2_title(value: str) -> str:
    return value.replace("プレイ時間", "游戏时间")


def rengoku2_detail(value: str) -> str:
    value = re.sub(
        r"ペテロの門を押し開きし魂共よ。\r?\n淑女の許しを得、汝等の罪を浄化せよ。",
        lambda match: "推开彼得之门的灵魂们啊。"
        + ("\r\n" if "\r\n" in match.group(0) else "\n")
        + "蒙淑女允准，净化尔等罪孽。",
        value,
    )
    value = value.replace("クリア回数", "通关次数")
    value = value.replace("死亡回数", "死亡次数")
    value = value.replace("撃破数", "击破数")
    return value


def apply_rengoku2_chs(sfo: ParamSfo) -> dict[str, tuple[str, str]]:
    changes: dict[str, tuple[str, str]] = {}
    if sfo.has_key("SAVEDATA_TITLE"):
        old = sfo.string_value("SAVEDATA_TITLE")
        new = rengoku2_title(old)
        if new != old:
            sfo.set_string("SAVEDATA_TITLE", new)
            changes["SAVEDATA_TITLE"] = (old, new)
    if sfo.has_key("SAVEDATA_DETAIL"):
        old = sfo.string_value("SAVEDATA_DETAIL")
        new = rengoku2_detail(old)
        if new != old:
            sfo.set_string("SAVEDATA_DETAIL", new)
            changes["SAVEDATA_DETAIL"] = (old, new)
    if sfo.has_key("TITLE"):
        old = sfo.string_value("TITLE")
        if old != R2_TITLE:
            sfo.set_string("TITLE", R2_TITLE)
            changes["TITLE"] = (old, R2_TITLE)
    return changes


def field_display(sfo: ParamSfo, key: str) -> str:
    entry = sfo.entries[key]
    value = sfo.value(key)
    if entry.format == FORMAT_UTF8:
        return f"{key}: {value!r} ({entry.length}/{entry.max_length} bytes)"
    if entry.format == FORMAT_INT32:
        return f"{key}: {value} ({entry.length}/{entry.max_length} bytes)"
    if entry.format == FORMAT_BINARY:
        raw = bytes(value)
        return f"{key}: <binary {len(raw)}/{entry.max_length} bytes>"
    raw = bytes(value)
    return f"{key}: <format 0x{entry.format:04x}, {len(raw)}/{entry.max_length} bytes>"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    parser = argparse.ArgumentParser(
        description="List or patch PSP savedata PARAM.SFO metadata fields."
    )
    parser.add_argument("input", type=Path, help="Input savedata PARAM.SFO.")
    parser.add_argument("output", type=Path, nargs="?", help="Output PARAM.SFO. Omit with --in-place or --list.")
    parser.add_argument("--list", action="store_true", help="Print parsed fields without writing.")
    parser.add_argument("--in-place", action="store_true", help="Patch the input file in place.")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing.")
    parser.add_argument("--rengoku2-chs", action="store_true", help="Apply the current Rengoku 2 CHS savedata metadata preset.")
    parser.add_argument("--title", help="Override TITLE.")
    parser.add_argument("--savedata-title", help="Override SAVEDATA_TITLE.")
    parser.add_argument("--detail", help="Override SAVEDATA_DETAIL.")
    args = parser.parse_args()

    sfo = load_param_sfo(args.input)
    if args.list:
        for key in sorted(sfo.entries):
            print(field_display(sfo, key))
        return 0

    changes: dict[str, tuple[str, str]] = {}
    if args.rengoku2_chs:
        changes.update(apply_rengoku2_chs(sfo))
    for key, value in (
        ("TITLE", args.title),
        ("SAVEDATA_TITLE", args.savedata_title),
        ("SAVEDATA_DETAIL", args.detail),
    ):
        if value is None:
            continue
        old = sfo.string_value(key)
        if old != value:
            sfo.set_string(key, value)
            changes[key] = (old, value)

    if not changes:
        print("no changes")
        return 0
    for key, (old, new) in changes.items():
        print(f"{key}: {old!r} -> {new!r}")
    if args.dry_run:
        print("dry run: no file written")
        return 0
    if args.in_place:
        output = args.input
    elif args.output:
        output = args.output
    else:
        raise SystemExit("patch mode requires an output path, --in-place, or --dry-run")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(sfo.to_bytes())
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
