from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from make_chs_name_input_sheet import make_name_input_sheet
from make_equipment_name_english_variant import actual_ascii_name, make_equipment_name_english_variant
from format_chs_manual_layout import MANUAL_HELP_TEXT, PROSE_LAYOUT_RECORDS, encoded_units, wrap_manual_prose
from report_chs_coverage import read_build_keys, summarize_rows
from build_chs_tutorial import RESERVED_SOURCE_ICON_CELLS, assign_chars, encode_translation, visible_translation_chars


class ChsVariantToolTests(unittest.TestCase):
    def make_temp_dir(self) -> tempfile.TemporaryDirectory[str]:
        temp_root = ROOT / "tests" / ".tmp"
        temp_root.mkdir(exist_ok=True)
        return tempfile.TemporaryDirectory(dir=temp_root)

    def test_actual_ascii_name_only_uses_real_name_when_it_fits(self) -> None:
        self.assertEqual(actual_ascii_name("Heat Axe", 7), "HEATAXE")
        self.assertEqual(actual_ascii_name("Double Claw", 6), "")

    def test_equipment_name_variant_keeps_chs_when_english_does_not_fit(self) -> None:
        with self.make_temp_dir() as temp_dir:
            path = Path(temp_dir) / "equipment.json"
            path.write_text(
                json.dumps(
                    {
                        "entries": [
                            {
                                "record": 4,
                                "run": 0,
                                "role": "name",
                                "source_max_units": 6,
                                "usa_kind": "text",
                                "usa_text": "Double Claw",
                                "chs_draft": "双爪",
                            },
                            {
                                "record": 4,
                                "run": 1,
                                "role": "description_or_stats",
                                "source_max_units": 20,
                                "chs_draft": "近战武器",
                            },
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            payload, summary = make_equipment_name_english_variant(path)

            self.assertEqual(payload["entries"][0]["chs_draft"], "双爪")
            self.assertEqual(payload["entries"][1]["chs_draft"], "近战武器")
            self.assertEqual(summary["assigned_chars_saved"], 0)

    def test_name_input_sheet_uses_confirm_records(self) -> None:
        with self.make_temp_dir() as temp_dir:
            path = Path(temp_dir) / "0065.json"
            path.write_text(
                json.dumps(
                    {
                        "entries": [
                            {"record": 82, "run": 0, "length": 13, "kind": "glyph_codes", "codes": []},
                            {"record": 83, "run": 0, "length": 2, "kind": "glyph_codes", "codes": []},
                            {"record": 84, "run": 0, "length": 3, "kind": "glyph_codes", "codes": []},
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            payload = make_name_input_sheet(path)

            self.assertEqual([row["record"] for row in payload["entries"]], [82, 83, 84])
            self.assertEqual(payload["entries"][0]["chs_draft"], "用此名吗？")

    def test_manual_layout_overrides_stay_within_source_budgets(self) -> None:
        path = ROOT / "local" / "work" / "ui_help_chs_v1" / "DATA001_0017_help_sheet.json"
        if not path.exists():
            self.skipTest("local help sheet is not available")
        payload = json.loads(path.read_text(encoding="utf-8"))
        budgets = {int(entry["record"]): int(entry["source_max_units"]) for entry in payload["entries"]}

        for record, text in MANUAL_HELP_TEXT.items():
            with self.subTest(record=record):
                self.assertLessEqual(encoded_units(text), budgets[record])

    def test_manual_prose_wrapper_keeps_ascii_words_intact(self) -> None:
        wrapped = wrap_manual_prose("保存到Memory Stick Duo。选择Delete Save删除。", width=16)

        self.assertIn("Memory Stick", wrapped)
        self.assertIn("Duo。", wrapped)
        self.assertIn("Delete Save删除。", wrapped)
        self.assertNotIn("Sti\nck", wrapped)
        self.assertNotIn("MemoryStick", wrapped)

    def test_flagged_prose_records_have_short_lines(self) -> None:
        path = ROOT / "local" / "work" / "ui_help_chs_v1" / "DATA001_0017_help_sheet.json"
        if not path.exists():
            self.skipTest("local help sheet is not available")
        payload = json.loads(path.read_text(encoding="utf-8"))
        by_record = {int(entry["record"]): entry for entry in payload["entries"]}

        for record in PROSE_LAYOUT_RECORDS:
            with self.subTest(record=record):
                wrapped = wrap_manual_prose(str(by_record[record]["chs_draft"]), width=16)
                self.assertLessEqual(encoded_units(wrapped), int(by_record[record]["source_max_units"]))
                self.assertTrue(all(encoded_units(line) <= 22 for line in wrapped.splitlines() if line))

    def test_inline_icon_tokens_preserve_source_codes(self) -> None:
        text = "<icon:0161>键:头部"
        assignments = {
            "键": {"base": 0x0100, "cell": 1},
            "头": {"base": 0x0100, "cell": 2},
            "部": {"base": 0x0100, "cell": 3},
        }

        self.assertEqual(encode_translation(text, assignments)[0], 0x0161)
        self.assertNotIn("<", visible_translation_chars(text))
        self.assertEqual(encoded_units(text), 5)

    def test_source_icon_cells_are_not_reassigned(self) -> None:
        assignments = assign_chars([{"chs_translation": "".join(chr(0x4E00 + index) for index in range(40))}])

        used_slots = {(int(value["child"]), int(value["cell"])) for value in assignments.values()}
        self.assertFalse(RESERVED_SOURCE_ICON_CELLS & used_slots)

    def test_coverage_report_reads_current_build_keys(self) -> None:
        with self.make_temp_dir() as temp_dir:
            root = Path(temp_dir)
            (root / "DATA001_0017_chs.json").write_text(
                json.dumps(
                    {
                        "table": "DATA001/0017",
                        "entries": [
                            {"record": 16, "run": 0, "chs_draft": "槽位"},
                            {"record": 18, "run": 0, "chs_draft": "技能点"},
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            keys = read_build_keys(root)

            self.assertIn(("DATA001/0017", 16, 0), keys)
            rows = [
                {"v15_status": "current_build"},
                {"v15_status": "local_draft_not_built"},
                {"v15_status": "estimate_only_not_built"},
            ]
            self.assertEqual(summarize_rows(rows)["rows_not_in_current_build"], 2)


if __name__ == "__main__":
    unittest.main()
