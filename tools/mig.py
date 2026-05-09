from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import struct
import zlib


@dataclass(frozen=True)
class MigRecord:
    kind: int
    offset_or_size: int
    size_or_width: int
    alignment_or_height: int


@dataclass(frozen=True)
class MigFile:
    path: Path
    records: tuple[MigRecord, ...]
    width: int | None
    height: int | None
    bits_per_pixel: int | None
    palette_offset: int | None
    pixel_offset: int | None
    pixel_size: int | None


def read_mig(path: Path) -> MigFile:
    data = path.read_bytes()
    if len(data) < 0x40:
        raise ValueError("file is too small for MIG")
    if not data.startswith(b"MIG.00.1PSP"):
        raise ValueError(f"expected MIG.00.1PSP magic, got {data[:12]!r}")

    records = tuple(MigRecord(*struct.unpack_from("<IIII", data, 0x10 + index * 0x10)) for index in range(3))

    width = None
    height = None
    bits_per_pixel = None
    palette_offset = None
    pixel_offset = None
    pixel_size = None

    if len(data) >= 0x100:
        # Observed font-page resources use a 16-color RGBA palette at 0x80.
        # The 4bpp pixel indices occupy the final width*height/2 bytes.
        # For the 128x128 font pages this starts at 0x110; starting at 0x100
        # accidentally includes a 16-byte descriptor and causes cracked glyphs.
        candidate_width, candidate_height = struct.unpack_from("<HH", data, 0xD8)
        if candidate_width and candidate_height:
            expected_4bpp_size = candidate_width * candidate_height // 2
            candidate_pixel_offset = len(data) - expected_4bpp_size
            if candidate_pixel_offset >= 0x100:
                width = candidate_width
                height = candidate_height
                bits_per_pixel = 4
                palette_offset = 0x80
                pixel_offset = candidate_pixel_offset
                pixel_size = expected_4bpp_size

    return MigFile(
        path=path,
        records=records,
        width=width,
        height=height,
        bits_per_pixel=bits_per_pixel,
        palette_offset=palette_offset,
        pixel_offset=pixel_offset,
        pixel_size=pixel_size,
    )


def render_mig_rgba(path: Path, palette_mode: str = "rgba", debug_contrast: bool = False) -> tuple[int, int, bytes]:
    mig = read_mig(path)
    if (
        mig.width is None
        or mig.height is None
        or mig.bits_per_pixel != 4
        or mig.palette_offset is None
        or mig.pixel_offset is None
        or mig.pixel_size is None
    ):
        raise ValueError(f"{path} is not a supported 4bpp paletted MIG texture")

    data = path.read_bytes()
    palette = data[mig.palette_offset : mig.palette_offset + 16 * 4]
    pixels = decode_mig_indices(path)[2]

    rgba = bytearray()
    for index in pixels:
        base = index * 4
        red, green, blue, alpha = decode_palette_color(palette[base : base + 4], palette_mode)
        if debug_contrast:
            red, green, blue, alpha = debug_contrast_color(index, alpha)
        rgba.extend((red, green, blue, alpha))

    expected = mig.width * mig.height * 4
    if len(rgba) != expected:
        raise ValueError(f"decoded {len(rgba)} RGBA bytes, expected {expected}")
    return mig.width, mig.height, bytes(rgba)


def decode_mig_indices(path: Path) -> tuple[int, int, bytes]:
    mig = read_mig(path)
    if (
        mig.width is None
        or mig.height is None
        or mig.bits_per_pixel != 4
        or mig.pixel_offset is None
        or mig.pixel_size is None
    ):
        raise ValueError(f"{path} is not a supported 4bpp paletted MIG texture")

    data = path.read_bytes()
    packed_pixels = unswizzle_texture_bytes(
        data[mig.pixel_offset : mig.pixel_offset + mig.pixel_size],
        width_bytes=mig.width // 2,
        height=mig.height,
    )

    indices = bytearray()
    for packed in packed_pixels:
        indices.extend((packed & 0x0F, packed >> 4))

    expected = mig.width * mig.height
    if len(indices) != expected:
        raise ValueError(f"decoded {len(indices)} pixel indices, expected {expected}")
    return mig.width, mig.height, bytes(indices)


def replace_mig_indices(path: Path, indices: bytes, output_path: Path) -> None:
    mig = read_mig(path)
    if (
        mig.width is None
        or mig.height is None
        or mig.bits_per_pixel != 4
        or mig.pixel_offset is None
        or mig.pixel_size is None
    ):
        raise ValueError(f"{path} is not a supported 4bpp paletted MIG texture")

    expected = mig.width * mig.height
    if len(indices) != expected:
        raise ValueError(f"got {len(indices)} indices, expected {expected}")

    packed_linear = pack_4bpp_indices(indices)
    swizzled = swizzle_texture_bytes(packed_linear, width_bytes=mig.width // 2, height=mig.height)

    data = bytearray(path.read_bytes())
    data[mig.pixel_offset : mig.pixel_offset + mig.pixel_size] = swizzled
    output_path.write_bytes(data)


def pack_4bpp_indices(indices: bytes) -> bytes:
    if len(indices) % 2:
        raise ValueError("4bpp index buffer must have an even number of pixels")

    packed = bytearray(len(indices) // 2)
    for index in range(0, len(indices), 2):
        low = indices[index]
        high = indices[index + 1]
        if low > 0x0F or high > 0x0F:
            raise ValueError("4bpp palette indices must be in range 0..15")
        packed[index // 2] = low | (high << 4)
    return bytes(packed)


def decode_palette_color(color: bytes, palette_mode: str) -> tuple[int, int, int, int]:
    if len(color) != 4:
        raise ValueError("palette color must be 4 bytes")
    if palette_mode == "rgba":
        return color[0], color[1], color[2], color[3]
    if palette_mode == "abgr":
        return color[3], color[2], color[1], color[0]
    if palette_mode == "bgra":
        return color[2], color[1], color[0], color[3]
    raise ValueError(f"unsupported palette mode: {palette_mode}")


def debug_contrast_color(index: int, alpha: int) -> tuple[int, int, int, int]:
    if index == 0 or alpha == 0:
        return 0, 0, 0, 0
    value = 255
    return value, value, value, 255


def unswizzle_texture_bytes(data: bytes, width_bytes: int, height: int) -> bytes:
    block_width = 16
    block_height = 8
    if width_bytes % block_width != 0 or height % block_height != 0:
        raise ValueError("unsupported swizzled texture dimensions")

    expected = width_bytes * height
    if len(data) != expected:
        raise ValueError(f"got {len(data)} swizzled bytes, expected {expected}")

    blocks_per_row = width_bytes // block_width
    linear = bytearray(expected)
    for y in range(height):
        for x in range(width_bytes):
            block_x = x // block_width
            block_y = y // block_height
            in_block_x = x % block_width
            in_block_y = y % block_height
            swizzled_offset = (
                (block_y * blocks_per_row + block_x) * block_width * block_height
                + in_block_y * block_width
                + in_block_x
            )
            linear[y * width_bytes + x] = data[swizzled_offset]
    return bytes(linear)


def swizzle_texture_bytes(data: bytes, width_bytes: int, height: int) -> bytes:
    block_width = 16
    block_height = 8
    if width_bytes % block_width != 0 or height % block_height != 0:
        raise ValueError("unsupported linear texture dimensions")

    expected = width_bytes * height
    if len(data) != expected:
        raise ValueError(f"got {len(data)} linear bytes, expected {expected}")

    blocks_per_row = width_bytes // block_width
    swizzled = bytearray(expected)
    for y in range(height):
        for x in range(width_bytes):
            block_x = x // block_width
            block_y = y // block_height
            in_block_x = x % block_width
            in_block_y = y % block_height
            swizzled_offset = (
                (block_y * blocks_per_row + block_x) * block_width * block_height
                + in_block_y * block_width
                + in_block_x
            )
            swizzled[swizzled_offset] = data[y * width_bytes + x]
    return bytes(swizzled)


def write_png_rgba(path: Path, width: int, height: int, rgba: bytes) -> None:
    if len(rgba) != width * height * 4:
        raise ValueError("RGBA buffer size does not match dimensions")

    rows = bytearray()
    stride = width * 4
    for y in range(height):
        rows.append(0)
        rows.extend(rgba[y * stride : (y + 1) * stride])

    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png.extend(chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)))
    png.extend(chunk(b"IDAT", zlib.compress(bytes(rows), level=9)))
    png.extend(chunk(b"IEND", b""))
    path.write_bytes(png)
