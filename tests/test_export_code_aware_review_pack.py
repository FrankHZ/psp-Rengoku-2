from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from export_code_aware_review_pack import normalize_hash_gram_for_review, render_code_aware_jp, review_chs_text


GLYPHS = {
    0x01A8: "Ｌ",
    0x01AE: "Ｒ",
    0x0242: "タ",
    0x025F: "ボ",
    0x0276: "ン",
    0x0283: "L",
    0x0284: "L",
    0x0285: "R",
    0x0286: "R",
    0x0287: "○",
    0x0288: "×",
    0x0289: "△",
    0x028A: "□",
}


class CodeAwareReviewPackTests(unittest.TestCase):
    def test_render_preserves_source_space_codes_and_gram_token(self) -> None:
        codes = [0x0100, *[ord(char) for char in "#GRAM#"], 0x0020, 0x000A]

        self.assertEqual(render_code_aware_jp(codes, GLYPHS), "\u3000#GRAM# \n")

    def test_render_button_icons_as_readable_tokens(self) -> None:
        codes = [0x0283, 0x025F, 0x0242, 0x0276, 0x0020, 0x0285, 0x025F, 0x0242, 0x0276]

        self.assertEqual(render_code_aware_jp(codes, GLYPHS), "<icon:L>ボタン <icon:R>ボタン")

    def test_render_does_not_rewrite_fullwidth_latin_l_without_button_suffix(self) -> None:
        codes = [0x01A8, ord("A"), ord("N")]

        self.assertEqual(render_code_aware_jp(codes, GLYPHS), "ＬAN")

    def test_render_shape_button_icons_as_readable_tokens(self) -> None:
        codes = [0x0287, 0x0288, 0x0289, 0x028A]

        self.assertEqual(render_code_aware_jp(codes, GLYPHS), "<icon:○><icon:×><icon:△><icon:□>")

    def test_normalize_hash_gram_for_review(self) -> None:
        self.assertEqual(normalize_hash_gram_for_review("为让「gram的心复活」"), "为让「#GRAM#的心复活」")

    def test_review_chs_text_uses_equipment_unshrunk_fallback(self) -> None:
        row = {"current_chs": "运行", "chs_unshrunk": "审校", "chs_shrunk": "压缩"}

        self.assertEqual(review_chs_text(row), "审校")
