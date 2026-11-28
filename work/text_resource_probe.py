"""Inflate one headered resource from an archive and show where given key hashes sit inside it."""

import argparse
import struct
import sys
import zlib
from pathlib import Path

from hash_probe import joaat

HEADER_SIZE = 16
READ_LIMIT = 8 * 1024 * 1024


def hexdump(data: bytes, base: int, length: int) -> str:
    lines = []
    for offset in range(0, min(length, len(data)), 16):
        row = data[offset:offset + 16]
        text = "".join(chr(byte) if 32 <= byte < 127 else "." for byte in row)
        lines.append(f"  {base + offset:08x}  {row.hex(' '):<47}  {text}")

    return "\n".join(lines)


def read_resource(archive: Path, page_offset: int) -> tuple[bytes, bytes, int]:
    with archive.open("rb") as handle:
        handle.seek(page_offset)
        data = handle.read(READ_LIMIT)

    decompressor = zlib.decompressobj()
    content = decompressor.decompress(data[HEADER_SIZE:])
    if not decompressor.eof:
        raise ValueError("zlib stream did not end inside the read window")

    consumed = len(data) - HEADER_SIZE - len(decompressor.unused_data)
    return data[:HEADER_SIZE], content, consumed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("page_offset", type=lambda text: int(text, 0))
    parser.add_argument("--keys", nargs="*", default=[])
    parser.add_argument("--save", type=Path)
    parser.add_argument("--head", type=int, default=160)
    parser.add_argument("--context", type=int, default=64)
    args = parser.parse_args()

    try:
        header, content, consumed = read_resource(args.archive, args.page_offset)
    except (zlib.error, ValueError) as error:
        print(f"Cannot read resource: {error}", file=sys.stderr)
        return 1

    print(f"header: {header.hex(' ')}")
    print(f"compressed={consumed} inflated={len(content)}")
    print(hexdump(content, 0, args.head))
    for key in args.keys:
        needle = struct.pack("<I", joaat(key.lower()))
        position = content.find(needle)
        positions = []
        while position != -1:
            positions.append(position)
            position = content.find(needle, position + 1)

        print(f"key {key} hash={joaat(key.lower()):08x} offsets={[hex(p) for p in positions[:6]]}")
        for found in positions[:2]:
            start = max(0, found - 16) & ~0xF
            print(hexdump(content[start:start + args.context], start, args.context))

    if args.save:
        args.save.write_bytes(content)
        print(f"Saved {args.save}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
