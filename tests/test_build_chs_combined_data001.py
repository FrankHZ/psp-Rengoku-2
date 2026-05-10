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
from build_chs_tutorial import assign_chars, encode_translation


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

    def test_required_assigned_chars_ignores_ascii_and_newlines(self) -> None:
        rows = [{"chs_translation": "C-K.O.D\n移动"}]

        self.assertEqual(required_assigned_chars(rows), {"移", "动"})


if __name__ == "__main__":
    unittest.main()
