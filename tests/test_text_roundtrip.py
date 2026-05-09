from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from extract_text import export_text
from import_text import import_text


class TextRoundTripTests(unittest.TestCase):
    def make_temp_dir(self) -> tempfile.TemporaryDirectory[str]:
        temp_root = ROOT / "tests" / ".tmp"
        temp_root.mkdir(exist_ok=True)
        return tempfile.TemporaryDirectory(dir=temp_root)

    def test_ascii_extract_import_shorter_translation(self) -> None:
        with self.make_temp_dir() as temp_dir:
            temp = Path(temp_dir)
            source = temp / "sample.bin"
            exported = temp / "sample.json"
            output = temp / "patched.bin"

            source.write_bytes(b"\x00\x01HELLO WORLD\x00TAIL\xff")
            entries = export_text(source, exported, min_length=4)

            hello = next(entry for entry in entries if entry["text"] == "HELLO WORLD")
            payload = json.loads(exported.read_text(encoding="utf-8"))
            payload["entries"][hello["id"]]["translation"] = "HI"
            exported.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

            applied = import_text(source, exported, output)

            self.assertEqual(applied, len(entries))
            patched = output.read_bytes()
            self.assertIn(b"HI\x00\x00\x00\x00\x00\x00\x00\x00\x00", patched)
            self.assertEqual(source.read_bytes()[0:2], patched[0:2])
            self.assertNotEqual(source.read_bytes(), patched)

    def test_utf8_extract_import_same_length_translation(self) -> None:
        with self.make_temp_dir() as temp_dir:
            temp = Path(temp_dir)
            source = temp / "sample.bin"
            exported = temp / "sample.json"
            output = temp / "patched.bin"

            source.write_bytes(b"HEAD\x00" + "カナ".encode("utf-8") + b"\x00END")
            entries = export_text(source, exported, min_length=2)

            kana = next(entry for entry in entries if entry["encoding"] == "utf-8" and entry["text"] == "カナ")
            payload = json.loads(exported.read_text(encoding="utf-8"))
            payload["entries"][kana["id"]]["translation"] = "かな"
            exported.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

            import_text(source, exported, output)

            self.assertIn("かな".encode("utf-8"), output.read_bytes())

    def test_import_rejects_longer_translation(self) -> None:
        with self.make_temp_dir() as temp_dir:
            temp = Path(temp_dir)
            source = temp / "sample.bin"
            exported = temp / "sample.json"
            output = temp / "patched.bin"

            source.write_bytes(b"ABCDEF")
            export_text(source, exported, min_length=4)
            payload = json.loads(exported.read_text(encoding="utf-8"))
            payload["entries"][0]["translation"] = "TOO LONG FOR SLOT"
            exported.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

            with self.assertRaises(ValueError):
                import_text(source, exported, output)


if __name__ == "__main__":
    unittest.main()
