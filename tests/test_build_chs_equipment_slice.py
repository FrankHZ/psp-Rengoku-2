from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from build_chs_offset_table import (
    apply_translation_codes,
    build_offset_table_payload,
    infer_source_entry,
    infer_source_export,
    load_translator_sheet,
    parse_table_id,
)
from build_chs_tutorial import assign_chars


class BuildChsEquipmentSliceTests(unittest.TestCase):
    def make_temp_dir(self) -> tempfile.TemporaryDirectory[str]:
        temp_root = ROOT / "tests" / ".tmp"
        temp_root.mkdir(exist_ok=True)
        return tempfile.TemporaryDirectory(dir=temp_root)

    def test_load_translator_sheet_accepts_equipment_rows(self) -> None:
        with self.make_temp_dir() as temp_dir:
            path = Path(temp_dir) / "sheet.json"
            path.write_text(
                json.dumps(
                    [
                        {"table": "DATA001/0015", "record": 71, "run": 0, "chs_draft": "C-K.O.D"},
                        {"table": "DATA001/0015", "record": 71, "run": 1, "chs_draft": ""},
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            rows = load_translator_sheet(path, table="DATA001/0015")

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["record"], 71)
            self.assertEqual(rows[0]["chs_translation"], "C-K.O.D")

    def test_equipment_payload_generates_exact_runtime_codes(self) -> None:
        rows = [{"record": 71, "run": 0, "chs_translation": "移动方式", "source_max_units": 4}]
        source_by_record = {
            (71, 0): {
                "record": 71,
                "run": 0,
                "length": 4,
                "entry_offset": 123,
                "codes": ["0x019f", "0x013c", "0x01a7", "0x0105"],
            }
        }

        payload = build_offset_table_payload(
            rows,
            source_by_record,
            source="local/work/mcd3_entries/DATA001/0015_bin.bin",
            table="DATA001/0015",
        )
        apply_translation_codes(payload["entries"], assign_chars(rows))

        self.assertEqual(payload["source"], "local/work/mcd3_entries/DATA001/0015_bin.bin")
        self.assertEqual(payload["entries"][0]["translation_codes"], ["0x0465", "0x033f", "0x042e", "0x05ca"])

    def test_equipment_payload_rejects_budget_mismatch(self) -> None:
        rows = [{"record": 71, "run": 0, "chs_translation": "C-K.O.D", "source_max_units": 7}]
        source_by_record = {(71, 0): {"record": 71, "run": 0, "length": 6}}

        with self.assertRaisesRegex(ValueError, "sheet budget"):
            build_offset_table_payload(
                rows,
                source_by_record,
                source="local/work/mcd3_entries/DATA001/0015_bin.bin",
                table="DATA001/0015",
            )

    def test_table_helpers_support_other_data001_entries(self) -> None:
        table = parse_table_id("DATA001/0016")

        self.assertEqual(table, ("DATA001", 16))
        self.assertEqual(infer_source_export(table), Path("local/work/extract_text_DATA001_0016_seeded.json"))
        self.assertEqual(infer_source_entry(table), Path("local/work/mcd3_entries/DATA001/0016_bin.bin"))


if __name__ == "__main__":
    unittest.main()
