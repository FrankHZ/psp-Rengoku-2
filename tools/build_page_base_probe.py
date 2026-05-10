from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from stage_font_probe import stage_font_probe


DEFAULT_FONT = Path("C:/Windows/Fonts/simsun.ttc")

PAGE_SOURCES = {
    1: ("codeJAP14x14_00_", "local/work/tdl_DATA001_0002/0001_codeJAP14x14_00_.bin"),
    2: ("codeJAP14x14_02_", "local/work/tdl_DATA001_0002/0002_codeJAP14x14_02_.bin"),
    3: ("codeJAP14x14_04_", "local/work/tdl_DATA001_0002/0003_codeJAP14x14_04_.bin"),
    4: ("codeJAP14x14_06_", "local/work/tdl_DATA001_0002/0004_codeJAP14x14_06_.bin"),
    5: ("codeJAP14x14_08_", "local/work/tdl_DATA001_0002/0005_codeJAP14x14_08_.bin"),
    6: ("codeJAP14x14_10_", "local/work/tdl_DATA001_0002/0006_codeJAP14x14_10_.bin"),
    7: ("codeJAP14x14_12_", "local/work/tdl_DATA001_0002/0007_codeJAP14x14_12_.bin"),
    8: ("codeJAP14x14_14_", "local/work/tdl_DATA001_0002/0008_codeJAP14x14_14_.bin"),
    9: ("codeJAP14x14_16_", "local/work/tdl_DATA001_0002/0009_codeJAP14x14_16_.bin"),
    11: ("codeJAP14x14_20_", "local/work/tdl_DATA001_0002/0011_codeJAP14x14_20_.bin"),
}

PROBES_V1 = (
    {
        "id": "punc-0100",
        "label": "0100",
        "code": 0x0100,
        "candidates": (
            {"marker": "A", "child": 1, "cell": 0, "base": 0x0100, "formula": "page100"},
            {"marker": "B", "child": 2, "cell": 49, "base": 0x00CF, "formula": "contiguous"},
        ),
    },
    {
        "id": "punc-0101",
        "label": "0101",
        "code": 0x0101,
        "candidates": (
            {"marker": "C", "child": 1, "cell": 1, "base": 0x0100, "formula": "page100"},
            {"marker": "D", "child": 2, "cell": 50, "base": 0x00CF, "formula": "contiguous"},
        ),
    },
    {
        "id": "long-011b",
        "label": "011B",
        "code": 0x011B,
        "candidates": (
            {"marker": "E", "child": 1, "cell": 27, "base": 0x0100, "formula": "page100"},
            {"marker": "F", "child": 2, "cell": 76, "base": 0x00CF, "formula": "contiguous"},
        ),
    },
    {
        "id": "kana-01fe",
        "label": "01FE",
        "code": 0x01FE,
        "candidates": (
            {"marker": "G", "child": 5, "cell": 60, "base": 0x01C2, "formula": "contiguous"},
        ),
    },
    {
        "id": "kana-01fb",
        "label": "01FB",
        "code": 0x01FB,
        "candidates": (
            {"marker": "H", "child": 5, "cell": 57, "base": 0x01C2, "formula": "contiguous"},
        ),
    },
    {
        "id": "kana-01d4",
        "label": "01D4",
        "code": 0x01D4,
        "candidates": (
            {"marker": "I", "child": 5, "cell": 18, "base": 0x01C2, "formula": "contiguous"},
        ),
    },
    {
        "id": "ambig-021b",
        "label": "021B",
        "code": 0x021B,
        "candidates": (
            {"marker": "J", "child": 2, "cell": 40, "base": 0x01F3, "formula": "observed-overlay"},
            {"marker": "K", "child": 2, "cell": 27, "base": 0x0200, "formula": "page100"},
        ),
    },
    {
        "id": "ambig-0222",
        "label": "0222",
        "code": 0x0222,
        "candidates": (
            {"marker": "L", "child": 6, "cell": 15, "base": 0x0213, "formula": "contiguous"},
            {"marker": "M", "child": 2, "cell": 34, "base": 0x0200, "formula": "page100"},
        ),
    },
    {
        "id": "ambig-023c",
        "label": "023C",
        "code": 0x023C,
        "candidates": (
            {"marker": "N", "child": 3, "cell": 73, "base": 0x01F3, "formula": "observed-overlay"},
            {"marker": "O", "child": 2, "cell": 60, "base": 0x0200, "formula": "page100"},
        ),
    },
    {
        "id": "kana-0276",
        "label": "0276",
        "code": 0x0276,
        "candidates": (
            {"marker": "P", "child": 7, "cell": 18, "base": 0x0264, "formula": "contiguous"},
        ),
    },
    {
        "id": "kana-026e",
        "label": "026E",
        "code": 0x026E,
        "candidates": (
            {"marker": "Q", "child": 7, "cell": 10, "base": 0x0264, "formula": "contiguous"},
        ),
    },
)

PROBES_V2 = (
    {
        "id": "c2-known-kana-01fe",
        "label": "1FE",
        "code": 0x01FE,
        "candidates": ({"marker": "A", "child": 5, "cell": 60, "base": 0x01C2, "formula": "contiguous"},),
    },
    {
        "id": "c2-known-kana-01fb",
        "label": "1FB",
        "code": 0x01FB,
        "candidates": ({"marker": "B", "child": 5, "cell": 57, "base": 0x01C2, "formula": "contiguous"},),
    },
    {
        "id": "c2-known-kana-01d4",
        "label": "1D4",
        "code": 0x01D4,
        "candidates": ({"marker": "C", "child": 5, "cell": 18, "base": 0x01C2, "formula": "contiguous"},),
    },
    {
        "id": "c2-known-kana-01ef",
        "label": "1EF",
        "code": 0x01EF,
        "candidates": ({"marker": "D", "child": 5, "cell": 45, "base": 0x01C2, "formula": "contiguous"},),
    },
    {
        "id": "c2-known-kana-01f6",
        "label": "1F6",
        "code": 0x01F6,
        "candidates": ({"marker": "E", "child": 5, "cell": 52, "base": 0x01C2, "formula": "contiguous"},),
    },
    {
        "id": "punct-0100",
        "label": "100",
        "code": 0x0100,
        "candidates": (
            {"marker": "F", "child": 1, "cell": 0, "base": 0x0100, "formula": "observed-overlay"},
            {"marker": "G", "child": 2, "cell": 49, "base": 0x00CF, "formula": "contiguous"},
        ),
    },
    {
        "id": "punct-0101",
        "label": "101",
        "code": 0x0101,
        "candidates": (
            {"marker": "H", "child": 1, "cell": 1, "base": 0x0100, "formula": "observed-overlay"},
            {"marker": "I", "child": 2, "cell": 50, "base": 0x00CF, "formula": "contiguous"},
        ),
    },
    {
        "id": "punct-0102",
        "label": "102",
        "code": 0x0102,
        "candidates": (
            {"marker": "J", "child": 1, "cell": 2, "base": 0x0100, "formula": "observed-overlay"},
            {"marker": "K", "child": 2, "cell": 51, "base": 0x00CF, "formula": "contiguous"},
        ),
    },
    {
        "id": "punct-011b",
        "label": "11B",
        "code": 0x011B,
        "candidates": (
            {"marker": "L", "child": 1, "cell": 27, "base": 0x0100, "formula": "observed-overlay"},
            {"marker": "M", "child": 2, "cell": 76, "base": 0x00CF, "formula": "contiguous"},
        ),
    },
    {
        "id": "ellipsis-0123",
        "label": "123",
        "code": 0x0123,
        "candidates": (
            {"marker": "N", "child": 3, "cell": 3, "base": 0x0120, "formula": "contiguous"},
            {"marker": "O", "child": 1, "cell": 35, "base": 0x0100, "formula": "observed-overlay"},
        ),
    },
    {
        "id": "c2-unknown-01e7",
        "label": "1E7",
        "code": 0x01E7,
        "candidates": ({"marker": "P", "child": 2, "cell": 69, "base": 0x01A2, "formula": "observed-overlay"},),
    },
    {
        "id": "c2-unknown-01e9",
        "label": "1E9",
        "code": 0x01E9,
        "candidates": ({"marker": "Q", "child": 2, "cell": 71, "base": 0x01A2, "formula": "observed-overlay"},),
    },
    {
        "id": "c2-unknown-01dc",
        "label": "1DC",
        "code": 0x01DC,
        "candidates": ({"marker": "R", "child": 2, "cell": 58, "base": 0x01A2, "formula": "observed-overlay"},),
    },
    {
        "id": "c2-unknown-01e3",
        "label": "1E3",
        "code": 0x01E3,
        "candidates": ({"marker": "S", "child": 2, "cell": 65, "base": 0x01A2, "formula": "observed-overlay"},),
    },
    {
        "id": "c2-unknown-01dd",
        "label": "1DD",
        "code": 0x01DD,
        "candidates": ({"marker": "T", "child": 2, "cell": 59, "base": 0x01A2, "formula": "observed-overlay"},),
    },
)

PROBES_V4 = (
    {
        "id": "r4-contig-019d",
        "label": "19D",
        "code": 0x019D,
        "candidates": ({"marker": "A", "child": 4, "cell": 44, "base": 0x0171, "formula": "contiguous"},),
    },
    {
        "id": "r4-contig-01a0",
        "label": "1A0",
        "code": 0x01A0,
        "candidates": ({"marker": "B", "child": 4, "cell": 47, "base": 0x0171, "formula": "contiguous"},),
    },
    {
        "id": "r4-contig-0194",
        "label": "194",
        "code": 0x0194,
        "candidates": ({"marker": "C", "child": 4, "cell": 35, "base": 0x0171, "formula": "contiguous"},),
    },
    {
        "id": "r4-contig-0196",
        "label": "196",
        "code": 0x0196,
        "candidates": ({"marker": "D", "child": 4, "cell": 37, "base": 0x0171, "formula": "contiguous"},),
    },
    {
        "id": "r4-contig-01a1",
        "label": "1A1",
        "code": 0x01A1,
        "candidates": ({"marker": "E", "child": 4, "cell": 48, "base": 0x0171, "formula": "contiguous"},),
    },
    {
        "id": "h4-page100-0428",
        "label": "428",
        "code": 0x0428,
        "candidates": ({"marker": "F", "child": 4, "cell": 40, "base": 0x0400, "formula": "page100"},),
    },
    {
        "id": "h4-page100-0410",
        "label": "410",
        "code": 0x0410,
        "candidates": ({"marker": "G", "child": 4, "cell": 16, "base": 0x0400, "formula": "page100"},),
    },
    {
        "id": "h4-page100-0411",
        "label": "411",
        "code": 0x0411,
        "candidates": ({"marker": "H", "child": 4, "cell": 17, "base": 0x0400, "formula": "page100"},),
    },
    {
        "id": "h4-page100-0424",
        "label": "424",
        "code": 0x0424,
        "candidates": ({"marker": "I", "child": 4, "cell": 36, "base": 0x0400, "formula": "page100"},),
    },
    {
        "id": "h4-page100-040d",
        "label": "40D",
        "code": 0x040D,
        "candidates": ({"marker": "J", "child": 4, "cell": 13, "base": 0x0400, "formula": "page100"},),
    },
    {
        "id": "h5-page100-052e",
        "label": "52E",
        "code": 0x052E,
        "candidates": ({"marker": "K", "child": 5, "cell": 46, "base": 0x0500, "formula": "page100"},),
    },
    {
        "id": "h5-page100-0530",
        "label": "530",
        "code": 0x0530,
        "candidates": ({"marker": "L", "child": 5, "cell": 48, "base": 0x0500, "formula": "page100"},),
    },
    {
        "id": "h5-page100-0523",
        "label": "523",
        "code": 0x0523,
        "candidates": ({"marker": "M", "child": 5, "cell": 35, "base": 0x0500, "formula": "page100"},),
    },
    {
        "id": "h5-page100-0532",
        "label": "532",
        "code": 0x0532,
        "candidates": ({"marker": "N", "child": 5, "cell": 50, "base": 0x0500, "formula": "page100"},),
    },
    {
        "id": "h5-page100-052a",
        "label": "52A",
        "code": 0x052A,
        "candidates": ({"marker": "O", "child": 5, "cell": 42, "base": 0x0500, "formula": "page100"},),
    },
    {
        "id": "h11-contig-03de",
        "label": "3DE",
        "code": 0x03DE,
        "candidates": ({"marker": "P", "child": 11, "cell": 54, "base": 0x03A8, "formula": "contiguous"},),
    },
    {
        "id": "h11-contig-03f1",
        "label": "3F1",
        "code": 0x03F1,
        "candidates": ({"marker": "Q", "child": 11, "cell": 73, "base": 0x03A8, "formula": "contiguous"},),
    },
    {
        "id": "h11-contig-03e1",
        "label": "3E1",
        "code": 0x03E1,
        "candidates": ({"marker": "R", "child": 11, "cell": 57, "base": 0x03A8, "formula": "contiguous"},),
    },
    {
        "id": "h11-contig-03f2",
        "label": "3F2",
        "code": 0x03F2,
        "candidates": ({"marker": "S", "child": 11, "cell": 74, "base": 0x03A8, "formula": "contiguous"},),
    },
)

PROBES_V5 = (
    {
        "id": "r4-contig-019d",
        "label": "19D",
        "code": 0x019D,
        "candidates": ({"marker": "A", "child": 4, "cell": 44, "base": 0x0171, "formula": "contiguous"},),
    },
    {
        "id": "r4-contig-01a0",
        "label": "1A0",
        "code": 0x01A0,
        "candidates": ({"marker": "B", "child": 4, "cell": 47, "base": 0x0171, "formula": "contiguous"},),
    },
    {
        "id": "r4-contig-0194",
        "label": "194",
        "code": 0x0194,
        "candidates": ({"marker": "C", "child": 4, "cell": 35, "base": 0x0171, "formula": "contiguous"},),
    },
    {
        "id": "r4-contig-0196",
        "label": "196",
        "code": 0x0196,
        "candidates": ({"marker": "D", "child": 4, "cell": 37, "base": 0x0171, "formula": "contiguous"},),
    },
    {
        "id": "r4-contig-01a1",
        "label": "1A1",
        "code": 0x01A1,
        "candidates": ({"marker": "E", "child": 4, "cell": 48, "base": 0x0171, "formula": "contiguous"},),
    },
    {
        "id": "d3-0314",
        "label": "314",
        "code": 0x0314,
        "candidates": (
            {"marker": "F", "child": 9, "cell": 14, "base": 0x0306, "formula": "contiguous"},
            {"marker": "G", "child": 3, "cell": 20, "base": 0x0300, "formula": "page100"},
        ),
    },
    {
        "id": "d3-0311",
        "label": "311",
        "code": 0x0311,
        "candidates": (
            {"marker": "H", "child": 9, "cell": 11, "base": 0x0306, "formula": "contiguous"},
            {"marker": "I", "child": 3, "cell": 17, "base": 0x0300, "formula": "page100"},
        ),
    },
    {
        "id": "d3-0310",
        "label": "310",
        "code": 0x0310,
        "candidates": (
            {"marker": "J", "child": 9, "cell": 10, "base": 0x0306, "formula": "contiguous"},
            {"marker": "K", "child": 3, "cell": 16, "base": 0x0300, "formula": "page100"},
        ),
    },
    {
        "id": "d3-0334",
        "label": "334",
        "code": 0x0334,
        "candidates": (
            {"marker": "L", "child": 9, "cell": 46, "base": 0x0306, "formula": "contiguous"},
            {"marker": "M", "child": 3, "cell": 52, "base": 0x0300, "formula": "page100"},
        ),
    },
    {
        "id": "h5low-0508",
        "label": "508",
        "code": 0x0508,
        "candidates": ({"marker": "N", "child": 5, "cell": 8, "base": 0x0500, "formula": "page100"},),
    },
    {
        "id": "h5low-0502",
        "label": "502",
        "code": 0x0502,
        "candidates": ({"marker": "O", "child": 5, "cell": 2, "base": 0x0500, "formula": "page100"},),
    },
    {
        "id": "h5low-051b",
        "label": "51B",
        "code": 0x051B,
        "candidates": ({"marker": "P", "child": 5, "cell": 27, "base": 0x0500, "formula": "page100"},),
    },
    {
        "id": "h5low-0516",
        "label": "516",
        "code": 0x0516,
        "candidates": ({"marker": "Q", "child": 5, "cell": 22, "base": 0x0500, "formula": "page100"},),
    },
    {
        "id": "h5low-051a",
        "label": "51A",
        "code": 0x051A,
        "candidates": ({"marker": "R", "child": 5, "cell": 26, "base": 0x0500, "formula": "page100"},),
    },
)

PROBES_V6 = (
    {
        "id": "h6-page100-063b",
        "label": "63B",
        "code": 0x063B,
        "candidates": ({"marker": "A", "child": 6, "cell": 59, "base": 0x0600, "formula": "page100"},),
    },
    {
        "id": "h6-page100-062e",
        "label": "62E",
        "code": 0x062E,
        "candidates": ({"marker": "B", "child": 6, "cell": 46, "base": 0x0600, "formula": "page100"},),
    },
    {
        "id": "h6-page100-062c",
        "label": "62C",
        "code": 0x062C,
        "candidates": ({"marker": "C", "child": 6, "cell": 44, "base": 0x0600, "formula": "page100"},),
    },
    {
        "id": "h6-page100-062d",
        "label": "62D",
        "code": 0x062D,
        "candidates": ({"marker": "D", "child": 6, "cell": 45, "base": 0x0600, "formula": "page100"},),
    },
    {
        "id": "h6-page100-063a",
        "label": "63A",
        "code": 0x063A,
        "candidates": ({"marker": "E", "child": 6, "cell": 58, "base": 0x0600, "formula": "page100"},),
    },
    {
        "id": "h7-page100-0712",
        "label": "712",
        "code": 0x0712,
        "candidates": ({"marker": "F", "child": 7, "cell": 18, "base": 0x0700, "formula": "page100"},),
    },
    {
        "id": "h7-page100-072a",
        "label": "72A",
        "code": 0x072A,
        "candidates": ({"marker": "G", "child": 7, "cell": 42, "base": 0x0700, "formula": "page100"},),
    },
    {
        "id": "h7-page100-072e",
        "label": "72E",
        "code": 0x072E,
        "candidates": ({"marker": "H", "child": 7, "cell": 46, "base": 0x0700, "formula": "page100"},),
    },
    {
        "id": "h7-page100-074c",
        "label": "74C",
        "code": 0x074C,
        "candidates": ({"marker": "I", "child": 7, "cell": 76, "base": 0x0700, "formula": "page100"},),
    },
    {
        "id": "h7-page100-0705",
        "label": "705",
        "code": 0x0705,
        "candidates": ({"marker": "J", "child": 7, "cell": 5, "base": 0x0700, "formula": "page100"},),
    },
    {
        "id": "small-contig-02ae",
        "label": "2AE",
        "code": 0x02AE,
        "candidates": ({"marker": "K", "child": 7, "cell": 74, "base": 0x0264, "formula": "contiguous"},),
    },
    {
        "id": "small-contig-02af",
        "label": "2AF",
        "code": 0x02AF,
        "candidates": ({"marker": "L", "child": 7, "cell": 75, "base": 0x0264, "formula": "contiguous"},),
    },
    {
        "id": "small-contig-02ac",
        "label": "2AC",
        "code": 0x02AC,
        "candidates": ({"marker": "M", "child": 7, "cell": 72, "base": 0x0264, "formula": "contiguous"},),
    },
    {
        "id": "small-contig-02ad",
        "label": "2AD",
        "code": 0x02AD,
        "candidates": ({"marker": "N", "child": 7, "cell": 73, "base": 0x0264, "formula": "contiguous"},),
    },
    {"id": "observe-0493", "label": "493", "code": 0x0493, "candidates": ()},
    {"id": "observe-048a", "label": "48A", "code": 0x048A, "candidates": ()},
    {"id": "observe-04a5", "label": "4A5", "code": 0x04A5, "candidates": ()},
    {"id": "observe-049d", "label": "49D", "code": 0x049D, "candidates": ()},
    {"id": "observe-0483", "label": "483", "code": 0x0483, "candidates": ()},
    {"id": "observe-0485", "label": "485", "code": 0x0485, "candidates": ()},
    {"id": "observe-04a6", "label": "4A6", "code": 0x04A6, "candidates": ()},
    {"id": "observe-0496", "label": "496", "code": 0x0496, "candidates": ()},
    {"id": "observe-05ab", "label": "5AB", "code": 0x05AB, "candidates": ()},
    {"id": "observe-0599", "label": "599", "code": 0x0599, "candidates": ()},
)

PROBES_HELP_0017_V1 = (
    {
        "id": "g47b-0493",
        "label": "493",
        "code": 0x0493,
        "candidates": ({"marker": "A", "child": 6, "cell": 24, "base": 0x047B, "formula": "contiguous-gap"},),
    },
    {
        "id": "g47b-048a",
        "label": "48A",
        "code": 0x048A,
        "candidates": ({"marker": "B", "child": 6, "cell": 15, "base": 0x047B, "formula": "contiguous-gap"},),
    },
    {
        "id": "g47b-04a5",
        "label": "4A5",
        "code": 0x04A5,
        "candidates": ({"marker": "C", "child": 6, "cell": 42, "base": 0x047B, "formula": "contiguous-gap"},),
    },
    {
        "id": "g47b-049d",
        "label": "49D",
        "code": 0x049D,
        "candidates": ({"marker": "D", "child": 6, "cell": 34, "base": 0x047B, "formula": "contiguous-gap"},),
    },
    {
        "id": "g47b-0485",
        "label": "485",
        "code": 0x0485,
        "candidates": ({"marker": "E", "child": 6, "cell": 10, "base": 0x047B, "formula": "contiguous-gap"},),
    },
    {
        "id": "g56e-05ab",
        "label": "5AB",
        "code": 0x05AB,
        "candidates": ({"marker": "F", "child": 8, "cell": 61, "base": 0x056E, "formula": "contiguous-gap"},),
    },
    {
        "id": "g56e-05b1",
        "label": "5B1",
        "code": 0x05B1,
        "candidates": ({"marker": "G", "child": 8, "cell": 67, "base": 0x056E, "formula": "contiguous-gap"},),
    },
    {
        "id": "g56e-0599",
        "label": "599",
        "code": 0x0599,
        "candidates": ({"marker": "H", "child": 8, "cell": 43, "base": 0x056E, "formula": "contiguous-gap"},),
    },
    {
        "id": "g56e-0591",
        "label": "591",
        "code": 0x0591,
        "candidates": ({"marker": "I", "child": 8, "cell": 35, "base": 0x056E, "formula": "contiguous-gap"},),
    },
    {
        "id": "g56e-05b0",
        "label": "5B0",
        "code": 0x05B0,
        "candidates": ({"marker": "J", "child": 8, "cell": 66, "base": 0x056E, "formula": "contiguous-gap"},),
    },
    {
        "id": "h6-page100-063b",
        "label": "63B",
        "code": 0x063B,
        "candidates": ({"marker": "K", "child": 6, "cell": 59, "base": 0x0600, "formula": "page100"},),
    },
    {
        "id": "h6-page100-062e",
        "label": "62E",
        "code": 0x062E,
        "candidates": ({"marker": "L", "child": 6, "cell": 46, "base": 0x0600, "formula": "page100"},),
    },
    {
        "id": "h6-page100-062c",
        "label": "62C",
        "code": 0x062C,
        "candidates": ({"marker": "M", "child": 6, "cell": 44, "base": 0x0600, "formula": "page100"},),
    },
    {
        "id": "h6-page100-062d",
        "label": "62D",
        "code": 0x062D,
        "candidates": ({"marker": "N", "child": 6, "cell": 45, "base": 0x0600, "formula": "page100"},),
    },
    {
        "id": "h6-page100-063a",
        "label": "63A",
        "code": 0x063A,
        "candidates": ({"marker": "O", "child": 6, "cell": 58, "base": 0x0600, "formula": "page100"},),
    },
    {
        "id": "h7-page100-0712",
        "label": "712",
        "code": 0x0712,
        "candidates": ({"marker": "P", "child": 7, "cell": 18, "base": 0x0700, "formula": "page100"},),
    },
    {
        "id": "h7-page100-072a",
        "label": "72A",
        "code": 0x072A,
        "candidates": ({"marker": "Q", "child": 7, "cell": 42, "base": 0x0700, "formula": "page100"},),
    },
    {
        "id": "h7-page100-072e",
        "label": "72E",
        "code": 0x072E,
        "candidates": ({"marker": "R", "child": 7, "cell": 46, "base": 0x0700, "formula": "page100"},),
    },
    {
        "id": "h7-page100-074c",
        "label": "74C",
        "code": 0x074C,
        "candidates": ({"marker": "S", "child": 7, "cell": 76, "base": 0x0700, "formula": "page100"},),
    },
    {
        "id": "h7-page100-0705",
        "label": "705",
        "code": 0x0705,
        "candidates": ({"marker": "T", "child": 7, "cell": 5, "base": 0x0700, "formula": "page100"},),
    },
    {
        "id": "small-contig-02ae",
        "label": "2AE",
        "code": 0x02AE,
        "candidates": ({"marker": "U", "child": 7, "cell": 74, "base": 0x0264, "formula": "contiguous"},),
    },
    {
        "id": "small-contig-02af",
        "label": "2AF",
        "code": 0x02AF,
        "candidates": ({"marker": "V", "child": 7, "cell": 75, "base": 0x0264, "formula": "contiguous"},),
    },
    {
        "id": "small-contig-02ac",
        "label": "2AC",
        "code": 0x02AC,
        "candidates": ({"marker": "W", "child": 7, "cell": 72, "base": 0x0264, "formula": "contiguous"},),
    },
    {
        "id": "small-contig-02ad",
        "label": "2AD",
        "code": 0x02AD,
        "candidates": ({"marker": "X", "child": 7, "cell": 73, "base": 0x0264, "formula": "contiguous"},),
    },
)

ROWS_V1 = (
    (10, "BASE PROBE"),
    (11, "LOOK AT BODY ROWS"),
    (67, "B0", PROBES_V1[0:3]),
    (69, "B1", PROBES_V1[3:6]),
    (71, "B2", PROBES_V1[6:]),
)

ROWS_V2 = (
    (10, "BASE PROBE 2"),
    (11, "HIGH VALUE BASES"),
    (67, "C2", PROBES_V2[0:5]),
    (69, "P0", PROBES_V2[5:10]),
    (71, "C3", PROBES_V2[10:]),
)

ROWS_V3 = (
    (10, "BASE PROBE 3"),
    (11, "PUNCT VISIBLE"),
    (67, "C2", PROBES_V2[0:5]),
    (69, "C3", PROBES_V2[10:]),
    (71, "P0", PROBES_V2[5:10]),
)

ROWS_V4 = (
    (10, "BASE PROBE 4"),
    (11, "REMAINING BASES"),
    (65, "R4", PROBES_V4[0:5]),
    (67, "H4", PROBES_V4[5:10]),
    (69, "H5", PROBES_V4[10:15]),
    (71, "H11", PROBES_V4[15:]),
)

ROWS_V5 = (
    (10, "BASE PROBE 5"),
    (11, "R4 PLUS NEXT"),
    (67, "D3", PROBES_V5[5:9]),
    (69, "H5L", PROBES_V5[9:]),
    (71, "R4", PROBES_V5[0:5]),
)

ROWS_V6 = (
    (10, "BASE PROBE 6"),
    (11, "STATIC PLUS OBSERVE"),
    (65, "H6", PROBES_V6[0:5]),
    (67, "H7", PROBES_V6[5:10]),
    (69, "S2", PROBES_V6[10:14]),
    (71, "OBS", PROBES_V6[14:19]),
    (73, "OBS2", PROBES_V6[19:]),
)

ROWS_HELP_0017_V1 = (
    (1, "A", PROBES_HELP_0017_V1[0:1]),
    (2, "B", PROBES_HELP_0017_V1[1:2]),
    (3, "C", PROBES_HELP_0017_V1[2:3]),
    (4, "D", PROBES_HELP_0017_V1[3:4]),
    (5, "E", PROBES_HELP_0017_V1[4:5]),
    (6, "F", PROBES_HELP_0017_V1[5:6]),
    (7, "G", PROBES_HELP_0017_V1[6:7]),
    (8, "H", PROBES_HELP_0017_V1[7:8]),
    (9, "I", PROBES_HELP_0017_V1[8:9]),
    (11, "J", PROBES_HELP_0017_V1[9:10]),
    (12, "P6", PROBES_HELP_0017_V1[10:15]),
    (14, "P7", PROBES_HELP_0017_V1[15:20]),
    (16, "S2", PROBES_HELP_0017_V1[20:]),
)

VARIANTS = {
    "v1": {"probes": PROBES_V1, "rows": ROWS_V1},
    "v2": {"probes": PROBES_V2, "rows": ROWS_V2},
    "v3": {"probes": PROBES_V2, "rows": ROWS_V3},
    "v4": {"probes": PROBES_V4, "rows": ROWS_V4},
    "v5": {"probes": PROBES_V5, "rows": ROWS_V5},
    "v6": {"probes": PROBES_V6, "rows": ROWS_V6},
    "help0017-v1": {
        "probes": PROBES_HELP_0017_V1,
        "rows": ROWS_HELP_0017_V1,
        "entry_id": 17,
        "source_entry": "local/work/mcd3_entries/DATA001/0017_bin.bin",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build one PPSSPP artifact that probes multiple candidate glyph page bases.")
    parser.add_argument("--work-root", type=Path, default=Path("local/work/page_base_probe_v1"))
    parser.add_argument("--output-root", type=Path, default=Path("local/rebuilt/page_base_probe_v1_extracted"))
    parser.add_argument("--variant", choices=sorted(VARIANTS), default="v1")
    parser.add_argument("--font", type=Path, default=DEFAULT_FONT)
    parser.add_argument("--font-index", type=int, default=0)
    parser.add_argument("--font-size", type=int, default=12)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    build_page_base_probe(
        work_root=args.work_root,
        output_root=args.output_root,
        font_path=args.font,
        font_index=args.font_index,
        font_size=args.font_size,
        variant=args.variant,
        overwrite=args.overwrite,
    )
    print(f"staged {args.output_root}")
    return 0


def build_page_base_probe(
    work_root: Path,
    output_root: Path,
    font_path: Path = DEFAULT_FONT,
    font_index: int = 0,
    font_size: int = 12,
    variant: str = "v1",
    overwrite: bool = False,
) -> None:
    variant_config = VARIANTS[variant]
    probes = variant_config["probes"]
    rows = variant_config["rows"]
    entry_id = int(variant_config.get("entry_id", 8))
    source_entry = str(variant_config.get("source_entry", "local/work/mcd3_entries/DATA001/0008_bin.bin"))
    work_root.mkdir(parents=True, exist_ok=True)
    text_payload = build_text_payload(rows)
    text_json = work_root / "DATA001_0008_page_base_probe.json"
    text_json.write_text(json.dumps(text_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    write_probe_manifest(work_root / "probe_manifest.csv", probes)
    write_readme(work_root / "README.md", output_root, rows, variant, entry_id)

    stage_config = {
        "extracted_root": "local/extracted/Rengoku 2",
        "entries_root": "local/work/mcd3_entries",
        "work_root": str(work_root / "stage"),
        "output_root": str(output_root),
        "font_patches": build_font_patches(probes, work_root / "previews", font_path, font_index, font_size),
        "text_patch": {
            "entry_id": entry_id,
            "source_entry": source_entry,
            "json": str(text_json),
        },
        "overwrite": overwrite,
    }
    (work_root / "stage_page_base_probe.json").write_text(
        json.dumps(stage_config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    stage_font_probe(stage_config)


def build_text_payload(rows: tuple[tuple[Any, ...], ...]) -> dict[str, Any]:
    entries = []
    for index, row in enumerate(rows):
        record = int(row[0])
        if len(row) == 2:
            codes = encode_ascii(str(row[1]))
        else:
            codes = encode_probe_line(str(row[1]), row[2])
        entries.append(
            {
                "id": f"page-base-probe-{index:02d}",
                "record": record,
                "run": 0,
                "kind": "glyph_codes",
                "length": max(len(codes), 1),
                "translation": "",
                "translation_codes": [f"0x{code:04x}" for code in codes],
                "notes": "generated by tools/build_page_base_probe.py",
            }
        )
    return {
        "format": "offset-table-runs-v1",
        "source": "local/work/mcd3_entries/DATA001/0008_bin.bin",
        "entries": entries,
    }


def encode_probe_line(prefix: str, probes: tuple[dict[str, Any], ...]) -> list[int]:
    codes = encode_ascii(prefix + " ")
    for probe in probes:
        codes.extend(encode_ascii(str(probe["label"]) + "="))
        codes.append(int(probe["code"]))
        codes.append(ord(" "))
    return codes


def encode_ascii(text: str) -> list[int]:
    return [0x000A if char == "\n" else ord(char) for char in text]


def build_font_patches(
    probes: tuple[dict[str, Any], ...],
    preview_dir: Path,
    font_path: Path,
    font_index: int,
    font_size: int,
) -> list[dict[str, Any]]:
    patches = []
    seen_slots: set[tuple[int, int]] = set()
    for probe in probes:
        for candidate in probe["candidates"]:
            child = int(candidate["child"])
            cell = int(candidate["cell"])
            slot = (child, cell)
            if slot in seen_slots:
                continue
            seen_slots.add(slot)
            source, target_page = PAGE_SOURCES[child]
            marker = str(candidate["marker"])
            patches.append(
                {
                    "mode": "render",
                    "target_page": target_page,
                    "target_child": child,
                    "target_cell": cell,
                    "char": marker,
                    "font": str(font_path),
                    "font_index": font_index,
                    "font_size": font_size,
                    "render_mode": "binary",
                    "threshold": 64,
                    "gray_threshold": 176,
                    "stroke_radius": 0,
                    "preview": str(preview_dir / f"child{child}_cell{cell:02d}_{marker}.png"),
                    "source": source,
                }
            )
    return patches


def write_probe_manifest(path: Path, probes: tuple[dict[str, Any], ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["probe_id", "display_label", "display_code", "marker", "child", "source", "cell", "base", "formula"],
        )
        writer.writeheader()
        for probe in probes:
            for candidate in probe["candidates"]:
                source = PAGE_SOURCES[int(candidate["child"])][0]
                writer.writerow(
                    {
                        "probe_id": probe["id"],
                        "display_label": probe["label"],
                        "display_code": f"0x{int(probe['code']):04x}",
                        "marker": candidate["marker"],
                        "child": candidate["child"],
                        "source": source,
                        "cell": candidate["cell"],
                        "base": f"0x{int(candidate['base']):04x}",
                        "formula": candidate["formula"],
                    }
                )


def write_readme(path: Path, output_root: Path, rows: tuple[tuple[Any, ...], ...], variant: str, entry_id: int = 8) -> None:
    row_lines = []
    for row in rows:
        record = row[0]
        if len(row) == 2:
            row_lines.append(f"- record `{record}`: overlay/body hint line `{row[1]}`")
        else:
            labels = " ".join(f"{probe['label']}=<mark>" for probe in row[2])
            row_lines.append(f"- record `{record}`: `{row[1]} {labels}`")

    target = "overlay/body" if entry_id == 8 else f"DATA001/{entry_id:04d}"
    lines = [
        f"# Page Base Probe {variant}",
        "",
        f"PPSSPP-ready artifact: `{output_root.as_posix()}/`",
        "",
        f"This build patches `{target}` rows so multiple raw",
        "glyph-code bases can be checked in one run. Each displayed code has one or more",
        "candidate font cells patched with marker letters. The marker that appears",
        "in game identifies the active runtime page/cell route for that code.",
        "",
        "Patched rows:",
        "",
        *row_lines,
        "",
        "Read `probe_manifest.csv` to map marker letters back to candidate bases.",
        "",
        "Example interpretation: if `0100=` shows `A`, candidate `child 1 cell 0",
        "base 0x0100` won. If it shows `B`, candidate `child 2 cell 49 base",
        "0x00cf` won.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
