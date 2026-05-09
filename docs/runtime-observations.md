# Runtime Observations

Runtime capture is used only to correlate static assets with what PPSSPP renders. Do not commit dumped textures or screenshots.

## Tutorial Text Capture

Observed in PPSSPP GE debugger:

```text
Texture addr 0: 0x040e8800, w=128
Tex size 0:     128x128
Tex format:     CLUT4
Tex CLUT:       0x089240c0
CLUT format:    ABGR 8888
```

The active texture preview shows Japanese glyphs used to draw tutorial text. This confirms the static `MIG` finding: font/code-page resources are 128x128, 4bpp/paletted glyph textures.

Additional capture in a menu/help screen showed:

```text
Texture addr 0: 0x040ea900, w=128
Tex size 0:     128x128
Tex format:     CLUT4
Tex CLUT:       0x089244c0
CLUT format:    ABGR 8888
```

## Dumped Textures

Local dumped PNGs are under:

```text
local/work/dumped_textures/
```

The dumped filenames include texture addresses. Unique observed addresses:

```text
0x040dc200
0x040de300
0x040e0400
0x040e2500
0x040e4600
0x040e6700
0x040e8800
0x040ea900
0x040eca00
```

Each address is spaced by `0x2100` bytes. The extracted `.TDL` child resources are `0x2110` bytes; their first internal record also contains `0x2100`, which appears to match the runtime spacing.

The dumped files are all 128x128, 8-bit RGBA PNGs exported by PPSSPP.

## UI Text Coverage

GE captures of the equipment/status UI show the same font-atlas mechanism covering visible UI labels such as:

```text
最大耐久力
物理防御
電子防御
素体頭部
素体左腕
素体右腕
素体胸部
素体脚部
```

Relevant runtime atlas pages observed in those captures:

```text
0x040e4600 -> codeJAP14x14_06_
0x040e6700 -> codeJAP14x14_08_
0x040e8800 -> codeJAP14x14_10_
0x040ea900 -> codeJAP14x14_12_
```

These are glyph atlases, not pre-rendered phrase textures. The game draws UI labels by selecting cells from one or more atlas pages.

Exact phrase searches for the UI labels above also miss in UTF-8, Shift-JIS/CP932, and EUC-JP, including shorter substrings such as `防御`, `頭部`, `左腕`, `右腕`, `胸部`, and `脚部`. This further supports a custom encoded text or glyph-index stream.

## Runtime Address Mapping

Use this reproducible report to map dumped PPSSPP texture addresses back to rendered static font pages:

```powershell
.\.venv\Scripts\python.exe tools/map_runtime_font_pages.py local/work/dumped_textures local/work/rendered_mig_pages
```

Current mapping:

| Runtime address | Page | Static page |
| --- | ---: | --- |
| `0x040dc200` | 0 | `0000_codeANK9x14_00_0.png` |
| `0x040de300` | 1 | `0001_codeJAP14x14_00_.png` |
| `0x040e0400` | 2 | `0002_codeJAP14x14_02_.png` |
| `0x040e2500` | 3 | `0003_codeJAP14x14_04_.png` |
| `0x040e4600` | 4 | `0004_codeJAP14x14_06_.png` |
| `0x040e6700` | 5 | `0005_codeJAP14x14_08_.png` |
| `0x040e8800` | 6 | `0006_codeJAP14x14_10_.png` |
| `0x040ea900` | 7 | `0007_codeJAP14x14_12_.png` |
| `0x040eca00` | 8 | `0008_codeJAP14x14_14_.png` |

Some runtime addresses have two dumped PNG variants with different filename hashes. These appear to be different palette/CLUT or render-state variants of the same page. Use address stride for page identity first; pixel comparison is secondary evidence.

## Interpretation

Runtime evidence strongly supports this mapping:

```text
.TDL font page child size: 0x2110 bytes
MIG internal record size/stride value: 0x2100 bytes
Runtime texture address stride: 0x2100 bytes
Runtime texture size: 128x128 CLUT4
Static MIG survey result: 128x128 4bpp paletted texture
```

The observed base address for the captured range is `0x040dc200`. Only 9 of 12 sequential page addresses were captured, so the remaining pages are inferred but not runtime-confirmed yet.

Static export notes:

- `MIG` pixel data is PSP-swizzled. The exporter unswizzles 16-byte by 8-row texture blocks before expanding 4bpp indices.
- The 8192-byte 4bpp pixel/index block starts at `0x110`. An earlier `0x100` guess included a 16-byte descriptor as texture data and caused visibly cracked glyphs.
- The current best visual static export uses `--palette-mode rgba`, which is also the CLI default.
- PPSSPP labels the runtime CLUT as `ABGR 8888`, but applying an `abgr` channel shuffle to the embedded static palette makes the pages visibly wrong. Treat PPSSPP's CLUT label as a runtime GPU format label, not proof of embedded palette byte order.
- The exported static pages can still look fuzzy because they are small 128x128 glyph atlases with antialiasing/alpha values. The geometry and glyph order are the important survey facts.

## Next Use

The font/rendering phase should:

1. Decode static `MIG` pages into image files.
2. Compare decoded static pages against `local/work/dumped_textures/`.
3. Use matching pages plus screenshots to infer glyph cell order and text encoding.

Static `MIG` pages can be exported with:

```powershell
.\.venv\Scripts\python.exe tools/export_mig_png.py local/work/tdl_DATA001_0002 local/work/rendered_mig_pages --overwrite
```

This writes local PNGs to:

```text
local/work/rendered_mig_pages/
```

For cell/order analysis, a high-contrast diagnostic export can be generated with:

```powershell
.\.venv\Scripts\python.exe tools/export_mig_png.py local/work/tdl_DATA001_0002 local/work/rendered_mig_pages_contrast --debug-contrast --overwrite
```

Glyph grid facts can be reproduced with:

```powershell
.\.venv\Scripts\python.exe tools/analyze_font_grid.py local/work/tdl_DATA001_0002
```

Observed grid:

- `codeANK9x14_00_0`: 14 columns by 9 rows, 120/126 nonempty cells.
- `codeJAP14x14_00_` through `codeJAP14x14_18_`: 9 columns by 9 rows, 81/81 nonempty cells per page.
- `codeJAP14x14_20_`: 9 columns by 9 rows, 33/81 nonempty cells.
- Every page leaves 2 unused pixels on the right and bottom edges.

Individual glyph cells can be exported with:

```powershell
.\.venv\Scripts\python.exe tools/export_glyph_cells.py local/work/tdl_DATA001_0002 local/work/glyph_cells --base-address 0x040dc200 --overwrite
```

This writes per-cell PNGs and `local/work/glyph_cells/manifest.csv` with page, runtime address, row, column, and pixel bounds.

The manifest includes two candidate glyph ID formulas:

- `glyph_id_contiguous`: ANK cells start at `0x0000`; `codeJAP` cells continue from `0x007e`. This currently matches value ranges seen in offset-table glyph runs.
- `glyph_id_page100`: each page starts at `page_index * 0x100`, retained as a comparison hypothesis.

The current seed map is tracked at:

```text
samples/glyph_map_seed.csv
```

It starts with a manually transcribed subset of `codeJAP14x14_10_` using the `glyph_id_contiguous` formula. It is only a seed: successful decoding should be judged by recognizable strings in `DATA001` offset-table exports, not by the presence of isolated known characters.

## Dialogue Capture: 4F Boss / Briareos

Runtime dialogue supplied on 2026-05-09:

```text
マタ、キターーー！
オレ、モウ何モシタクナイノニ…
メンドクサイカラne、終ワロウヨ。
```

GE captures during this dialogue showed active font pages at:

```text
0x040de300
0x040e0400
0x040e8800
```

The `0x040e0400` page matches the shared Latin/kana atlas well enough to reuse as a visual reference, but the `0x040e8800` capture showed a different kanji set from the earlier UI seed page. Treat runtime VRAM address as page slot identity only; story scenes may load different glyph page contents into the same address range.

The external reference transcript for this scene is the Rengoku 2 wiki Briareos page:

```text
https://w.atwiki.jp/rengoku2/pages/14.html
```

The actual translation target for the captured Briareos dialogue is:

```text
DATA001.BIN -> MCD3 entry 12 -> records 140-143 and 160-174
```

Reproducible export:

```powershell
.\.venv\Scripts\python.exe tools/extract_text.py --format offset-table-runs --glyph-map samples/story_glyph_map_seed.csv local/work/mcd3_entries/DATA001/0012_bin.bin local/work/extract_text_DATA001_0012_story_seeded.json
```

Confirmed pre-fight records:

| Record | Decoded text |
| ---: | --- |
| `140` | `マタ、キターーー！\nオレ、モウ何モシタクナイノニ…` |
| `141` | `メンドクサイカラne、終ワロウヨ。` |
| `142` | `ウハｗｗｗオｋｋｋｋｋ\nイイコト思イツイタyo…` |
| `143` | `ボボ、ボクガ終ワラセテageルネ！` |

Confirmed post-fight records:

| Record | Decoded text |
| ---: | --- |
| `160` | `アア、アアアア、タタ、隊長…` |
| `161` | `オ、オレ、戦ワナイデ逃ゲヨウトシタラ…\n後ロカラ撃タレテ、ソレデ…` |
| `162` | `ウッ…また…思い…メモリーガ…` |
| `163` | `ブリアレオス…` |
| `164` | `死ンダハズ…ダ…` |
| `165` | `オオオレ、悪イコトシテナイヨネ？` |
| `166` | `デモ何モシナカッタカラ…\n撃タレタ…` |
| `167` | `何モシナイノモ、悪イコトナノカナ？` |
| `168` | `自分ヲ守レッテ、隊長ハ言ッテタ。` |
| `169` | `オレ、自分守レナカッタ…` |
| `170` | `ゴメンネ…@GRAM@。\n会エテ…ヨカッタ…` |
| `171` | `…マタ…会エタ？` |
| `172` | `俺ノメモリーニハ…\nオマエノ記録ハ残ッテイナイ。` |
| `173` | `ダガ…ブリアレオス。\nオマエノ名ハ刻まれている…` |
| `174` | `確かにコノ体の何処かに…！` |

Known transcript differences:

- Record `142` contains five `ｋ` codepoints in the ROM export.
- Record `170` contains an embedded `@GRAM@` token.
- Record `171` contains an ellipsis before `会エタ`.

Earlier static script lead for this capture was `#start 4F`, but the exact repeated code pattern for:

```text
マタ、キターーー
```

anchors the supplied dialogue in:

```text
DATA003.BIN -> MCD3 entry 1089 -> #start 6F section -> record 306
```

That `DATA003/1089` row is now treated as script/control context rather than the primary translation text table. The relevant command flow is:

```text
#start 6F
#bgm 21
#readbg 4
#readwait
#fade 30,100
#wait 30
#fade 30,50
#center 1
glyph row
#page
...
#end
```

`#start 6F` contains five page blocks. Page 1 includes record `306`, which contains this code window:

```text
0x0276 0x024c 0x0270 0x0227 0x024c 0x011c 0x011c 0x011c
```

Known mapping from the runtime line:

| Code | Character |
| --- | --- |
| `0x0276` | `マ` |
| `0x024c` | `タ` |
| `0x0270` | `、` |
| `0x0227` | `キ` |
| `0x011c` | `ー` |

These `DATA003/1089` codes do not match the confirmed `DATA001/0012` story glyph map one-to-one, so do not merge this table into `samples/story_glyph_map_seed.csv` until the indirection or page context is understood.

The current tracked story glyph map is:

```text
samples/story_glyph_map_seed.csv
```

It is a manually seeded, repo-safe map confirmed from the Briareos records and should be extended scene by scene.
