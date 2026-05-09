from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


PRINTABLE_ASCII = set(range(0x20, 0x7F)) | {0x09}


@dataclass(frozen=True)
class TextSpan:
    offset: int
    length: int
    encoding: str
    text: str


def is_ascii_byte(value: int) -> bool:
    return value in PRINTABLE_ASCII


def find_ascii_spans(data: bytes, min_length: int = 4) -> Iterable[TextSpan]:
    start: int | None = None
    for index, value in enumerate(data):
        if is_ascii_byte(value):
            if start is None:
                start = index
            continue

        if start is not None:
            yield from _ascii_span(data, start, index, min_length)
            start = None

    if start is not None:
        yield from _ascii_span(data, start, len(data), min_length)


def find_encoded_spans(data: bytes, encoding: str, min_length: int = 4) -> Iterable[TextSpan]:
    for start, end in _candidate_byte_runs(data):
        chunk = data[start:end]
        try:
            text = chunk.decode(encoding)
        except UnicodeDecodeError:
            continue

        if _looks_textual(text) and len(text) >= min_length:
            yield TextSpan(start, end - start, encoding, text)


def find_candidate_spans(
    data: bytes, min_length: int = 4, encodings: tuple[str, ...] = ("ascii", "utf-8", "shift_jis")
) -> list[TextSpan]:
    spans: list[TextSpan] = []

    if "ascii" in encodings:
        spans.extend(find_ascii_spans(data, min_length))

    for encoding in encodings:
        if encoding == "ascii":
            continue
        spans.extend(find_encoded_spans(data, encoding, min_length))

    return sorted(_dedupe_spans(spans), key=lambda span: (span.offset, span.length, span.encoding))


def encode_replacement(text: str, encoding: str, original_length: int) -> bytes:
    encoded = text.encode(encoding)
    if len(encoded) > original_length:
        raise ValueError(
            f"replacement encodes to {len(encoded)} bytes, exceeds original {original_length} bytes"
        )
    return encoded.ljust(original_length, b"\x00")


def has_japanese(text: str) -> bool:
    return any(
        "\u3040" <= char <= "\u30ff"
        or "\u3400" <= char <= "\u4dbf"
        or "\u4e00" <= char <= "\u9fff"
        or "\uff66" <= char <= "\uff9f"
        for char in text
    )


def _ascii_span(data: bytes, start: int, end: int, min_length: int) -> Iterable[TextSpan]:
    length = end - start
    if length >= min_length:
        yield TextSpan(start, length, "ascii", data[start:end].decode("ascii"))


def _looks_textual(text: str) -> bool:
    if not text:
        return False
    return all(char.isprintable() or char == "\t" for char in text)


def _candidate_byte_runs(data: bytes) -> Iterable[tuple[int, int]]:
    start: int | None = None
    for index, value in enumerate(data):
        if value >= 0x20 or value == 0x09:
            if start is None:
                start = index
            continue

        if start is not None:
            yield start, index
            start = None

    if start is not None:
        yield start, len(data)


def _dedupe_spans(spans: Iterable[TextSpan]) -> list[TextSpan]:
    by_key: dict[tuple[int, int], TextSpan] = {}
    for span in spans:
        key = (span.offset, span.length)
        if key not in by_key:
            by_key[key] = span
    return list(by_key.values())
