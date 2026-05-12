# Runtime Observations

Runtime capture is used only to correlate static assets with what PPSSPP
renders. Do not commit dumped textures or screenshots.

## Font Texture Model

Confirmed PPSSPP/GE observations:

```text
texture size:       128x128
texture format:     CLUT4
font page payload:  MIG 4bpp paletted texture
runtime stride:     0x2100 bytes
TDL child size:     0x2110 bytes
```

The font/code-page resources are glyph atlases, not pre-rendered phrase
textures. The game draws UI, help, tutorial, and story text by selecting glyph
cells from those atlases.

Static MIG export facts:

```text
pixel/index block offset: 0x110
pixel/index data size:   8192 bytes
swizzle:                 PSP 16-byte by 8-row texture blocks
default palette mode:    rgba
```

The earlier `0x100` pixel-offset guess was wrong because it included a
16-byte descriptor as texture data.

## Low/High Logical Pages

PPSSPP dump comparison confirmed that each physical 4bpp font texture carries
two logical glyph pages:

```text
low logical page:  index & 0x03
high logical page: index & 0x0c
```

This explains the even `codeJAP14x14_00_`, `02_`, `04_` naming. The 11
physical JP pages provide up to 1782 logical 14x14 cells.

Confirmed runtime bases:

```text
child 1  base 0x0100 / 0x0151
child 2  base 0x01a2 / 0x01f3
child 3  base 0x0244 / 0x0295
child 4  base 0x02e6 / 0x0337
child 5  base 0x0388 / 0x03d9
child 6  base 0x042a / 0x047b
child 7  base 0x04cc / 0x051d
child 8  base 0x056e / 0x05bf
child 9  base 0x0610 / 0x0661
child 10 base 0x06b2 / 0x0703
child 11 base 0x0754 / 0x07a5
```

Alternate bases on one child are alternate code windows over the same cells,
not extra physical storage.

## Grid Facts

Reproduce with:

```powershell
.\.venv\Scripts\python.exe tools/analyze_font_grid.py local/work/tdl_DATA001_0002
```

Observed grid:

```text
codeANK9x14_00_0:               14 columns x 9 rows
codeJAP14x14_00_ through _18_:   9 columns x 9 rows
codeJAP14x14_20_:                9 columns x 9 rows, partial tail page
unused edge pixels:              2 right, 2 bottom
```

## Text Ownership

Confirmed offset-table family:

```text
DATA001/0003 boot/init UI
DATA001/0008 live tutorial/objective overlay
DATA001/0012 story/local story table slice
DATA001/0015 equipment/catalog table
DATA001/0016 UI/menu table
DATA001/0017 help/manual table
DATA002/0065 player-name input and related visible rows
DATA003/1089 script/control context and visible story candidate bank
```

USA reference alignment remains local-only. Useful known alignments:

```text
JP DATA001/0003 -> USA DATA001/0009
JP DATA001/0008 -> USA DATA001/0017
JP DATA001/0012 -> USA DATA001/0022
JP DATA001/0015 -> USA DATA001/0026
JP DATA001/0016 -> USA DATA001/0027
JP DATA001/0017 -> USA DATA001/0028
```

## Story Reference Note

The Briareos dialogue slice was useful for proving story decoding and variable
name tokens. The relevant local target is `DATA001/0012`; `DATA003/1089`
contains script/control context and visible candidate text but is not the
primary table for that confirmed dialogue slice.

External Japanese wiki pages such as `https://w.atwiki.jp/rengoku2/pages/14.html`
may be used for future translation reference, but they are not committed source
material.
