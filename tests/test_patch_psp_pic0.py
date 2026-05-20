from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from PIL import Image

from patch_psp_pic0 import PIC0_RELATIVE_PATH, patch_pic0, validate_pic0_replacement


class PatchPspPic0Tests(unittest.TestCase):
    def test_patch_pic0_writes_valid_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / PIC0_RELATIVE_PATH
            target.parent.mkdir(parents=True)
            Image.new("RGBA", (310, 180), (0, 0, 0, 255)).save(target)
            replacement = root / "replacement.png"
            Image.new("RGBA", (310, 180), (10, 20, 30, 255)).save(replacement)

            patch_pic0(root, replacement)

            self.assertEqual(target.read_bytes(), replacement.read_bytes())
            with Image.open(target) as image:
                self.assertEqual(image.size, (310, 180))
                self.assertEqual(image.convert("RGBA").getpixel((0, 0)), (10, 20, 30, 255))

    def test_rejects_wrong_dimensions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "wrong.png"
            Image.new("RGBA", (319, 180), (0, 0, 0, 255)).save(path)

            with self.assertRaisesRegex(ValueError, "320x180"):
                validate_pic0_replacement(path, (320, 180))


if __name__ == "__main__":
    unittest.main()
