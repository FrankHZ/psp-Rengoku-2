from __future__ import annotations

import argparse
import datetime as dt
import math
import struct
from dataclasses import dataclass, field
from pathlib import Path


SECTOR_SIZE = 2048


@dataclass
class IsoNode:
    name: str
    source: Path | None
    is_dir: bool
    parent: "IsoNode | None" = None
    children: list["IsoNode"] = field(default_factory=list)
    extent: int = 0
    size: int = 0
    path_table_index: int = 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a simple PSP-compatible ISO9660 image from an extracted PSP folder.")
    parser.add_argument("input_root", type=Path, help="Extracted PSP folder containing UMD_DATA.BIN and PSP_GAME/")
    parser.add_argument("output_iso", type=Path, help="Output ISO path")
    parser.add_argument("--volume-id", default="", help="Override ISO volume id. Defaults to blank, matching UMDGen output.")
    parser.add_argument(
        "--version-numbers",
        action="store_true",
        help="Write standard ISO9660 ;1 file versions. Default omits them, matching UMDGen output.",
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    build_psp_iso(
        input_root=args.input_root,
        output_iso=args.output_iso,
        volume_id=args.volume_id,
        include_version_numbers=args.version_numbers,
        overwrite=args.overwrite,
    )
    print(f"wrote {args.output_iso}")
    return 0


def build_psp_iso(
    input_root: Path,
    output_iso: Path,
    volume_id: str,
    include_version_numbers: bool = False,
    overwrite: bool = False,
) -> None:
    input_root = input_root.resolve()
    if not (input_root / "UMD_DATA.BIN").is_file():
        raise FileNotFoundError(input_root / "UMD_DATA.BIN")
    if not (input_root / "PSP_GAME").is_dir():
        raise FileNotFoundError(input_root / "PSP_GAME")
    if output_iso.exists() and not overwrite:
        raise FileExistsError(output_iso)

    root = build_tree(input_root)
    dirs = collect_dirs(root)
    for index, node in enumerate(dirs, start=1):
        node.path_table_index = index

    path_table_size = sum(path_table_record_size(node) for node in dirs)
    le_path_table_lba = 18
    be_path_table_lba = 20

    current_lba = 22
    for node in dirs:
        node.extent = current_lba
        node.size = SECTOR_SIZE
        current_lba += 1

    for node in collect_files(root):
        node.size = node.source.stat().st_size if node.source else 0
        node.extent = current_lba
        current_lba += sectors_for(node.size)

    volume_space_size = current_lba
    output_iso.parent.mkdir(parents=True, exist_ok=True)
    with output_iso.open("wb") as iso:
        iso.write(b"\x00" * SECTOR_SIZE * 16)
        iso.write(primary_volume_descriptor(root, volume_id, volume_space_size, path_table_size, le_path_table_lba, be_path_table_lba))
        iso.write(volume_descriptor_set_terminator())
        write_padded(iso, build_path_table(dirs, endian="<"), SECTOR_SIZE * 2)
        write_padded(iso, build_path_table(dirs, endian=">"), SECTOR_SIZE * 2)
        for node in dirs:
            write_padded(iso, build_directory_data(node, include_version_numbers), node.size)
        for node in collect_files(root):
            with node.source.open("rb") as source:
                copy_padded(source, iso, node.size)


def build_tree(input_root: Path) -> IsoNode:
    root = IsoNode("", input_root, True)
    root_order = ["UMD_DATA.BIN", "PSP_GAME"]
    for name in root_order:
        path = input_root / name
        if path.exists():
            root.children.append(build_node(path, root))
    for path in sorted(input_root.iterdir(), key=lambda item: iso_sort_key(item.name)):
        if path.name not in root_order:
            root.children.append(build_node(path, root))
    return root


def build_node(path: Path, parent: IsoNode) -> IsoNode:
    node = IsoNode(path.name, path, path.is_dir(), parent)
    if node.is_dir:
        for child in sorted(path.iterdir(), key=lambda item: iso_sort_key(item.name)):
            node.children.append(build_node(child, node))
    return node


def iso_sort_key(name: str) -> tuple[int, str]:
    order = {
        "UMD_DATA.BIN": -20,
        "PSP_GAME": -10,
        "SYSDIR": -9,
        "USRDIR": -8,
        "UPDATE": -7,
        "DLL": -6,
        "EBOOT.BIN": -5,
        "PARAM.SFO": -4,
        "ICON0.PNG": -3,
        "PIC0.PNG": -2,
        "PIC1.PNG": -1,
    }
    return (order.get(name.upper(), 0), name.upper())


def collect_dirs(root: IsoNode) -> list[IsoNode]:
    result = [root]
    cursor = 0
    while cursor < len(result):
        result.extend(child for child in result[cursor].children if child.is_dir)
        cursor += 1
    return result


def collect_files(root: IsoNode) -> list[IsoNode]:
    result: list[IsoNode] = []

    def visit(node: IsoNode) -> None:
        if node.is_dir:
            for child in node.children:
                visit(child)
        else:
            result.append(node)

    visit(root)
    return sorted(result, key=file_layout_key)


def node_path(node: IsoNode) -> str:
    parts: list[str] = []
    current: IsoNode | None = node
    while current and current.parent is not None:
        parts.append(current.name)
        current = current.parent
    return "/".join(reversed(parts))


def file_layout_key(node: IsoNode) -> tuple[int, str]:
    order = {
        "UMD_DATA.BIN": 0,
        "PSP_GAME/SYSDIR/EBOOT.BIN": 1,
        "PSP_GAME/SYSDIR/UPDATE/PARAM.SFO": 2,
        "PSP_GAME/SYSDIR/UPDATE/EBOOT.BIN": 3,
        "PSP_GAME/SYSDIR/UPDATE/DATA.BIN": 4,
        "PSP_GAME/PARAM.SFO": 5,
        "PSP_GAME/ICON0.PNG": 6,
        "PSP_GAME/PIC0.PNG": 7,
        "PSP_GAME/PIC1.PNG": 8,
        "PSP_GAME/SYSDIR/BOOT.BIN": 9,
        "PSP_GAME/USRDIR/DATA000.BIN": 10,
        "PSP_GAME/USRDIR/DLL/audiocodec.prx": 11,
        "PSP_GAME/USRDIR/DLL/libatrac3plus.prx": 12,
        "PSP_GAME/USRDIR/DLL/sc_sascore.prx": 13,
        "PSP_GAME/USRDIR/DLL/videocodec.prx": 14,
        "PSP_GAME/USRDIR/DLL/mpegbase.prx": 15,
        "PSP_GAME/USRDIR/DLL/mpeg.prx": 16,
        "PSP_GAME/USRDIR/DLL/libfont.prx": 17,
        "PSP_GAME/USRDIR/DATA001.BIN": 18,
        "PSP_GAME/USRDIR/DATA002.BIN": 19,
        "PSP_GAME/USRDIR/DATA003.BIN": 20,
        "PSP_GAME/USRDIR/DATA004.BIN": 21,
        "PSP_GAME/USRDIR/DATA005.BIN": 22,
    }
    path = node_path(node)
    return (order.get(path, 1000), path.upper())


def primary_volume_descriptor(
    root: IsoNode,
    volume_id: str,
    volume_space_size: int,
    path_table_size: int,
    le_path_table_lba: int,
    be_path_table_lba: int,
) -> bytes:
    data = bytearray(SECTOR_SIZE)
    data[0] = 1
    data[1:6] = b"CD001"
    data[6] = 1
    write_a_string(data, 8, 32, "PSP GAME")
    write_d_string(data, 40, 32, volume_id)
    both_endian_u32(data, 80, volume_space_size)
    both_endian_u16(data, 120, 1)
    both_endian_u16(data, 124, 1)
    both_endian_u16(data, 128, SECTOR_SIZE)
    both_endian_u32(data, 132, path_table_size)
    struct.pack_into("<I", data, 140, le_path_table_lba)
    struct.pack_into("<I", data, 144, 0)
    struct.pack_into(">I", data, 148, be_path_table_lba)
    struct.pack_into(">I", data, 152, 0)
    root_record = directory_record(root, b"\x00", include_version_numbers=True)
    data[156 : 156 + len(root_record)] = root_record
    write_d_string(data, 190, 128, "")
    write_d_string(data, 318, 128, "")
    write_d_string(data, 446, 128, "")
    write_d_string(data, 574, 128, "")
    write_file_structure_version(data)
    return bytes(data)


def volume_descriptor_set_terminator() -> bytes:
    data = bytearray(SECTOR_SIZE)
    data[0] = 255
    data[1:6] = b"CD001"
    data[6] = 1
    return bytes(data)


def build_path_table(dirs: list[IsoNode], endian: str) -> bytes:
    payload = bytearray()
    for node in dirs:
        name = b"\x00" if node.parent is None else iso_name(node.name, is_dir=True, include_version_numbers=False)
        payload.append(1 if node.parent is None else len(name))
        payload.append(0)
        payload.extend(struct.pack(f"{endian}I", node.extent))
        parent_index = 1 if node.parent is None else node.parent.path_table_index
        payload.extend(struct.pack(f"{endian}H", parent_index))
        payload.extend(name)
        if len(name) % 2:
            payload.append(0)
    return bytes(payload)


def path_table_record_size(node: IsoNode) -> int:
    name_len = 1 if node.parent is None else len(iso_name(node.name, is_dir=True, include_version_numbers=False))
    return 8 + name_len + (name_len % 2)


def build_directory_data(node: IsoNode, include_version_numbers: bool) -> bytes:
    payload = bytearray()
    payload.extend(directory_record(node, b"\x00", include_version_numbers))
    payload.extend(directory_record(node.parent or node, b"\x01", include_version_numbers))
    for child in node.children:
        record = directory_record(child, iso_name(child.name, child.is_dir, include_version_numbers), include_version_numbers)
        if len(payload) % SECTOR_SIZE + len(record) > SECTOR_SIZE:
            payload.extend(b"\x00" * (SECTOR_SIZE - (len(payload) % SECTOR_SIZE)))
        payload.extend(record)
    return bytes(payload)


def directory_record(node: IsoNode, name: bytes, include_version_numbers: bool) -> bytes:
    if name not in (b"\x00", b"\x01"):
        name = iso_name(node.name, node.is_dir, include_version_numbers)
    record_len = 33 + len(name) + (0 if len(name) % 2 else 1)
    data = bytearray(record_len)
    data[0] = record_len
    data[1] = 0
    both_endian_u32(data, 2, node.extent)
    both_endian_u32(data, 10, node.size)
    data[18:25] = recording_time()
    data[25] = 0x02 if node.is_dir else 0x00
    data[26] = 0
    data[27] = 0
    both_endian_u16(data, 28, 1)
    data[32] = len(name)
    data[33 : 33 + len(name)] = name
    return bytes(data)


def iso_name(name: str, is_dir: bool, include_version_numbers: bool) -> bytes:
    result = name.encode("ascii")
    if not is_dir and include_version_numbers:
        result += b";1"
    return result


def infer_volume_id(input_root: Path) -> str:
    text = (input_root / "UMD_DATA.BIN").read_bytes().decode("ascii", errors="ignore")
    title_id = text.split("|", 1)[0].strip() or "PSP_GAME"
    return title_id.replace("-", "_")[:32]


def write_file_structure_version(data: bytearray) -> None:
    now = dt.datetime.now(dt.UTC)
    stamp = now.strftime("%Y%m%d%H%M%S00")
    tz = 0
    for offset in (813, 830, 847, 864):
        data[offset : offset + 16] = stamp.encode("ascii")
        data[offset + 16] = tz
    data[881] = 1


def recording_time() -> bytes:
    now = dt.datetime.now(dt.UTC)
    return bytes((now.year - 1900, now.month, now.day, now.hour, now.minute, now.second, 0))


def both_endian_u16(data: bytearray, offset: int, value: int) -> None:
    struct.pack_into("<H", data, offset, value)
    struct.pack_into(">H", data, offset + 2, value)


def both_endian_u32(data: bytearray, offset: int, value: int) -> None:
    struct.pack_into("<I", data, offset, value)
    struct.pack_into(">I", data, offset + 4, value)


def write_a_string(data: bytearray, offset: int, length: int, text: str) -> None:
    encoded = text.encode("ascii", errors="replace")[:length]
    data[offset : offset + length] = encoded.ljust(length, b" ")


def write_d_string(data: bytearray, offset: int, length: int, text: str) -> None:
    encoded = text.encode("ascii", errors="replace")[:length]
    data[offset : offset + length] = encoded.ljust(length, b" ")


def sectors_for(size: int) -> int:
    return max(1, math.ceil(size / SECTOR_SIZE))


def write_padded(handle, payload: bytes, total_size: int) -> None:
    handle.write(payload)
    if len(payload) > total_size:
        raise ValueError("payload exceeds reserved size")
    handle.write(b"\x00" * (total_size - len(payload)))


def copy_padded(source, target, size: int) -> None:
    remaining = size
    while remaining:
        chunk = source.read(min(1024 * 1024, remaining))
        if not chunk:
            raise EOFError("source ended early")
        target.write(chunk)
        remaining -= len(chunk)
    padding = (-size) % SECTOR_SIZE
    if padding:
        target.write(b"\x00" * padding)


if __name__ == "__main__":
    raise SystemExit(main())
