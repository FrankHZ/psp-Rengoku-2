from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


DEFAULT_UI_SHEET = Path("local/work/ui_help_chs_v1/DATA001_0016_ui_sheet.json")
DEFAULT_HELP_SHEET = Path("local/work/ui_help_chs_v1/DATA001_0017_help_sheet.json")
DEFAULT_TUTORIAL_SHEET = Path(
    "local/work/combined_chs_v12_manual_skillpoints_0003_0008_0012anchored_0015full_0016full_0017full/"
    "DATA001_0008_chs.json"
)
DEFAULT_HELP_WIDTH = 20
DEFAULT_PROSE_WIDTH = 16
INLINE_CODE_RE = re.compile(r"<(?:icon|code):0x?([0-9a-fA-F]{1,4})>")
PROSE_LAYOUT_RECORDS = {
    14,  # A2
    38,  # C5
    55,  # F1
    59,  # F3
    63,  # G1
    65,  # G2
    75,  # G7
    79,  # G9
    81,  # H1
    83,  # H2
    87,  # H4
    89,  # H5
    93,  # H7
}
MANUAL_HELP_TEXT = {
    12: (
        "· 体力：\n"
        "左上生命槽。\n"
        "归零会熔解，\n"
        "已持武器掉落，\n"
        "ADAM回到最低层。\n"
        "体力会随时间恢复。\n\n"
        "· 物理防御：\n"
        "减少物理伤害。\n"
        "可在终端或状态菜单查看。\n"
        "武器物理攻击力\n"
        "可在道具等菜单查看。\n\n"
        "· 电子防御：\n"
        "减少电子伤害。\n"
        "同样可在终端或状态菜单查看。\n"
        "武器电子攻击力\n"
        "可在道具等菜单查看。"
    ),
    16: (
        "槽位是装备武器所需接口。\n\n"
        "每件武器需要1至3槽，\n"
        "所需槽数因武器而异。\n\n"
        "每个身体部位最多5槽。\n\n"
        "同一部位装多件武器时，\n"
        "按SELECT键切换武器。"
    ),
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
    20: (
        "武器分3类：\n"
        "1. 攻击武器：头、手臂、躯干\n"
        "2. 防御武器：手臂、躯干\n"
        "3. 辅助武器：腿部\n\n"
        "这3类又分为6型：\n"
        "（攻击武器）\n"
        "近战  刀刃  枪械\n"
        "（防御武器）\n"
        "盾牌  装甲\n"
        "（辅助武器）\n"
        "腿部"
    ),
    22: (
        "按R键查看当前武器\n"
        "基本能力的详细资料。\n\n"
        "详细资料包括：\n"
        "·所选武器名称\n"
        "·所选武器说明\n"
        "·使用次数、热量、攻击力等\n"
        "·能力概览雷达图\n"
        "·能力提升的强化值\n"
        "·称为属性的特殊追加效果"
    ),
    24: (
        "属性是武器的特殊追加效果。\n"
        "并非所有武器都有属性，\n"
        "命中时也不一定发动。\n\n"
        "属性共有19种：\n\n"
        " 1. 速度提升\n"
        "    移动速度上升。\n"
        " 2. 冷却提升\n"
        "    热量增加降低。\n"
        " 3. 恢复体力\n"
        "    恢复体力。\n"
        " 4. 物理麻痹攻击\n"
        "    物理攻击使敌人麻痹。\n"
        " 5. 电子麻痹攻击\n"
        "    电子攻击使敌人麻痹。\n"
        " 6. 浮空攻击\n"
        "    将敌人打离地面。\n"
        " 7. 击倒攻击\n"
        "    将敌人击倒在地。\n"
        " 8. 减速攻击\n"
        "    降低敌人移动速度。\n"
        " 9. 击退攻击\n"
        "    将敌人向后击退。\n"
        "10. 吹飞攻击\n"
        "    将敌人向后吹飞。\n"
        "11. 破防\n"
        "    突破盾牌防御。\n"
        "12. 故障攻击\n"
        "    削减敌武器能量。\n"
        "13. 破坏物体\n"
        "    一击破坏可破坏物。\n"
        "14. 蓄力攻击\n"
        "    蓄力后发动重击。\n"
        "15. 无视防御\n"
        "    敌人无法防御。\n"
        "16. 暴击效果\n"
        "    敌耐久减半。\n"
        "17. 机动\n"
        "    可在移动中使用。\n"
        "18. 连携连击\n"
        "    增加连段攻击次数。\n"
        "19. 穿甲弹\n"
        "    弹丸贯穿敌人。"
    ),
    26: (
        "部分装备武器可提升基本能力，\n"
        "这称为强化。\n\n"
        "武器必须长期使用，\n"
        "才可能发生强化。\n\n"
        "击败敌人时会随机强化，\n"
        "但并非一定触发。\n\n"
        "强化是随机的，无法指定项目。\n"
        "空手攻击也不会触发强化。\n\n"
        "强化分3类：\n\n"
        "1. EG\n"
        "   能量增益，可使用更久。\n\n"
        "2. HR\n"
        "   热量降低，不易过热。\n\n"
        "3. CE\n"
        "   效果率，特殊效果更易发动。"
    ),
    28: (
        "按R键查看当前武器基本能力。\n\n"
        "详情画面会用雷达图\n"
        "粗略显示武器能力。\n"
        "显示项目因武器而异。\n\n"
        "（近战、刀刃、枪械）\n"
        "1. Power：物理与电子攻击\n"
        "2. Ammo：能量消耗\n"
        "3. Hit：射程与命中率\n"
        "4. Use：所需槽位和属性\n"
        "5. Rare：稀有度\n\n"
        "（盾牌、装甲）\n"
        "1. Def：物理与电子防御\n"
        "2. Stam：能量消耗\n"
        "3. Rst：状态抗性\n"
        "4. Efct：属性\n"
        "5. Rare：稀有度\n\n"
        "（腿部）\n"
        "1. Mob：移动速度和冷却\n"
        "2. Outp：次数与能量消耗\n"
        "3. Rst：状态抗性\n"
        "4. Efct：属性\n"
        "5. Rare：稀有度"
    ),
    30: (
        "终端用于维护ADAM。\n"
        "位于传送目的地房间墙上。\n\n"
        "终端左右有传送装置：\n"
        "·左（蓝）：前往下层\n"
        "·右（红）：前往上层\n\n"
        "面向终端按<icon:011a>键连接。\n\n"
        "连接后体力和武器能量全恢复，\n"
        "并显示状态信息与楼层地图。\n\n"
        "终端菜单有7项：\n\n"
        "1. EQUIP  更换装备\n"
        "2. UPGRADE  强化能力\n"
        "3. ITEM  查看道具\n"
        "4. FILE  保存/删除存档\n"
        "5. OPTION  调音量或结束游戏\n"
        "6. HELP  查看术语和技巧\n"
        "7. EXIT  返回游戏\n\n"
        "按<icon:01a8>键切换状态与楼层地图。\n\n"
        "·状态显示\n"
        "1. 当前最大体力\n"
        "2. 物理防御\n"
        "3. 电子防御\n"
        "4. 当前灵药皮肤\n"
        "5. 当前装备武器\n"
        "6. 各部位槽位数\n"
        "7. 技能点\n\n"
        "·楼层地图\n"
        "显示已到过区域。\n"
        "红房是强敌控制的挑战房。"
    ),
    32: (
        "更换ADAM装备武器：\n"
        "先选装备部位，\n"
        "再选道具，\n"
        "最后选槽位。\n\n"
        "按<icon:0161>键可将道具\n"
        "回收为灵药皮肤。"
    ),
    34: (
        "使用灵药皮肤强化ADAM。\n\n"
        "ADAM可强化5类：\n\n"
        "1. 最大体力\n"
        "   提高熔解前可承受伤害。\n"
        "2. 物理防御\n"
        "   减轻刀刃、弹丸等物理攻击。\n"
        "3. 电子防御\n"
        "   减轻激光、电击等电子攻击。\n"
        "4. 槽位数\n"
        "   增加可装备武器槽。\n"
        "5. 耐热\n"
        "   提高各部位过热上限。"
    ),
    36: (
        "查看已收集道具。\n\n"
        "·<icon:01ae>键：查看道具详细资料\n"
        "·<icon:01a8>键：按类型排序\n\n"
        "按<icon:0161>键可将道具\n"
        "回收为灵药皮肤。"
    ),
    42: (
        "显示ADAM状态或楼层地图。\n\n"
        "暂停菜单有4项：\n\n"
        "1. ITEM  查看道具\n"
        "2. OPTION  调音量并结束游戏\n"
        "3. HELP  查看术语和技巧\n"
        "4. EXIT  返回游戏\n\n"
        "按<icon:01a8>键在状态和地图间切换。\n\n"
        "·状态显示\n"
        "1. 当前最大体力\n"
        "2. 物理防御\n"
        "3. 电子防御\n"
        "4. 当前灵药皮肤\n"
        "5. 当前装备武器\n"
        "6. 各部位槽位数\n"
        "7. 技能点\n\n"
        "·楼层地图\n"
        "显示已到过区域。\n"
        "红房是强敌控制的挑战房。"
    ),
    44: (
        "查看已收集道具。\n\n"
        "·<icon:01ae>键：查看道具详情\n"
        "·<icon:01a8>键：按类型排序\n\n"
        "可将道具\n"
        "回收为灵药皮肤。"
    ),
    47: (
        "方向键上：前进\n"
        "方向键下：后退\n"
        "方向键左：左转\n"
        "方向键右：右转\n\n"
        "移动时按住<icon:01ae>键，\n"
        "可保持朝向平移。\n\n"
        "方向键或摇杆连按两次，\n"
        "即可进行闪避。"
    ),
    49: (
        "用4个部位装备的武器攻击：\n\n"
        "<icon:0161>键：头部\n\n"
        "<icon:015f>键：左臂\n\n"
        "<icon:011a>键：右臂\n\n"
        "<icon:013e>键：躯干\n\n"
        "未装备武器时会出拳。"
    ),
    53: (
        "游戏中按SELECT键\n"
        "打开切换槽位画面。\n\n"
        "同一部位装有多件武器时，\n"
        "可选择当前使用的武器，\n"
        "也就是有效槽位。\n\n"
        "·方向键：选择要切换的部位\n"
        "·<icon:011a>键：切换有效槽位\n\n"
        "按<icon:013e>键结束切换槽位。\n\n"
        "熟练使用多种武器，\n"
        "可节省弹药并应对战斗。"
    ),
    57: (
        "楼层地图会简要显示\n"
        "已到过的房间。\n\n"
        "楼层由多种房间组成。\n\n"
        "在终端或暂停菜单按<icon:01a8>键，\n"
        "可切换查看楼层地图。\n\n"
        "地图标记如下：\n\n"
        "·黄色方块\n"
        "  终端，本层起点。\n"
        "  每层仅有一处。\n\n"
        "·红三角\n"
        "  通往上层的传送装置。\n\n"
        "·蓝三角\n"
        "  通往下层的传送装置。\n\n"
        "·红色房间\n"
        "  强敌控制的挑战房。\n"
        "  起初即显示。\n\n"
        "·红方块\n"
        "  尚未访问的房间。\n\n"
        "·蓝方块\n"
        "  已访问的房间。\n\n"
        "·绿色菱形\n"
        "  返回终端的传送门。"
    ),
    61: (
        "返回传送门可瞬间回到\n"
        "本层终端。\n\n"
        "站在传送门上按<icon:011a>键，\n"
        "即可启动。\n\n"
        "锁定敌人时无法使用。\n"
        "若在锁定房内，\n"
        "须先击败所有敌人。\n\n"
        "地图上以绿色菱形表示。"
    ),
    71: (
        "拾取后，所有部位温度\n"
        "恢复正常。\n\n"
        "过热时也有效。"
    ),
    73: (
        "拾取后：\n"
        "·体力全恢复\n"
        "·所有部位温度恢复正常\n"
        "·武器能量全恢复"
    ),
    77: (
        "补给箱分两类：\n"
        "旋转箱含灵药皮肤，\n"
        "彩色箱含恢复道具。\n"
        "破坏后都会掉落内容物。\n\n"
        "箱子颜色表示内容：\n\n"
        "·紫色：完全恢复\n"
        "·黄绿：恢复体力\n"
        "·橙色：恢复能量\n"
        "·浅蓝：冷却\n"
        "·白色：超载\n\n"
        "破坏的补给箱会在\n"
        "楼层移动时重置。"
    ),
    85: (
        "方向键或摇杆同方向连按两次，\n"
        "即可进行闪避。\n\n"
        "闪避中ADAM完全无敌，\n"
        "不会受到敌人攻击伤害。\n\n"
        "被包围或陷入死角时，\n"
        "闪避能有效扭转局面。\n\n"
        "被敌人击倒在地时，\n"
        "ADAM毫无防备。\n"
        "适时闪避可立刻起身。\n\n"
        "不过反复闪避会让腿部过热。\n\n"
        "没有闪避战术，\n"
        "在炼狱中难以生存。"
    ),
    91: (
        "获得灵药皮肤有3种方法：\n\n"
        "1. 击败敌人\n"
        "2. 破坏补给箱\n"
        "3. 回收武器胶囊\n\n"
        "强化能力需要灵药皮肤。\n"
        "回到已清除的低层，\n"
        "是收集灵药皮肤的好办法。\n\n"
        "也可以回收不需要的武器。\n"
        "回收就是把武器胶囊\n"
        "转化为灵药皮肤。\n\n"
        "道具只能在终端回收。\n"
        "从菜单选择ITEM，\n"
        "选择不用的武器并按<icon:0161>键，\n"
        "可显示武器胶囊的回收值。\n"
        "获得的灵药皮肤会加入储备。\n"
        "武器胶囊一旦回收，\n"
        "就无法还原。"
    ),
}
TUTORIAL_TEXT = {
    11: "按<icon:015a>键进入下一房间",
    67: (
        "用4个部位装备的武器攻击：\n\n"
        "<icon:0161>键：头部\n\n"
        "<icon:015f>键：左臂\n\n"
        "<icon:011a>键：右臂\n\n"
        "<icon:013e>键：躯干\n\n"
        "未装备武器时会出拳。"
    ),
    69: (
        "按<icon:01a8>键锁定附近敌人。\n"
        "再次按<icon:01a8>切换目标。\n"
        "同时按<icon:01a8>和<icon:01ae>解除锁定。\n"
        "锁定是战斗的基础，也要学会解除。"
    ),
}
UI_TEXT = {
    200: "按<icon:015a>键。",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply runtime layout fixes to CHS UI/help translator sheets.")
    parser.add_argument("--ui-sheet", type=Path, default=DEFAULT_UI_SHEET)
    parser.add_argument("--help-sheet", type=Path, default=DEFAULT_HELP_SHEET)
    parser.add_argument("--tutorial-sheet", type=Path, default=DEFAULT_TUTORIAL_SHEET)
    parser.add_argument("--help-width", type=int, default=DEFAULT_HELP_WIDTH)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    ui_changed = pad_input_tokens(args.ui_sheet, dry_run=args.dry_run)
    ui_changed += apply_record_overrides(args.ui_sheet, UI_TEXT, dry_run=args.dry_run)
    help_changed = wrap_help_body(args.help_sheet, width=args.help_width, dry_run=args.dry_run)
    tutorial_changed = apply_record_overrides(args.tutorial_sheet, TUTORIAL_TEXT, dry_run=args.dry_run)
    print(f"ui token rows changed: {ui_changed}")
    print(f"help body rows changed: {help_changed}")
    print(f"tutorial rows changed: {tutorial_changed}")
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
        entry["chs_units"] = encoded_units(fixed)
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
        if record in MANUAL_HELP_TEXT:
            wrapped = MANUAL_HELP_TEXT[record]
        elif record in PROSE_LAYOUT_RECORDS:
            wrapped = wrap_manual_prose(draft, DEFAULT_PROSE_WIDTH)
        else:
            wrapped = wrap_text(draft, width)
        if wrapped == draft:
            continue
        if encoded_units(wrapped) > int(entry.get("source_max_units", entry.get("length", len(wrapped)))):
            continue
        entry["chs_draft"] = wrapped
        entry["chs_units"] = encoded_units(wrapped)
        changed += 1
    if changed and not dry_run:
        write_json(path, payload)
    return changed


def apply_record_overrides(path: Path, overrides: dict[int, str], dry_run: bool = False) -> int:
    if not path.exists():
        return 0
    payload = load_json(path)
    changed = 0
    for entry in payload.get("entries", []):
        record = int(entry.get("record", -1))
        if record not in overrides:
            continue
        text = overrides[record]
        field = "chs_draft" if "chs_draft" in entry else "translation"
        if entry.get(field) == text:
            continue
        max_units = int(entry.get("source_max_units", entry.get("length", encoded_units(text))))
        if encoded_units(text) > max_units:
            continue
        entry[field] = text
        if "chs_units" in entry:
            entry["chs_units"] = encoded_units(text)
        changed += 1
    if changed and not dry_run:
        write_json(path, payload)
    return changed


def encoded_units(text: str) -> int:
    return len(INLINE_CODE_RE.sub("X", text))


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


def wrap_manual_prose(text: str, width: int) -> str:
    paragraphs = normalize_manual_paragraphs(text)
    return "\n\n".join(wrap_prose_paragraph(paragraph, width) for paragraph in paragraphs if paragraph)


def normalize_manual_paragraphs(text: str) -> list[str]:
    paragraphs = []
    for paragraph in text.replace("\r\n", "\n").split("\n\n"):
        compact = "".join(line.strip() for line in paragraph.split("\n"))
        compact = restore_manual_ascii_spacing(compact)
        if compact:
            paragraphs.append(compact)
    return paragraphs


def restore_manual_ascii_spacing(text: str) -> str:
    replacements = {
        "MemoryStickPRODuo": "Memory Stick PRO Duo",
        "MemoryStickDuo": "Memory Stick Duo",
        "DeleteSave": "Delete Save",
    }
    for before, after in replacements.items():
        text = text.replace(before, after)
    return text


def wrap_prose_paragraph(paragraph: str, width: int) -> str:
    lines: list[str] = []
    for sentence in split_manual_sentences(paragraph):
        lines.extend(wrap_tokens(tokenize_manual_text(sentence), width))
    return "\n".join(lines)


def split_manual_sentences(text: str) -> list[str]:
    sentences: list[str] = []
    current = ""
    for char in text:
        current += char
        if char in "。；;":
            sentences.append(current)
            current = ""
    if current:
        sentences.append(current)
    return sentences


def tokenize_manual_text(text: str) -> list[str]:
    tokens: list[str] = []
    index = 0
    while index < len(text):
        match = INLINE_CODE_RE.match(text, index)
        if match:
            tokens.append(match.group(0))
            index = match.end()
            continue
        char = text[index]
        if char.isspace():
            tokens.append(" ")
            index += 1
            continue
        if char.isascii() and char not in "，。；：、,.!?:;)]）】([":
            start = index
            while index < len(text) and text[index].isascii() and not text[index].isspace() and text[index] not in "，。；：、,.!?:;)]）】([":
                index += 1
            tokens.append(text[start:index])
            continue
        tokens.append(char)
        index += 1
    return tokens


def wrap_tokens(tokens: list[str], width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for token in tokens:
        if token == " " and not current:
            continue
        token_width = encoded_units(token)
        if current and encoded_units(current) + token_width > width and not token_is_closing_punctuation(token):
            lines.append(current)
            current = "" if token == " " else token
            continue
        current += token
        if token and token[-1] in "。；;":
            lines.append(current)
            current = ""
    if current:
        lines.append(current)
    return lines


def token_is_closing_punctuation(token: str) -> bool:
    return token in "，。；：、,.!?:;)]）】"


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
