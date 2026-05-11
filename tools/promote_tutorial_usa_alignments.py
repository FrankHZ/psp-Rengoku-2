from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from build_chs_tutorial import iter_translation_tokens


TUTORIAL_PROMOTIONS = {
    0: "Start继续",
    12: "按L锁定敌人",
    13: "按攻击键使用武器",
    14: "快速连按方向键闪避",
    15: "击败敌人解锁门",
    20: "[状态/地图]\n按L切换两种显示。\n\n-角色状态\n显示体力、防御、装备武器、各部位槽数、技能点、剩余Elixir Skin。\n-楼层地图\n显示已到达区域。红色房间是强敌控制的挑战房。",
    21: "[道具]\n查看获得的道具。\nR键：查看说明\nL键：按类型排序\n连接终端时，按<icon:0161>键将道具还原为Elixir Skin。",
    22: "[强化]\n使用收集的Elixir Skin强化。\n体力上限：增加熔解前可承受伤害。\n物理防御：减少刀弹等物理伤害。\n电子防御：减少激光、电击等电子伤害。\n槽数：增加可装备武器数。\n耐热：提高过热阈值。",
    23: "[装备]\n在此装备道具。\n选择装备部位。\n选择要装备的道具。\n选择装备槽。\n按<icon:0161>键可将道具还原为Elixir Skin。",
    24: "[槽位切换]\n游戏中按Select可打开槽位切换画面。\n同一部位装备多件武器时，可在此选择当前使用的武器。\n方向键：选择要切换的部位\n<icon:013e>键：切换当前槽位\n按<icon:011a>键退出。",
    30: "过热",
    31: "连续使用同一部位会升温。达到极限后会过热并暂时不能使用；腿部过热时无法紧急闪避。\n过热部位会在短时间后恢复。",
    32: "能量",
    33: "使用武器会消耗能量。能量为零后武器无法使用。\n在终端可完全充能。",
    34: "超驱动",
    35: "Meth病毒引发的亢奋状态称为超驱动。\n持续时间内：\n不受伤害。\n能量不减少。\n不会过热。\n连击无上限。",
    36: "灵液外皮",
    37: "Elixir Skin是构成ADAM身体的液态塑料材料，由拥有高级资料传输系统的自律AI细胞组成。\n击败敌人或破坏补给箱可获得。进入终端可用它强化状态。",
    38: "体力恢复",
    39: "拾取后完全恢复体力",
    40: "冷却",
    41: "拾取后所有部位恢复常温。\n过热中也有效。",
    42: "能量恢复",
    43: "拾取后完全补满所有部位武器能量。",
    44: "全恢复",
    45: "拾取后：\n体力全满。\n全身恢复常温。\n武器能量全满。",
    46: "武器舱",
    47: "武器舱含核心单元，可统合大量AI细胞，并含武器的形状与功能资料。使用后可获得武器。",
    48: "过量击杀",
    49: "敌人体力归零后继续造成伤害称为过量击杀。伤害越高，获得的Elixir Skin越多。",
    50: "连锁连击",
    51: "用不同部位连续攻击会形成连锁连击。连击越长，造成伤害与获得的技能经验越多。",
    52: "挑战房",
    53: "由高阶ADAM控制的房间。每层有数间，地图上以红色显示。清除全部挑战房后，通往下一层的传送机启动。",
    54: "清层",
    55: "清除所有挑战房后，终端内通往下一层的传送机启动。若本层有Boss，击败Boss后启动。",
    56: "武器强化",
    57: "同一武器使用足够久后，能力可能提升三类之一：E攻击、物理攻击、电子攻击。提升项取决于武器类型。",
    58: "熔解/重构",
    59: "被敌人击败时，ADAM会熔解并掉到下一层。稍后以初始状态重构，持有武器暂时失效。",
    60: "紧急闪避",
    61: "快速连按方向键或类比摇杆可紧急闪避。腿部过热时不能使用。",
    62: "清房",
    63: "进入房间时，有时所有门会关闭并上锁，这类房间称为锁定房。击败全部敌人后门会打开。",
    64: "技能点",
    65: "击败敌人可获得五类攻击经验并提高攻击力。获得一定经验后得到技能点，可在终端强化能力。",
    72: "槽位切换",
    73: "增加槽数后，一个部位可装备多件武器。若有多件，用槽位切换选择当前使用的武器。",
    74: "倒地闪避",
    75: "被攻击倒地时，掌握时机闪避是起身关键。按方向键两次可快速翻身。",
    76: "状态强化",
    77: "在终端的强化菜单中，可消耗Elixir Skin提升状态。优先强化符合自己战斗方式的项目。",
    79: "此处ADAM会恢复初始状态，当前持有武器全部失效。（离开区域后恢复）",
    81: "此处状态恢复初始值。（离开区域后恢复正常）",
    83: "此处当前持有武器全部不可用。（离开区域后归还）",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Promote DATA001/0008 tutorial placeholders using USA same-record references.")
    parser.add_argument("--input-sheet", type=Path, default=Path("local/work/full_current_target_sheets_v2/DATA001_0008_full_current_target_sheet.json"))
    parser.add_argument("--alignment", type=Path, default=Path("local/work/align_JP0008_USA0017_tutorial_full_v1.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("local/work/tutorial_usa_alignment_promotions_v1"))
    args = parser.parse_args()

    summary = promote_tutorial_placeholders(args.input_sheet, args.alignment, args.output_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def promote_tutorial_placeholders(input_sheet: Path, alignment_path: Path, output_dir: Path) -> dict[str, Any]:
    sheet = json.loads(input_sheet.read_text(encoding="utf-8"))
    alignment = json.loads(alignment_path.read_text(encoding="utf-8"))
    alignment_by_record = {(int(row["record"]), int(row.get("run", 0))): row for row in alignment["entries"]}

    output_dir.mkdir(parents=True, exist_ok=True)
    report_rows: list[dict[str, Any]] = []
    promoted = 0
    over_budget: list[int] = []

    for row in sheet["entries"]:
        if row.get("table") != "DATA001/0008" or int(row.get("run", 0)) != 0:
            continue
        record = int(row["record"])
        if record not in TUTORIAL_PROMOTIONS:
            continue
        old_text = str(row.get("chs_draft", ""))
        new_text = TUTORIAL_PROMOTIONS[record]
        max_units = int(row["source_max_units"])
        units = encoded_unit_count(new_text)
        if units > max_units:
            over_budget.append(record)
        ref = alignment_by_record.get((record, 0), {})
        row["chs_draft"] = new_text
        row["source"] = "usa-aligned-draft"
        row["notes"] = "drafted from DATA001/0017 USA same-record reference; review in PPSSPP"
        promoted += 1
        report_rows.append(
            {
                "record": record,
                "max_units": max_units,
                "new_units": units,
                "fits": units <= max_units,
                "old_chs": old_text,
                "new_chs": new_text,
                "usa_reference_text": ref.get("reference_text", ""),
            }
        )

    if over_budget:
        joined = ", ".join(str(record) for record in over_budget)
        raise ValueError(f"promoted tutorial rows exceed source budgets: {joined}")

    sheet_path = output_dir / "DATA001_0008_full_current_target_sheet.json"
    sheet_path.write_text(json.dumps(sheet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_report(output_dir / "promotions.csv", report_rows)

    readme = output_dir / "README.md"
    readme.write_text(
        "# Tutorial USA Alignment Promotions\n\n"
        "DATA001/0008 was rejoined against the USA DATA001/0017 extraction by same record/run.\n"
        "The fresh pass found English references for all 55 previous `教程粗译` tutorial rows.\n\n"
        f"- promoted rows: {promoted}\n"
        f"- output sheet: `{sheet_path.as_posix()}`\n"
        "- English reference text is kept only in the ignored CSV report.\n",
        encoding="utf-8",
    )
    return {"promoted_rows": promoted, "output_sheet": sheet_path.as_posix(), "report": (output_dir / "promotions.csv").as_posix()}


def encoded_unit_count(text: str) -> int:
    return sum(1 for _ in iter_translation_tokens(text))


def write_report(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["record", "max_units", "new_units", "fits", "old_chs", "new_chs", "usa_reference_text"],
        )
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
