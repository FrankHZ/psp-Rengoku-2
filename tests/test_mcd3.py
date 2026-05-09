from __future__ import annotations

import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from mcd3 import read_mcd3, selector_to_archive_index
from extract_mcd3_entries import extract_mcd3_entries
from extract_text import export_offset_table_runs
from export_script_table import export_script_table
from import_text import import_text
from replace_mcd3_entry import replace_mcd3_entry
from analyze_font_grid import cell_has_ink, parse_cell_size
from align_reference_text import align_reference_text
from decode_offset_table_text import decode_values
from extract_offset_table_runs import classify_run, decode_ascii_run, parse_record_runs
from export_glyph_cells import crop_rgba, glyph_id_contiguous, glyph_id_page100
from copy_mig_font_cell import copy_font_cell
from font_cell_inventory import inventory_page_cells
from glyph_map import decode_glyph_values, read_glyph_map
from mig import (
    decode_mig_indices,
    decode_palette_color,
    read_mig,
    render_mig_rgba,
    replace_mig_indices,
    swizzle_texture_bytes,
    unswizzle_texture_bytes,
)
from map_runtime_font_pages import map_runtime_pages, parse_dump_address
from patch_mig_font_cell import parse_cell_range, patch_font_cell, patch_font_cells
from png_rgba import read_png_rgba
from search_encoded_text import search_phrase
from stage_font_probe import apply_font_patch, parse_cells
from mscr import read_mscr
from offset_table import read_offset_table
from pack0001 import read_pack0001
from tdl import read_tdl, replace_tdl_child, replace_tdl_children
from translation_char_inventory import collect_translation_chars, is_cjk


class Mcd3Tests(unittest.TestCase):
    def make_temp_dir(self) -> tempfile.TemporaryDirectory[str]:
        temp_root = ROOT / "tests" / ".tmp"
        temp_root.mkdir(exist_ok=True)
        return tempfile.TemporaryDirectory(dir=temp_root)

    def test_selector_to_archive_index(self) -> None:
        self.assertEqual(selector_to_archive_index(0x8000), 0)
        self.assertEqual(selector_to_archive_index(0x18000), 1)
        self.assertEqual(selector_to_archive_index(0x48000), 4)
        self.assertIsNone(selector_to_archive_index(0))
        self.assertIsNone(selector_to_archive_index(0x1234))

    def test_read_mcd3_synthetic_index(self) -> None:
        with self.make_temp_dir() as temp_dir:
            path = Path(temp_dir) / "DATA000.BIN"
            header = struct.pack("<III4s", 0x30, 2, 3, b"MCD3")
            names = b"DATA001.BIN".ljust(16, b"\x00") + b"DATA002.BIN".ljust(16, b"\x00")
            entries = b"".join(
                [
                    struct.pack("<IIII", 0x8000, 10, 0, 10),
                    struct.pack("<IIII", 0, 0, 0, 0),
                    struct.pack("<IIII", 0x18000, 20, 32, 20),
                ]
            )
            path.write_bytes(header + names + entries)

            index = read_mcd3(path)

            self.assertEqual(index.header_size, 0x30)
            self.assertEqual(index.archive_count, 2)
            self.assertEqual(index.entry_count, 3)
            self.assertEqual(index.archive_names, ("DATA001.BIN", "DATA002.BIN"))
            self.assertEqual(index.entries[0].archive_name, "DATA001.BIN")
            self.assertTrue(index.entries[1].is_empty)
            self.assertEqual(index.entries[2].archive_index, 1)
            self.assertEqual(index.entries[2].end_offset, 52)

    def test_extract_mcd3_entries_writes_manifest_and_files(self) -> None:
        with self.make_temp_dir() as temp_dir:
            temp = Path(temp_dir)
            index_path = temp / "DATA000.BIN"
            archives_dir = temp / "archives"
            output_dir = temp / "entries"
            archives_dir.mkdir()

            header = struct.pack("<III4s", 0x30, 2, 3, b"MCD3")
            names = b"DATA001.BIN".ljust(16, b"\x00") + b"DATA002.BIN".ljust(16, b"\x00")
            entries = b"".join(
                [
                    struct.pack("<IIII", 0x8000, 8, 0, 8),
                    struct.pack("<IIII", 0, 0, 0, 0),
                    struct.pack("<IIII", 0x18000, 12, 4, 12),
                ]
            )
            index_path.write_bytes(header + names + entries)
            (archives_dir / "DATA001.BIN").write_bytes(b"MSCRabcd")
            (archives_dir / "DATA002.BIN").write_bytes(b"xxxxPACK0001tail")

            manifest = extract_mcd3_entries(index_path, archives_dir, output_dir)

            self.assertEqual(manifest["entry_count"], 2)
            self.assertTrue((output_dir / "manifest.json").exists())
            self.assertEqual((output_dir / "DATA001" / "0000_mscr.bin").read_bytes(), b"MSCRabcd")
            self.assertEqual((output_dir / "DATA002" / "0002_pack0001.bin").read_bytes(), b"PACK0001tail")

    def test_replace_mcd3_entry_writes_archive_copy(self) -> None:
        with self.make_temp_dir() as temp_dir:
            temp = Path(temp_dir)
            index_path = temp / "DATA000.BIN"
            archives_dir = temp / "archives"
            output_path = temp / "DATA001_patched.BIN"
            replacement_path = temp / "replacement.bin"
            archives_dir.mkdir()

            header = struct.pack("<III4s", 0x60, 1, 1, b"MCD3")
            names = b"DATA001.BIN".ljust(16, b"\x00")
            entries = struct.pack("<IIII", 0x8000, 4, 2, 4)
            index_path.write_bytes((header + names).ljust(0x60, b"\x00") + entries)
            (archives_dir / "DATA001.BIN").write_bytes(b"aaOLD!zz")
            replacement_path.write_bytes(b"NEW!")

            replace_mcd3_entry(index_path, archives_dir, 0, replacement_path, output_path)

            self.assertEqual(output_path.read_bytes(), b"aaNEW!zz")
            self.assertEqual((archives_dir / "DATA001.BIN").read_bytes(), b"aaOLD!zz")

    def test_read_tdl_synthetic_container(self) -> None:
        with self.make_temp_dir() as temp_dir:
            path = Path(temp_dir) / "sample.tdl"
            header = struct.pack("<4sIII", b".TDL", 2, 8, 0)
            rows = b"".join(
                [
                    b"font_a".ljust(16, b"\x00") + struct.pack("<II", 4, 0x40),
                    b"font_b".ljust(16, b"\x00") + struct.pack("<II", 4, 0x44),
                ]
            )
            path.write_bytes((header + rows).ljust(0x40, b"\x00") + b"AAAABBBB")

            tdl = read_tdl(path)

            self.assertEqual(tdl.entry_count, 2)
            self.assertEqual(tdl.entries[0].name, "font_a")
            self.assertEqual(tdl.entries[0].offset, 0x40)
            self.assertEqual(tdl.entries[1].end_offset, 0x48)

    def test_replace_tdl_child_writes_container_copy(self) -> None:
        with self.make_temp_dir() as temp_dir:
            temp = Path(temp_dir)
            source = temp / "sample.tdl"
            replacement = temp / "replacement.bin"
            output = temp / "patched.tdl"
            header = struct.pack("<4sIII", b".TDL", 2, 8, 0)
            rows = b"".join(
                [
                    b"font_a".ljust(16, b"\x00") + struct.pack("<II", 4, 0x40),
                    b"font_b".ljust(16, b"\x00") + struct.pack("<II", 4, 0x44),
                ]
            )
            source.write_bytes((header + rows).ljust(0x40, b"\x00") + b"AAAABBBB")
            replacement.write_bytes(b"CCCC")

            replace_tdl_child(source, 1, replacement, output)

            self.assertEqual(output.read_bytes()[-8:], b"AAAACCCC")
            self.assertEqual(source.read_bytes()[-8:], b"AAAABBBB")

    def test_replace_tdl_children_writes_multiple_children(self) -> None:
        with self.make_temp_dir() as temp_dir:
            temp = Path(temp_dir)
            source = temp / "sample.tdl"
            first = temp / "first.bin"
            second = temp / "second.bin"
            output = temp / "patched.tdl"
            header = struct.pack("<4sIII", b".TDL", 2, 8, 0)
            rows = b"".join(
                [
                    b"font_a".ljust(16, b"\x00") + struct.pack("<II", 4, 0x40),
                    b"font_b".ljust(16, b"\x00") + struct.pack("<II", 4, 0x44),
                ]
            )
            source.write_bytes((header + rows).ljust(0x40, b"\x00") + b"AAAABBBB")
            first.write_bytes(b"1111")
            second.write_bytes(b"2222")

            replace_tdl_children(source, {0: first, 1: second}, output)

            self.assertEqual(output.read_bytes()[-8:], b"11112222")

    def test_read_pack0001_synthetic_container(self) -> None:
        with self.make_temp_dir() as temp_dir:
            path = Path(temp_dir) / "sample.pack"
            header = struct.pack("<8sII", b"PACK0001", 2, 0x20) + b"\x00" * 16
            rows = b"".join(
                [
                    struct.pack("<IIII", 0x40, 0, 4, 0),
                    struct.pack("<IIII", 0x44, 0, 4, 0),
                ]
            )
            path.write_bytes(header + rows + b"AAAABBBB")

            pack = read_pack0001(path)

            self.assertEqual(pack.entry_count, 2)
            self.assertEqual(pack.table_offset, 0x20)
            self.assertEqual(pack.entries[0].offset, 0x40)
            self.assertEqual(pack.entries[1].end_offset, 0x48)

    def test_read_mig_synthetic_font_texture_shape(self) -> None:
        with self.make_temp_dir() as temp_dir:
            path = Path(temp_dir) / "font.mig"
            data = bytearray(0x2110)
            data[0:11] = b"MIG.00.1PSP"
            struct.pack_into("<IIII", data, 0x10, 2, 0x2100, 0x10, 0x10)
            struct.pack_into("<IIII", data, 0x20, 3, 0x20F0, 0x10, 0x10)
            struct.pack_into("<IIII", data, 0x30, 5, 0x90, 0x90, 0x10)
            struct.pack_into("<HH", data, 0xD8, 128, 128)
            path.write_bytes(data)

            mig = read_mig(path)

            self.assertEqual(mig.width, 128)
            self.assertEqual(mig.height, 128)
            self.assertEqual(mig.bits_per_pixel, 4)
            self.assertEqual(mig.palette_offset, 0x80)
            self.assertEqual(mig.pixel_offset, 0x110)
            self.assertEqual(mig.pixel_size, 8192)

            width, height, rgba = render_mig_rgba(path)

            self.assertEqual((width, height), (128, 128))
            self.assertEqual(len(rgba), 128 * 128 * 4)

    def test_decode_palette_color_modes(self) -> None:
        color = bytes([1, 2, 3, 4])
        self.assertEqual(decode_palette_color(color, "rgba"), (1, 2, 3, 4))
        self.assertEqual(decode_palette_color(color, "abgr"), (4, 3, 2, 1))
        self.assertEqual(decode_palette_color(color, "bgra"), (3, 2, 1, 4))

    def test_decode_mig_indices_expands_4bpp_nibbles(self) -> None:
        with self.make_temp_dir() as temp_dir:
            path = Path(temp_dir) / "font.mig"
            data = bytearray(0x2110)
            data[0:11] = b"MIG.00.1PSP"
            struct.pack_into("<HH", data, 0xD8, 128, 128)
            data[0x110] = 0x21
            path.write_bytes(data)

            width, height, indices = decode_mig_indices(path)

            self.assertEqual((width, height), (128, 128))
            self.assertEqual(indices[:2], bytes([1, 2]))

    def test_swizzle_texture_bytes_round_trips_linear_data(self) -> None:
        linear = bytes(index % 256 for index in range(64 * 16))
        swizzled = swizzle_texture_bytes(linear, width_bytes=64, height=16)

        self.assertEqual(unswizzle_texture_bytes(swizzled, width_bytes=64, height=16), linear)

    def test_replace_mig_indices_preserves_shape_and_updates_pixels(self) -> None:
        with self.make_temp_dir() as temp_dir:
            temp = Path(temp_dir)
            source = temp / "0001_codeJAP14x14_00_.bin"
            output = temp / "patched.bin"
            data = bytearray(0x2110)
            data[0:11] = b"MIG.00.1PSP"
            struct.pack_into("<HH", data, 0xD8, 128, 128)
            source.write_bytes(data)

            indices = bytearray(128 * 128)
            indices[0] = 7
            indices[127 * 128 + 127] = 9
            replace_mig_indices(source, bytes(indices), output)

            self.assertEqual(source.read_bytes()[:0x110], output.read_bytes()[:0x110])
            self.assertEqual(decode_mig_indices(output), (128, 128, bytes(indices)))

    def test_patch_font_cell_writes_pattern_to_requested_cell(self) -> None:
        with self.make_temp_dir() as temp_dir:
            temp = Path(temp_dir)
            source = temp / "0001_codeJAP14x14_00_.bin"
            output = temp / "patched.bin"
            data = bytearray(0x2110)
            data[0:11] = b"MIG.00.1PSP"
            struct.pack_into("<HH", data, 0xD8, 128, 128)
            source.write_bytes(data)

            patch_font_cell(source, output, cell_index=10, pattern="box", ink_index=12)
            _, _, indices = decode_mig_indices(output)

            self.assertFalse(cell_has_ink(indices, image_width=128, x=0, y=0, width=14, height=14))
            self.assertTrue(cell_has_ink(indices, image_width=128, x=14, y=14, width=14, height=14))
            self.assertEqual(indices[(14 + 1) * 128 + 14 + 1], 12)

    def test_patch_font_cells_writes_multiple_requested_cells(self) -> None:
        with self.make_temp_dir() as temp_dir:
            temp = Path(temp_dir)
            source = temp / "0001_codeJAP14x14_00_.bin"
            output = temp / "patched.bin"
            data = bytearray(0x2110)
            data[0:11] = b"MIG.00.1PSP"
            struct.pack_into("<HH", data, 0xD8, 128, 128)
            source.write_bytes(data)

            patch_font_cells(source, output, cell_indices=[0, 80], pattern="cross", ink_index=8)
            _, _, indices = decode_mig_indices(output)

            self.assertTrue(cell_has_ink(indices, image_width=128, x=0, y=0, width=14, height=14))
            self.assertTrue(cell_has_ink(indices, image_width=128, x=112, y=112, width=14, height=14))
            self.assertFalse(cell_has_ink(indices, image_width=128, x=14, y=0, width=14, height=14))

    def test_parse_cell_range_accepts_lists_and_ranges(self) -> None:
        self.assertEqual(parse_cell_range("0-2,5 7"), [0, 1, 2, 5, 7])

    def test_stage_font_probe_parse_cells(self) -> None:
        self.assertEqual(parse_cells({"target_cell": 65}), [65])
        self.assertEqual(parse_cells({"target_cells": "61-63,65"}), [61, 62, 63, 65])

    def test_stage_font_probe_apply_font_patch_box_mode(self) -> None:
        with self.make_temp_dir() as temp_dir:
            temp = Path(temp_dir)
            target = temp / "0001_codeJAP14x14_00_.bin"
            output = temp / "patched.bin"
            data = bytearray(0x2110)
            data[0:11] = b"MIG.00.1PSP"
            struct.pack_into("<HH", data, 0xD8, 128, 128)
            target.write_bytes(data)

            apply_font_patch({"mode": "box", "target_cell": 3}, target, output)

            _, _, indices = decode_mig_indices(output)
            self.assertTrue(cell_has_ink(indices, image_width=128, x=42, y=0, width=14, height=14))

    def test_copy_font_cell_between_pages(self) -> None:
        with self.make_temp_dir() as temp_dir:
            temp = Path(temp_dir)
            source = temp / "0001_codeJAP14x14_00_.bin"
            target = temp / "0002_codeJAP14x14_02_.bin"
            output = temp / "patched.bin"
            data = bytearray(0x2110)
            data[0:11] = b"MIG.00.1PSP"
            struct.pack_into("<HH", data, 0xD8, 128, 128)
            source_indices = bytearray(128 * 128)
            source_indices[(14 + 1) * 128 + 14 + 1] = 9
            source.write_bytes(data)
            replace_mig_indices(source, bytes(source_indices), source)
            target.write_bytes(data)

            copy_font_cell(source, 10, target, 20, output)
            _, _, copied = decode_mig_indices(output)

            self.assertEqual(copied[(28 + 1) * 128 + 28 + 1], 9)
            self.assertFalse(cell_has_ink(copied, image_width=128, x=14, y=14, width=14, height=14))

    def test_write_and_read_png_rgba(self) -> None:
        from mig import write_png_rgba

        with self.make_temp_dir() as temp_dir:
            path = Path(temp_dir) / "image.png"
            rgba = bytes([255, 0, 0, 255, 0, 255, 0, 255])
            write_png_rgba(path, 2, 1, rgba)

            self.assertEqual(read_png_rgba(path), (2, 1, rgba))

    def test_map_runtime_font_pages_by_address_stride(self) -> None:
        from mig import write_png_rgba

        with self.make_temp_dir() as temp_dir:
            temp = Path(temp_dir)
            runtime_dir = temp / "runtime"
            static_dir = temp / "static"
            runtime_dir.mkdir()
            static_dir.mkdir()
            rgba = bytes([0, 0, 0, 0])

            write_png_rgba(runtime_dir / "040dc200aaaaaaaaaaaaaaaa.png", 1, 1, rgba)
            write_png_rgba(runtime_dir / "040de300bbbbbbbbbbbbbbbb.png", 1, 1, rgba)
            write_png_rgba(static_dir / "0000_codeANK9x14_00_0.png", 1, 1, rgba)
            write_png_rgba(static_dir / "0001_codeJAP14x14_00_.png", 1, 1, rgba)

            rows = map_runtime_pages(runtime_dir, static_dir)

            self.assertEqual(rows[0]["page_index"], 0)
            self.assertEqual(rows[0]["static_page"], "0000_codeANK9x14_00_0.png")
            self.assertEqual(rows[1]["page_index"], 1)
            self.assertEqual(rows[1]["static_page"], "0001_codeJAP14x14_00_.png")

    def test_parse_dump_address_requires_hex_prefix(self) -> None:
        self.assertEqual(parse_dump_address(Path("040e8800676a3b4eaa72713b.png")), 0x040E8800)
        with self.assertRaises(ValueError):
            parse_dump_address(Path("texture.png"))

    def test_parse_cell_size_from_font_name(self) -> None:
        self.assertEqual(parse_cell_size("0000_codeANK9x14_00_0"), (9, 14))
        self.assertEqual(parse_cell_size("0001_codeJAP14x14_00_"), (14, 14))
        with self.assertRaises(ValueError):
            parse_cell_size("not_a_font")

    def test_cell_has_ink(self) -> None:
        indices = bytes([0, 0, 0, 0, 0, 3, 0, 0])
        self.assertFalse(cell_has_ink(indices, image_width=4, x=0, y=0, width=2, height=1))
        self.assertTrue(cell_has_ink(indices, image_width=4, x=1, y=1, width=2, height=1))

    def test_crop_rgba(self) -> None:
        rgba = bytes(range(4 * 4 * 4))
        cropped = crop_rgba(rgba, image_width=4, x=1, y=1, width=2, height=2)

        self.assertEqual(cropped, rgba[20:28] + rgba[36:44])

    def test_glyph_id_formulas(self) -> None:
        self.assertEqual(glyph_id_contiguous("0000_codeANK9x14_00_0", 0, 5), 5)
        self.assertEqual(glyph_id_contiguous("0006_codeJAP14x14_10_", 6, 16), 0x223)
        self.assertEqual(glyph_id_page100("0006_codeJAP14x14_10_", 6, 16), 0x610)

    def test_font_cell_inventory_marks_empty_and_occupied_cells(self) -> None:
        with self.make_temp_dir() as temp_dir:
            path = Path(temp_dir) / "0000_codeANK9x14_00_0.bin"
            data = bytearray(0x2110)
            data[0:11] = b"MIG.00.1PSP"
            struct.pack_into("<HH", data, 0xD8, 128, 128)
            data[0x110] = 0x01
            path.write_bytes(data)

            rows = inventory_page_cells(path, page_index=0)

            self.assertEqual(len(rows), 126)
            self.assertTrue(rows[0]["has_ink"])
            self.assertFalse(rows[1]["has_ink"])
            self.assertEqual(rows[0]["glyph_id_contiguous"], "0x0000")

    def test_translation_char_inventory_counts_cjk_chars(self) -> None:
        with self.make_temp_dir() as temp_dir:
            path = Path(temp_dir) / "draft.json"
            path.write_text(
                json.dumps({"entries": [{"chs_translation": "移动 MOVE"}, {"chs_translation": "锁定"}]}),
                encoding="utf-8",
            )

            report = collect_translation_chars([path], ("chs_translation",))

            self.assertTrue(is_cjk("移"))
            self.assertFalse(is_cjk("A"))
            self.assertEqual(report["cjk_unique"], 4)
            self.assertIn("移", report["cjk_chars"])

    def test_search_phrase_finds_encoded_text(self) -> None:
        with self.make_temp_dir() as temp_dir:
            path = Path(temp_dir) / "strings.bin"
            path.write_bytes(b"abc" + "移動".encode("shift_jis") + b"xyz")

            hits = search_phrase([path], "移動", ("utf-8", "shift_jis"))

            self.assertEqual(len(hits), 1)
            self.assertEqual(hits[0]["encoding"], "shift_jis")
            self.assertEqual(hits[0]["offset"], 3)

    def test_read_offset_table(self) -> None:
        with self.make_temp_dir() as temp_dir:
            path = Path(temp_dir) / "table.bin"
            data = struct.pack("<IIII", 0, 2, 0x10, 0x16)
            data += struct.pack("<HHH", 1, 2, 3)
            data += struct.pack("<HH", 4, 5)
            path.write_bytes(data)

            table = read_offset_table(path)

            self.assertEqual(table.count, 2)
            self.assertEqual(table.table_end, 0x10)
            self.assertEqual(table.entries[0].size, 6)
            self.assertEqual(table.entries[0].u16_preview, (1, 2, 3))
            self.assertEqual(table.entries[1].u16_preview, (4, 5))

    def test_decode_offset_table_text_with_seed_map(self) -> None:
        decoded, known = decode_values((0x123, 0, 0x124, 0x000A, 0x999), {0x123: "移", 0x124: "動"})

        self.assertEqual(known, 2)
        self.assertIn("移", decoded)
        self.assertIn("動", decoded)

    def test_read_glyph_map_csv(self) -> None:
        with self.make_temp_dir() as temp_dir:
            path = Path(temp_dir) / "glyphs.csv"
            path.write_text("code,char\n0x0123,移\n", encoding="utf-8")

            self.assertEqual(read_glyph_map(path), {0x123: "移"})

    def test_read_glyph_map_csv_decodes_escaped_newline(self) -> None:
        with self.make_temp_dir() as temp_dir:
            path = Path(temp_dir) / "glyphs.csv"
            path.write_text('code,char\n0x000a,"\\n"\n', encoding="utf-8")

            self.assertEqual(read_glyph_map(path), {0x000A: "\n"})

    def test_decode_glyph_values_uses_known_glyphs_and_ascii(self) -> None:
        decoded, known = decode_glyph_values((0x123, 0, ord("A"), 0x124, 0x999), {0x123: "移", 0x124: "動"})

        self.assertEqual(known, 2)
        self.assertEqual(decoded, "移 A動·")

    def test_parse_single_run_offset_record(self) -> None:
        values = (1, 0, 1, 0, 0xC, 0, 2, 0, 1, 0, 0xC, 0, 3, 0x123, 0x124, 0)

        self.assertEqual(parse_record_runs(values), [(0x123, 0x124)])

    def test_parse_two_run_offset_record_and_decode_ascii(self) -> None:
        values = (
            1,
            0,
            1,
            0,
            0xC,
            0,
            2,
            0,
            2,
            0,
            0x10,
            0,
            0x40,
            0,
            3,
            0x123,
            0x124,
            0,
            3,
            ord("O"),
            ord("K"),
            0,
        )

        runs = parse_record_runs(values)

        self.assertEqual(runs, [(0x123, 0x124), (ord("O"), ord("K"))])
        self.assertEqual(classify_run(runs[1]), "text")
        self.assertEqual(decode_ascii_run(runs[1]), "OK")

    def test_export_offset_table_runs_json(self) -> None:
        with self.make_temp_dir() as temp_dir:
            temp = Path(temp_dir)
            table_path = temp / "table.bin"
            json_path = temp / "table.json"
            record = struct.pack(
                "<" + "H" * 16,
                1,
                0,
                1,
                0,
                0xC,
                0,
                2,
                0,
                1,
                0,
                0xC,
                0,
                3,
                ord("O"),
                ord("K"),
                0,
            )
            table_path.write_bytes(struct.pack("<III", 0, 1, 12) + record)

            entries = export_offset_table_runs(table_path, json_path)

            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["kind"], "text")
            self.assertEqual(entries[0]["text"], "OK")
            self.assertTrue(json_path.exists())

    def test_export_offset_table_runs_json_with_glyph_map(self) -> None:
        with self.make_temp_dir() as temp_dir:
            temp = Path(temp_dir)
            table_path = temp / "table.bin"
            glyph_path = temp / "glyphs.csv"
            json_path = temp / "table.json"
            record = struct.pack(
                "<" + "H" * 16,
                1,
                0,
                1,
                0,
                0xC,
                0,
                2,
                0,
                1,
                0,
                0xC,
                0,
                3,
                0x123,
                0x124,
                0,
            )
            table_path.write_bytes(struct.pack("<III", 0, 1, 12) + record)
            glyph_path.write_text("code,char\n0x0123,移\n0x0124,動\n", encoding="utf-8")

            entries = export_offset_table_runs(table_path, json_path, glyph_path)
            payload = json.loads(json_path.read_text(encoding="utf-8"))

            self.assertEqual(entries[0]["kind"], "glyph_codes")
            self.assertEqual(entries[0]["text"], "移動")
            self.assertEqual(entries[0]["decoded_known"], 2)
            self.assertEqual(payload["entries"][0]["translation"], "")

    def test_import_offset_table_runs_replaces_shorter_ascii_text(self) -> None:
        with self.make_temp_dir() as temp_dir:
            temp = Path(temp_dir)
            table_path = temp / "table.bin"
            json_path = temp / "table.json"
            output_path = temp / "patched.bin"
            record = struct.pack(
                "<" + "H" * 17,
                1,
                0,
                1,
                0,
                0xC,
                0,
                2,
                0,
                1,
                0,
                0xC,
                0,
                5,
                ord("H"),
                ord("E"),
                ord("L"),
                ord("P"),
            ) + struct.pack("<H", 0)
            table_path.write_bytes(struct.pack("<III", 0, 1, 12) + record)
            entries = export_offset_table_runs(table_path, json_path)
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            payload["entries"][0]["translation"] = "TEST"
            json_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

            applied = import_text(table_path, json_path, output_path)
            patched_entries = export_offset_table_runs(output_path, temp / "patched.json")

            self.assertEqual(applied, 1)
            self.assertEqual(entries[0]["text"], "HELP")
            self.assertEqual(patched_entries[0]["text"], "TEST")

    def test_import_offset_table_runs_replaces_explicit_glyph_codes(self) -> None:
        with self.make_temp_dir() as temp_dir:
            temp = Path(temp_dir)
            table_path = temp / "table.bin"
            json_path = temp / "table.json"
            output_path = temp / "patched.bin"
            record = struct.pack(
                "<" + "H" * 16,
                1,
                0,
                1,
                0,
                0xC,
                0,
                2,
                0,
                1,
                0,
                0xC,
                0,
                3,
                0x123,
                0x124,
                0,
            )
            table_path.write_bytes(struct.pack("<III", 0, 1, 12) + record)
            export_offset_table_runs(table_path, json_path)
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            payload["entries"][0]["translation_codes"] = ["0x0124", "0x0123"]
            json_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

            applied = import_text(table_path, json_path, output_path)
            patched_entries = export_offset_table_runs(output_path, temp / "patched.json")

            self.assertEqual(applied, 1)
            self.assertEqual(patched_entries[0]["codes"], ["0x0124", "0x0123"])

    def test_align_reference_text_matches_records_and_checks_budget(self) -> None:
        with self.make_temp_dir() as temp_dir:
            temp = Path(temp_dir)
            source_json = temp / "source.json"
            reference_json = temp / "reference.json"
            output_json = temp / "aligned.json"
            source_json.write_text(
                json.dumps(
                    {
                        "format": "offset-table-runs-v1",
                        "entries": [
                            {"record": 1, "run": 0, "kind": "glyph_codes", "length": 5, "text": ""},
                            {"record": 2, "run": 0, "kind": "glyph_codes", "length": 3, "text": ""},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            reference_json.write_text(
                json.dumps(
                    {
                        "format": "offset-table-runs-v1",
                        "entries": [
                            {
                                "record": 1,
                                "run": 0,
                                "kind": "glyph_codes",
                                "length": 4,
                                "codes": ["0x004f", "0x004b", "0x0020", "0x013e"],
                                "text": "",
                            },
                            {
                                "record": 2,
                                "run": 0,
                                "kind": "text",
                                "length": 4,
                                "codes": [],
                                "text": "TOO!",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )

            rows = align_reference_text(source_json, reference_json, output_json)

            self.assertEqual(rows[0]["reference_text"], "OK [X]")
            self.assertTrue(rows[0]["fits_source_slot"])
            self.assertFalse(rows[1]["fits_source_slot"])
            self.assertTrue(output_json.exists())

    def test_export_script_table_tracks_start_sections_and_commands(self) -> None:
        with self.make_temp_dir() as temp_dir:
            temp = Path(temp_dir)
            table_path = temp / "script.bin"
            json_path = temp / "script.json"

            def record(values: tuple[int, ...]) -> bytes:
                prefix = (1, 0, 1, 0, 0xC, 0, 2, 0, 1, 0, 0xC, 0)
                run = (len(values) + 1, *values, 0)
                return struct.pack("<" + "H" * (len(prefix) + len(run)), *(prefix + run))

            start = record(tuple(ord(ch) for ch in "#start 1F"))
            glyph = record((0x123, 0x124))
            page = record(tuple(ord(ch) for ch in "#page"))
            offsets = (20, 20 + len(start), 20 + len(start) + len(glyph))
            table_path.write_bytes(struct.pack("<IIIII", 0, 3, *offsets) + start + glyph + page)

            entries = export_script_table(table_path, json_path, None)

            self.assertEqual(entries[0]["role"], "command")
            self.assertEqual(entries[0]["text"], "#start 1F")
            self.assertEqual(entries[1]["section"], "#start 1F")
            self.assertEqual(entries[1]["role"], "glyph")
            self.assertEqual(entries[2]["role"], "command")
            self.assertTrue(json_path.exists())

    def test_unswizzle_texture_bytes(self) -> None:
        width_bytes = 16
        height = 8
        linear = bytes(range(width_bytes * height))
        self.assertEqual(unswizzle_texture_bytes(linear, width_bytes, height), linear)

    def test_read_mscr_with_embedded_tdl(self) -> None:
        with self.make_temp_dir() as temp_dir:
            path = Path(temp_dir) / "sample.mscr"
            mscr_header = struct.pack("<4sIIIIIII", b"MSCR", 0, 0x80, 1, 2, 0x10, 0, 0)
            section_stub = struct.pack("<IIII", 1, 0x50, 0, 0)
            tdl_header = struct.pack("<4sIII", b".TDL", 1, 4, 0)
            tdl_row = b"asset".ljust(16, b"\x00") + struct.pack("<II", 4, 0x28)
            path.write_bytes(mscr_header + section_stub + tdl_header + tdl_row + b"DATA")

            mscr = read_mscr(path)

            self.assertEqual(mscr.declared_size, 0x80)
            self.assertEqual(mscr.section_count, 1)
            self.assertIsNotNone(mscr.embedded_tdl)
            self.assertEqual(mscr.embedded_tdl.entries[0].name, "asset")


if __name__ == "__main__":
    unittest.main()
