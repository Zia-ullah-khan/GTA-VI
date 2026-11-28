"""Hexdump a byte range of a file."""

import argparse
import sys
from pathlib import Path


def format_line(offset: int, chunk: bytes) -> str:
    hex_part = " ".join(f"{b:02x}" for b in chunk)
    text_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
    return f"{offset:08x}  {hex_part:<47}  {text_part}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--offset", type=lambda v: int(v, 0), default=0)
    parser.add_argument("--size", type=lambda v: int(v, 0), default=0x100)
    args = parser.parse_args()

    if not args.path.is_file():
        print(f"Not a file: {args.path}", file=sys.stderr)
        return 1

    with args.path.open("rb") as handle:
        handle.seek(args.offset)
        data = handle.read(args.size)

    for start in range(0, len(data), 16):
        print(format_line(args.offset + start, data[start:start + 16]))

    return 0


if __name__ == "__main__":
    sys.exit(main())
