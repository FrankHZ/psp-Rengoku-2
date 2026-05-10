from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_UI_SHEET = Path("local/work/ui_help_chs_v1/DATA001_0016_ui_sheet.json")
DEFAULT_HELP_SHEET = Path("local/work/ui_help_chs_v1/DATA001_0017_help_sheet.json")
DEFAULT_HELP_WIDTH = 20
MANUAL_HELP_TEXT = {
    18: (
        "熟练度有5个类别\n\n"
        "1. 抓取  GRAPPLE\n"
        "   爪、拳套等近战攻击\n"
        "2. 斩击  SLASH\n"
        "   刀刃近战攻击\n"
        "3. 冲击  IMPACT\n"
        "   导弹等爆炸攻击\n"
        "4. 弹丸  BULLET\n"
        "   枪械射击攻击\n"
        "5. 量子  QUANTUM\n"
        "   激光、粒子能量攻击\n\n"
        "战斗越多ADAM越熟练，攻击力会提升。\n"
        "技能点显示在状态画面。\n"
        "增长速度取决于装备武器。"
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply runtime layout fixes to CHS UI/help translator sheets.")
    parser.add_argument("--ui-sheet", type=Path, default=DEFAULT_UI_SHEET)
    parser.add_argument("--help-sheet", type=Path, default=DEFAULT_HELP_SHEET)
    parser.add_argument("--help-width", type=int, default=DEFAULT_HELP_WIDTH)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    ui_changed = pad_input_tokens(args.ui_sheet, dry_run=args.dry_run)
    help_changed = wrap_help_body(args.help_sheet, width=args.help_width, dry_run=args.dry_run)
    print(f"ui token rows changed: {ui_changed}")
    print(f"help body rows changed: {help_changed}")
    return 0


def pad_input_tokens(path: Path, dry_run: bool = False) -> int:
    payload = load_json(path)
    changed = 0
    for entry in payload.get("entries", []):
        draft = str(entry.get("chs_draft", ""))
        fixed = draft.replace("按?@  ", "?@").replace("按?@", "?@").replace("?@  ", "?@")
        if fixed == draft:
            continue
        if len(fixed) > int(entry.get("source_max_units", len(fixed))):
            continue
        entry["chs_draft"] = fixed
        entry["chs_units"] = len(fixed)
        changed += 1
    if changed and not dry_run:
        write_json(path, payload)
    return changed


def wrap_help_body(path: Path, width: int, dry_run: bool = False) -> int:
    payload = load_json(path)
    changed = 0
    for entry in payload.get("entries", []):
        if int(entry.get("source_max_units", 0)) < 40:
            continue
        draft = str(entry.get("chs_draft", ""))
        record = int(entry.get("record", -1))
        wrapped = MANUAL_HELP_TEXT.get(record, wrap_text(draft, width))
        if wrapped == draft:
            continue
        if len(wrapped) > int(entry.get("source_max_units", len(wrapped))):
            continue
        entry["chs_draft"] = wrapped
        entry["chs_units"] = len(wrapped)
        changed += 1
    if changed and not dry_run:
        write_json(path, payload)
    return changed


def wrap_text(text: str, width: int) -> str:
    paragraphs = text.replace("\r\n", "\n").split("\n\n")
    return "\n\n".join(wrap_paragraph(paragraph, width) for paragraph in paragraphs)


def wrap_paragraph(paragraph: str, width: int) -> str:
    compact = "".join(line.strip() for line in paragraph.split("\n"))
    if not compact:
        return ""
    compact = add_semantic_breaks(compact)

    lines: list[str] = []
    for segment in compact.split("\n"):
        if segment == "":
            lines.append("")
            continue
        current = ""
        for char in segment:
            if len(current) >= width and can_break_before(char):
                lines.append(current)
                current = ""
            current += char
            if len(current) >= width and can_break_after(char):
                lines.append(current)
                current = ""
        if current:
            lines.append(current)
    return "\n".join(lines)


def add_semantic_breaks(text: str) -> str:
    replacements = {
        "。·": "。\n\n·",
        "；·": "；\n\n·",
        "。1": "。\n1",
        "。2": "。\n2",
        "。3": "。\n3",
        "。4": "。\n4",
        "。5": "。\n5",
        "。6": "。\n6",
        "。7": "。\n7",
        "。8": "。\n8",
        "。9": "。\n9",
        "。10": "。\n10",
        "。11": "。\n11",
        "。12": "。\n12",
        "。13": "。\n13",
        "。14": "。\n14",
        "。15": "。\n15",
        "。16": "。\n16",
        "。17": "。\n17",
        "。18": "。\n18",
        "。19": "。\n19",
    }
    for before, after in replacements.items():
        text = text.replace(before, after)
    return text


def can_break_before(char: str) -> bool:
    return char not in "，。；：、,.!?:;)]）】"


def can_break_after(char: str) -> bool:
    return char in "，。；：、,.!?:;)]）】" or len(char) == 1


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
