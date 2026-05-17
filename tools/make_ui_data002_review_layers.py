from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


UI_ATTACK_ATTRIBUTES = {
    5: "GRAPPLE",
    6: "SLASH",
    7: "IMPACT",
    8: "QUANTUM",
    9: "BULLET",
    10: "HEAT",
}


DATA002_TRANSLATIONS = {
    54: "GRAPPLE",
    86: "游戏分享",
    105: "主线剧情",
    106: "外传剧情",
    107: "音效模式",
    108: "图像",
    119: "剧本1【新数据】",
    120: "剧本2【课程】",
    121: "剧本3【惊愕】",
    122: "剧本4【蜜月】",
    123: "剧本5【ADAM诞生】",
    124: "剧本6【建塔】",
    125: "剧本7【心钥】",
    126: "外传1 序章",
    127: "外传2 序章2",
    128: "外传3 1F【傲慢】",
    129: "外传4 2F【嫉妒】",
    130: "外传5 3F【愤怒】",
    131: "外传6 4F【贪婪】",
    132: "外传7 5F【色欲】",
    133: "外传8 6F【暴食】",
    134: "外传9 7F【怠惰】",
    145: "楼层Boss BGM【对决】",
    150: "Boss战前BGM【战友】",
    151: "Boss战后BGM【解放】",
    154: "丢卡利翁前BGM【再会】",
    155: "丢卡利翁BGM【终焉】",
    159: "职员表BGM【彷徨】",
    166: "阿尔克迈翁",
    168: "封面插图",
    169: "形象插图1",
    170: "形象插图2",
    171: "形象插图3",
    172: "形象插图4",
    178: "尾声至职员表",
    179: "影片：摘要",
    180: "影片：开场",
    181: "影片：结尾至职员表",
    182: "影片：宣传片",
    183: "BGM：1F",
    189: "BGM：Boss 1",
    190: "BGM：Boss 2",
    191: "BGM：Boss 3",
    192: "BGM：Boss 4",
    193: "BGM：Boss 5",
    194: "BGM：格律普斯战",
    195: "BGM：丢卡利翁战",
    196: "BGM：改编1",
    197: "BGM：改编2",
    198: "BGM：改编3",
    199: "BGM：改编4",
    200: "BGM：改编5",
    208: "插图：玛尔斯",
    209: "插图：吕卡翁",
    210: "插图：米诺斯",
    211: "插图：布里阿瑞俄斯",
    212: "插图：斯芬克斯",
    213: "插图：阿尔克迈翁",
    214: "插图：斯塔提乌斯",
    215: "插图：格律普斯",
    216: "插图：丢卡利翁",
    217: "插图：形象1",
    218: "插图：形象2",
    219: "插图：形象3",
    220: "插图：GRAM",
    221: "插图：形象4",
    222: "插图：形象5",
    223: "插图：形象6",
    224: "插图：素体",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate v40 UI/DATA002 review and target sheets.")
    parser.add_argument(
        "--ui-target",
        type=Path,
        default=Path("local/work/translation_refine_v1/merged_target_sheets_v35_quality/DATA001_0016_full_current_target_sheet.json"),
    )
    parser.add_argument(
        "--data002-target",
        type=Path,
        default=Path("local/work/translation_refine_v1/merged_target_sheets_v35_quality/DATA002_0065_full_current_target_sheet.json"),
    )
    parser.add_argument("--ui-review", type=Path, default=Path("local/work/translation_review_slim_v5/ui.json"))
    parser.add_argument("--data002-review", type=Path, default=Path("local/work/translation_review_slim_v5/data002_ui.json"))
    parser.add_argument(
        "--target-root",
        type=Path,
        default=Path("local/work/translation_refine_v1/merged_target_sheets_v40_ui_data002"),
    )
    parser.add_argument("--review-root", type=Path, default=Path("local/work/translation_review_slim_v10_ui_data002"))
    args = parser.parse_args()

    args.target_root.mkdir(parents=True, exist_ok=True)
    args.review_root.mkdir(parents=True, exist_ok=True)

    ui_target = load_json(args.ui_target)
    data002_target = load_json(args.data002_target)
    ui_review = load_json(args.ui_review)
    data002_review = load_json(args.data002_review)

    ui_changes = apply_target_overrides(ui_target, UI_ATTACK_ATTRIBUTES, "v40_attack_attr_en")
    data002_changes = apply_target_overrides(data002_target, DATA002_TRANSLATIONS, "v40_data002_rough_clear")
    apply_review_overrides(ui_review, "DATA001/0016", UI_ATTACK_ATTRIBUTES)
    apply_review_overrides(data002_review, "DATA002/0065", DATA002_TRANSLATIONS)

    ensure_no_rough_markers(data002_target, data002_review)

    ui_target_out = args.target_root / "DATA001_0016_full_current_target_sheet.json"
    data002_target_out = args.target_root / "DATA002_0065_full_current_target_sheet.json"
    ui_review_out = args.review_root / "ui.json"
    data002_review_out = args.review_root / "data002_ui.json"
    summary_out = args.review_root / "summary.json"

    write_json(ui_target_out, ui_target)
    write_json(data002_target_out, data002_target)
    write_json(ui_review_out, slim_review(ui_review))
    write_json(data002_review_out, slim_review(data002_review))

    summary = {
        "target_root": args.target_root.as_posix(),
        "review_root": args.review_root.as_posix(),
        "ui_attack_attribute_rows_changed": len(ui_changes),
        "data002_rows_changed": len(data002_changes),
        "data002_rough_markers_remaining": count_rough_markers(data002_review),
        "ui_attack_attributes": UI_ATTACK_ATTRIBUTES,
        "data002_updated_records": sorted(DATA002_TRANSLATIONS),
    }
    write_json(summary_out, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def apply_target_overrides(payload: dict[str, Any], translations: dict[int, str], note: str) -> list[dict[str, Any]]:
    changes = []
    seen: set[int] = set()
    for row in payload["entries"]:
        record = int(row["record"])
        if int(row.get("run", 0)) != 0 or record not in translations:
            continue
        new = translations[record]
        max_units = int(row["source_max_units"])
        if len(new) > max_units:
            raise ValueError(f"record {record} translation exceeds source slot: {new!r} > {max_units}")
        old = str(row.get("chs_draft", ""))
        row["chs_draft"] = new
        row["source"] = "v40_ui_data002"
        row["notes"] = append_note(str(row.get("notes", "")), note)
        seen.add(record)
        if old != new:
            changes.append({"record": record, "old": old, "new": new, "max_units": max_units})
    missing = sorted(set(translations) - seen)
    if missing:
        raise ValueError(f"missing records in target sheet: {missing}")
    return changes


def apply_review_overrides(rows: list[dict[str, Any]], table: str, translations: dict[int, str]) -> None:
    seen: set[int] = set()
    for row in rows:
        row_table, record, run = parse_record_id(str(row["id"]))
        if row_table != table or run != 0 or record not in translations:
            continue
        row["chs"] = translations[record]
        seen.add(record)
    missing = sorted(set(translations) - seen)
    if missing:
        raise ValueError(f"missing records in review sheet {table}: {missing}")


def parse_record_id(record_id: str) -> tuple[str, int, int]:
    match = re.fullmatch(r"([^#]+)#(\d+):(\d+)", record_id)
    if not match:
        raise ValueError(f"unsupported record id: {record_id!r}")
    return match.group(1), int(match.group(2)), int(match.group(3))


def slim_review(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keys = ("id", "category", "chs", "jp", "en")
    return [{key: row.get(key, "") for key in keys} for row in rows]


def ensure_no_rough_markers(target_payload: dict[str, Any], review_rows: list[dict[str, Any]]) -> None:
    rough_targets = [
        row["record"]
        for row in target_payload["entries"]
        if "粗译" in str(row.get("chs_draft", ""))
    ]
    rough_review = [
        row["id"]
        for row in review_rows
        if "粗译" in str(row.get("chs", ""))
    ]
    if rough_targets or rough_review:
        raise ValueError(f"rough markers remain: target={rough_targets}, review={rough_review[:10]}")


def count_rough_markers(rows: list[dict[str, Any]]) -> int:
    return sum(1 for row in rows if "粗译" in str(row.get("chs", "")))


def append_note(existing: str, note: str) -> str:
    parts = [part.strip() for part in existing.split("|") if part.strip()]
    if note not in parts:
        parts.append(note)
    return " | ".join(parts)


if __name__ == "__main__":
    raise SystemExit(main())
