from __future__ import annotations

import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from render_mig_font_cell import mask_to_indices


class RenderMigFontCellTests(unittest.TestCase):
    def test_grayscale_quantizes_antialias_values(self) -> None:
        self.assertEqual(mask_to_indices(bytes([0, 32, 128, 255]), 15, 0), bytes([0, 2, 8, 15]))

    def test_binary_uses_full_ink_after_threshold(self) -> None:
        self.assertEqual(mask_to_indices(bytes([0, 63, 64, 65, 255]), 15, 64, "binary"), bytes([0, 0, 0, 15, 15]))

    def test_palette3_uses_original_gray_and_white_indices(self) -> None:
        self.assertEqual(
            mask_to_indices(bytes([0, 64, 65, 176, 177, 255]), 15, 64, "palette3", 176),
            bytes([0, 0, 14, 14, 15, 15]),
        )

    def test_rejects_unknown_render_mode(self) -> None:
        with self.assertRaises(ValueError):
            mask_to_indices(bytes([255]), 15, 0, "soft")


if __name__ == "__main__":
    unittest.main()
