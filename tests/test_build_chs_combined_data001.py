from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from build_chs_combined_data001 import load_targets, required_assigned_chars
from build_chs_tutorial import (
    BITPLANE_SLOT_POOLS,
    add_soft_line_breaks,
    apply_source_hard_breaks,
    assign_chars,
    assign_chars_bitplane,
    encode_translation,
    preserved_source_logical_slots,
    reserved_runtime_logical_slots,
)


class BuildChsCombinedData001Tests(unittest.TestCase):
    def make_temp_dir(self) -> tempfile.TemporaryDirectory[str]:
        temp_root = ROOT / "tests" / ".tmp"
        temp_root.mkdir(exist_ok=True)
        return tempfile.TemporaryDirectory(dir=temp_root)

    def test_load_targets_accepts_multiple_data001_tables(self) -> None:
        with self.make_temp_dir() as temp_dir:
            temp_path = Path(temp_dir)
            sheet_0008 = temp_path / "0008.json"
            sheet_0015 = temp_path / "0015.json"
            sheet_0008.write_text(
                json.dumps({"entries": [{"record": 70, "run": 0, "chs_draft": "移动方式"}]}, ensure_ascii=False),
                encoding="utf-8",
            )
            sheet_0015.write_text(
                json.dumps([{"record": 71, "run": 0, "chs_draft": "C-K.O.D"}], ensure_ascii=False),
                encoding="utf-8",
            )

            targets = load_targets((("DATA001/0008", sheet_0008), ("DATA001/0015", sheet_0015)))

            self.assertEqual([target["table"] for target in targets], [("DATA001", 8), ("DATA001", 15)])
            self.assertEqual([len(target["rows"]) for target in targets], [1, 1])

    def test_combined_assignments_are_shared_across_tables(self) -> None:
        rows = [
            {"record": 70, "run": 0, "chs_translation": "移动方式"},
            {"record": 71, "run": 0, "chs_translation": "移动"},
        ]

        assignments = assign_chars(rows)

        self.assertEqual(encode_translation("移动方式", assignments), [0x0465, 0x033F, 0x042E, 0x05CA])
        self.assertEqual(encode_translation("移动", assignments), [0x0465, 0x033F])

    def test_bitplane_assignments_can_share_physical_cells(self) -> None:
        text = "".join(chr(0x4E00 + index) for index in range(90))
        rows = [{"record": 70, "run": 0, "chs_translation": text}]

        assignments = assign_chars_bitplane(rows)
        physical_slots = [(slot["child"], slot["cell"]) for slot in assignments.values()]
        logical_slots = [(slot["child"], slot["cell"], slot["layer"]) for slot in assignments.values()]

        self.assertLess(len(set(physical_slots)), len(set(logical_slots)))
        self.assertEqual(len(set(logical_slots)), 90)

    def test_bitplane_pool_includes_confirmed_child11_high_window(self) -> None:
        self.assertEqual(sum(81 for _ in BITPLANE_SLOT_POOLS), 1782)
        self.assertIn(
            {"child": 11, "source": "codeJAP14x14_20_", "target_page": "local/work/tdl_DATA001_0002/0011_codeJAP14x14_20_.bin", "base": 0x07A5, "layer": "high"},
            BITPLANE_SLOT_POOLS,
        )

    def test_preserved_source_symbols_reserve_their_logical_cells(self) -> None:
        reserved = preserved_source_logical_slots()

        self.assertIn((1, 8, "low"), reserved)  # 0x0108 fullwidth question mark
        self.assertIn((1, 9, "high"), reserved)  # 0x015a white circle

    def test_runtime_reservations_include_icon_physical_layers(self) -> None:
        reserved = reserved_runtime_logical_slots()

        self.assertIn((1, 9, "low"), reserved)
        self.assertIn((1, 9, "high"), reserved)

    def test_required_assigned_chars_ignores_ascii_and_newlines(self) -> None:
        rows = [{"chs_translation": "C-K.O.D\n移动，。！？"}]

        self.assertEqual(required_assigned_chars(rows), {"移", "动"})

    def test_encode_translation_reuses_original_source_punctuation(self) -> None:
        assignments = assign_chars([{"record": 1, "run": 0, "chs_translation": "移动，。"}])

        self.assertEqual(encode_translation("移动，。", assignments), [0x0465, 0x033F, 0x0103, 0x0102])

    def test_encode_translation_rejects_unmapped_non_cjk_symbols(self) -> None:
        assignments = assign_chars([{"record": 1, "run": 0, "chs_translation": "移动"}])

        with self.assertRaises(ValueError):
            encode_translation("移动♪", assignments)

    def test_load_targets_accepts_non_data001_text_sheet(self) -> None:
        with self.make_temp_dir() as temp_dir:
            sheet = Path(temp_dir) / "0065.json"
            sheet.write_text(
                json.dumps({"entries": [{"record": 82, "run": 0, "chs_draft": "用此名吗？"}]}, ensure_ascii=False),
                encoding="utf-8",
            )

            targets = load_targets((("DATA002/0065", sheet),))

            self.assertEqual(targets[0]["table"], ("DATA002", 65))
            self.assertEqual(targets[0]["source_export"], Path("local/work/extract_text_DATA002_0065_seeded.json"))

    def test_source_hard_breaks_are_distributed_when_translation_has_none(self) -> None:
        text = "电磁盾发出沿地脉冲，命中敌人后可短时间麻痹。"
        source_codes = ["0x0377", "0x000a", "0x0377", "0x000a", "0x0102"]

        laid_out = apply_source_hard_breaks(text, source_codes)

        self.assertEqual(laid_out.count("\n"), 2)
        self.assertIn("电磁盾发出沿地脉冲，\n", laid_out)

    def test_source_hard_breaks_accept_star_as_manual_break_marker(self) -> None:
        source_codes = ["0x0377", "0x000a", "0x0102"]

        self.assertEqual(apply_source_hard_breaks("第一行*第二行", source_codes), "第一行\n第二行")

    def test_source_hard_breaks_normalizes_key_hint_token(self) -> None:
        source_codes = ["0x003f", "0x0040", "0x025f"]

        self.assertEqual(apply_source_hard_breaks("_`键:前往", source_codes), "?@键:前往")

    def test_soft_line_breaks_use_remaining_source_break_budget(self) -> None:
        source_codes = ["0x0101"] * 10 + ["0x000a"] + ["0x0101"] * 10 + ["0x000a"] + ["0x0101"] * 10
        text = "第一段已经手动分段。\n第二段特别长需要继续按原文宽度补入软换行。"

        laid_out = add_soft_line_breaks(text, source_codes)

        self.assertEqual(laid_out.count("\n"), 2)
        self.assertIn("第二段特别长需要继续", laid_out)
        self.assertIn("\n按原文宽度补入软换行。", laid_out)


if __name__ == "__main__":
    unittest.main()
