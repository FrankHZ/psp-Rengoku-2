from __future__ import annotations

import unittest
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from render_mig_font_cell import has_pillow, mask_to_indices, render_bmfont_glyph_mask, two_bit_indices_to_preview_rgba

if has_pillow():
    from PIL import Image


class RenderMigFontCellTests(unittest.TestCase):
    def test_grayscale_quantizes_antialias_values(self) -> None:
        self.assertEqual(mask_to_indices(bytes([0, 32, 128, 255]), 15, 0), bytes([0, 2, 8, 15]))

    def test_binary_uses_full_ink_after_threshold(self) -> None:
        self.assertEqual(mask_to_indices(bytes([0, 63, 64, 65, 255]), 15, 64, "binary"), bytes([0, 0, 0, 15, 15]))

    def test_palette3_uses_original_gray_and_white_indices(self) -> None:
        self.assertEqual(
            mask_to_indices(bytes([0, 64, 65, 176, 177, 255]), 15, 64, "palette3", 176),
            bytes([0, 14, 14, 14, 15, 15]),
        )

    def test_rejects_unknown_render_mode(self) -> None:
        with self.assertRaises(ValueError):
            mask_to_indices(bytes([255]), 15, 0, "soft")

    def test_two_bit_preview_uses_visible_four_level_palette(self) -> None:
        self.assertEqual(
            two_bit_indices_to_preview_rgba(bytes([0, 1, 2, 3])),
            bytes(
                [
                    0,
                    0,
                    0,
                    0,
                    176,
                    176,
                    176,
                    255,
                    96,
                    96,
                    96,
                    255,
                    255,
                    255,
                    255,
                    255,
                ]
            ),
        )

    @unittest.skipUnless(has_pillow(), "Pillow is required for BMFont rendering")
    def test_bmfont_renderer_uses_declared_glyph_page(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            Image.new("L", (8, 8), 0).save(root / "font_0.png")
            page_one = Image.new("L", (8, 8), 0)
            page_one.putpixel((2, 3), 255)
            page_one.save(root / "font_1.png")
            (root / "font.fnt").write_text(
                "\n".join(
                    [
                        'info face="test" size=8',
                        "common lineHeight=8 base=7 scaleW=8 scaleH=8 pages=2 packed=0",
                        'page id=0 file="font_0.png"',
                        'page id=1 file="font_1.png"',
                        "chars count=1",
                        "char id=20013 x=0 y=0 width=8 height=8 xoffset=0 yoffset=0 xadvance=8 page=1 chnl=15",
                    ]
                ),
                encoding="utf-8",
            )

            mask = render_bmfont_glyph_mask("中", root / "font.fnt", 8, 8, 0, 0, 8)

        self.assertEqual(mask.getpixel((2, 3)), 255)


if __name__ == "__main__":
    unittest.main()
