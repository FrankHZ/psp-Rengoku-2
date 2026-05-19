from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from PIL import Image

from patch_title_credit import DEFAULT_CREDIT_TEXT, draw_credit


class PatchTitleCreditTests(unittest.TestCase):
    def test_draw_credit_changes_top_left_only(self) -> None:
        image = Image.new("RGBA", (480, 272), (10, 20, 30, 255))

        draw_credit(image, DEFAULT_CREDIT_TEXT)

        changed = [
            (x, y)
            for y in range(image.height)
            for x in range(image.width)
            if image.getpixel((x, y)) != (10, 20, 30, 255)
        ]
        self.assertTrue(changed)
        self.assertLess(max(x for x, _y in changed), 180)
        self.assertGreaterEqual(min(y for _x, y in changed), 40)
        self.assertLess(max(y for _x, y in changed), 70)


if __name__ == "__main__":
    unittest.main()
