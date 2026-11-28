"""Scan one archive for names (ASCII or little-endian joaat), in raw bytes and inside every aligned zlib stream."""

import argparse
import struct
import sys
import zlib
from pathlib import Path

from decomp_common import joaat

SEGMENT = 64 * 1024 * 1024
OVERLAP = 0x20000
ALIGNMENT = 16
ZLIB_SECOND_BYTES = (0x01, 0x5E, 0x9C, 0xDA)
MAX_COMPRESSED = 0x12000


def inflate(data: bytes, position: int) -> tuple[bytes, int] | None:
    decompressor = zlib.decompressobj()
    try:
        content = decompressor.decompress(data[position:position + MAX_COMPRESSED])
    except zlib.error:
        return None

    if not decompressor.eof:
        return None

    return content, min(MAX_COMPRESSED, len(data) - position) - len(decompressor.unused_data)


def matches(content: bytes, needles: dict[str, tuple[bytes, bytes]]) -> list[str]:
    return [name for name, (text, packed) in needles.items() if text in content or packed in content]


def scan_segment(data: bytes, base: int, body: int, needles: dict, minimum: int) -> list[dict]:
    hits = []
    position = 0
    while position < body and position + 2 <= len(data):
        if data[position] != 0x78 or data[position + 1] not in ZLIB_SECOND_BYTES:
            position += ALIGNMENT
            continue

        result = inflate(data, position)
        if result is None:
            position += ALIGNMENT
            continue

        content, consumed = result
        found = matches(content, needles)
        if len(found) >= minimum:
            hits.append({"offset": base + position, "kind": "zlib", "inflated": len(content),
                         "head": content[:8].hex(), "names": found})

        position += (consumed + ALIGNMENT - 1) // ALIGNMENT * ALIGNMENT

    for start in range(0, body, 0x10000):
        found = matches(data[start:start + 0x10000], needles)
        if len(found) >= minimum:
            hits.append({"offset": base + start, "kind": "raw", "inflated": 0x10000,
                         "head": data[start:start + 8].hex(), "names": found})

    return hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("names", nargs="+")
    parser.add_argument("--min", type=int, default=2)
    args = parser.parse_args()

    needles = {name: (name.encode("ascii"), struct.pack("<I", joaat(name.lower()))) for name in args.names}
    size = args.archive.stat().st_size
    hits = []
    with args.archive.open("rb") as handle:
        for base in range(0, size, SEGMENT):
            handle.seek(base)
            data = handle.read(SEGMENT + OVERLAP)
            hits += scan_segment(data, base, min(SEGMENT, len(data)), needles, args.min)

    print(f"{args.archive.name}: bytes={size} hits={len(hits)}")
    for hit in hits:
        print(f"  0x{hit['offset']:x} {hit['kind']} inflated={hit['inflated']} head={hit['head']} "
              f"names={','.join(hit['names'])}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
