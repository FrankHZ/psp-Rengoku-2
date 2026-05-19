from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from patch_eboot_runtime_strings import PATCHES, apply_runtime_string_patches


class PatchEbootRuntimeStringsTests(unittest.TestCase):
    def test_patches_strings_in_place(self) -> None:
        size = max(patch.offset + len(patch.old.encode(patch.encoding)) + 4 for patch in PATCHES)
        data = bytearray(b"\x00" * size)
        for patch in PATCHES:
            old = patch.old.encode(patch.encoding)
            terminator = b"\x00\x00" if patch.encoding == "utf-16le" else b"\x00"
            data[patch.offset : patch.offset + len(old)] = old
            data[patch.offset + len(old) : patch.offset + len(old) + len(terminator)] = terminator

        changes = apply_runtime_string_patches(data)

        self.assertEqual(len(changes), len(PATCHES))
        for patch in PATCHES:
            new = patch.new.encode(patch.encoding)
            self.assertEqual(data[patch.offset : patch.offset + len(new)], new)

    def test_rejects_unexpected_source_bytes(self) -> None:
        size = max(patch.offset + len(patch.old.encode(patch.encoding)) + 4 for patch in PATCHES)
        data = bytearray(b"\x00" * size)

        with self.assertRaises(ValueError):
            apply_runtime_string_patches(data)


if __name__ == "__main__":
    unittest.main()
