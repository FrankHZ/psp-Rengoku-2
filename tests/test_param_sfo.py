from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from param_sfo import FORMAT_INT32, FORMAT_UTF8, ParamSfo
from patch_savedata_sfo import apply_rengoku2_chs


def build_sfo(entries: list[tuple[str, int, bytes, int]]) -> bytes:
    header_size = 20
    index_size = 16 * len(entries)
    key_table = bytearray()
    key_offsets: list[int] = []
    for key, _fmt, _value, _max_length in entries:
        key_offsets.append(len(key_table))
        key_table.extend(key.encode("ascii") + b"\x00")
    data_table_offset = header_size + index_size + len(key_table)
    data_table_offset = (data_table_offset + 3) & ~3
    key_table_offset = header_size + index_size
    data_table = bytearray()
    index_rows = bytearray()
    for key_offset, (_key, fmt, value, max_length) in zip(key_offsets, entries):
        data_offset = len(data_table)
        data_table.extend(value)
        data_table.extend(b"\x00" * (max_length - len(value)))
        index_rows.extend(struct.pack("<HHIII", key_offset, fmt, len(value), max_length, data_offset))
    header = struct.pack("<4sIIII", b"\x00PSF", 0x00000101, key_table_offset, data_table_offset, len(entries))
    padding = b"\x00" * (data_table_offset - key_table_offset - len(key_table))
    return header + bytes(index_rows) + bytes(key_table) + padding + bytes(data_table)


class ParamSfoTests(unittest.TestCase):
    def test_reads_utf8_and_int_fields(self) -> None:
        data = build_sfo(
            [
                ("TITLE", FORMAT_UTF8, "煉獄弐".encode("utf-8") + b"\x00", 64),
                ("PARENTAL_LEVEL", FORMAT_INT32, struct.pack("<I", 5), 4),
            ]
        )

        sfo = ParamSfo(data)

        self.assertEqual(sfo.string_value("TITLE"), "煉獄弐")
        self.assertEqual(sfo.value("PARENTAL_LEVEL"), 5)

    def test_sets_utf8_string_without_changing_file_size(self) -> None:
        data = build_sfo([("SAVEDATA_TITLE", FORMAT_UTF8, "1 F プレイ時間  0:00".encode("utf-8") + b"\x00", 64)])
        sfo = ParamSfo(data)

        sfo.set_string("SAVEDATA_TITLE", "1 F 游戏时间  0:00")

        self.assertEqual(len(sfo.to_bytes()), len(data))
        self.assertEqual(sfo.string_value("SAVEDATA_TITLE"), "1 F 游戏时间  0:00")
        self.assertLessEqual(sfo.entries["SAVEDATA_TITLE"].length, sfo.entries["SAVEDATA_TITLE"].max_length)

    def test_rejects_strings_that_exceed_fixed_capacity(self) -> None:
        data = build_sfo([("TITLE", FORMAT_UTF8, b"abc\x00", 8)])
        sfo = ParamSfo(data)

        with self.assertRaises(ValueError):
            sfo.set_string("TITLE", "太长太长太长")

    def test_applies_rengoku2_chs_preset(self) -> None:
        data = build_sfo(
            [
                ("SAVEDATA_TITLE", FORMAT_UTF8, "4 F プレイ時間 292:55".encode("utf-8") + b"\x00", 128),
                (
                    "SAVEDATA_DETAIL",
                    FORMAT_UTF8,
                    "ペテロの門を押し開きし魂共よ。\r\n淑女の許しを得、汝等の罪を浄化せよ。\r\nクリア回数：999 死亡回数：999 撃破数：99999".encode("utf-8")
                    + b"\x00",
                    512,
                ),
                ("TITLE", FORMAT_UTF8, "煉獄弐 The Stairway to H.E.A.V.E.N.".encode("utf-8") + b"\x00", 128),
            ]
        )
        sfo = ParamSfo(data)

        changes = apply_rengoku2_chs(sfo)

        self.assertEqual(set(changes), {"SAVEDATA_TITLE", "SAVEDATA_DETAIL", "TITLE"})
        self.assertEqual(sfo.string_value("SAVEDATA_TITLE"), "4 F 游戏时间 292:55")
        self.assertIn("推开彼得之门", sfo.string_value("SAVEDATA_DETAIL"))
        self.assertIn("通关次数：999", sfo.string_value("SAVEDATA_DETAIL"))
        self.assertEqual(sfo.string_value("TITLE"), "炼狱贰 The Stairway to H.E.A.V.E.N.")


if __name__ == "__main__":
    unittest.main()
