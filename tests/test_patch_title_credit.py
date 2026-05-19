from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from patch_title_credit import abgr_to_rgba, rgba_to_abgr


class PatchTitleCreditTests(unittest.TestCase):
    def test_abgr_rgba_roundtrip(self) -> None:
        rgba = bytes(
            (
                0x11,
                0x22,
                0x33,
                0x44,
                0xAA,
                0xBB,
                0xCC,
                0xDD,
            )
        )

        self.assertEqual(abgr_to_rgba(rgba_to_abgr(rgba)), rgba)


if __name__ == "__main__":
    unittest.main()
