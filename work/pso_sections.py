"""List the sections of a PSO file and optionally hexdump the start of one of them."""

import argparse
import struct
import sys
from pathlib import Path


def read_sections(data: bytes) -> list[tuple[str, int, int]]:
    sections = []
    position = 0
    while position + 8 <= len(data):
        tag = data[position:position + 4].decode("ascii", "replace")
        size = struct.unpack_from(">I", data, position + 4)[0]
        if size < 8:
            raise ValueError(f"Section {tag!r} at 0x{position:x} has invalid size {size}")

        sections.append((tag, position, size))
        position += size

    return sections


def hexdump(data: bytes, start: int, length: int) -> None:
    for offset in range(start, start + length, 16):
        row = data[offset:offset + 16]
        print(f"  {offset:08x}  {row.hex(' ')}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pso", type=Path)
    parser.add_argument("--dump", help="section tag to hexdump")
    parser.add_argument("--length", type=lambda text: int(text, 0), default=0x100)
    args = parser.parse_args()

    data = args.pso.read_bytes()
    for tag, offset, size in read_sections(data):
        print(f"{tag} offset=0x{offset:x} size=0x{size:x}")
        if tag == args.dump:
            hexdump(data, offset, min(size, args.length))

    return 0


if __name__ == "__main__":
    sys.exit(main())
