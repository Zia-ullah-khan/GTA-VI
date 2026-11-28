"""Read-only probe for RPF9 archives: header fields, hexdump, per-region entropy."""

import argparse
import math
import struct
import sys
from collections import Counter
from pathlib import Path

HEADER_SIZE = 0x40


def read_region(path: Path, offset: int, size: int) -> bytes:
    with path.open("rb") as handle:
        handle.seek(offset)
        return handle.read(size)


def entropy(data: bytes) -> float:
    if not data:
        return 0.0

    counts = Counter(data)
    total = len(data)
    return -sum((n / total) * math.log2(n / total) for n in counts.values())


def hexdump(data: bytes, base: int) -> str:
    lines = []
    for start in range(0, len(data), 16):
        chunk = data[start:start + 16]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        text_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{base + start:08x}  {hex_part:<47}  {text_part}")

    return "\n".join(lines)


def print_header(path: Path) -> None:
    header = read_region(path, 0, HEADER_SIZE)
    magic = header[:4]
    words = struct.unpack_from("<15I", header, 4)
    print(f"file: {path}")
    print(f"size: {path.stat().st_size}")
    print(f"magic: {magic!r}")
    for index, word in enumerate(words):
        print(f"  +0x{4 + index * 4:02x}: 0x{word:08x} ({word})")


def print_entropy_map(path: Path, start: int, end: int, step: int) -> None:
    print(f"entropy map 0x{start:x}..0x{end:x} step 0x{step:x}")
    for offset in range(start, end, step):
        block = read_region(path, offset, step)
        if not block:
            break

        zeros = block.count(0) / len(block)
        print(f"  0x{offset:08x}: entropy={entropy(block):.3f} zero_ratio={zeros:.2f}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--dump", type=lambda v: int(v, 0), default=0x300)
    parser.add_argument("--dump-offset", type=lambda v: int(v, 0), default=0)
    parser.add_argument("--entropy-end", type=lambda v: int(v, 0), default=0)
    parser.add_argument("--entropy-step", type=lambda v: int(v, 0), default=0x100)
    args = parser.parse_args()

    if not args.path.is_file():
        print(f"Not a file: {args.path}", file=sys.stderr)
        return 1

    print_header(args.path)
    print(hexdump(read_region(args.path, args.dump_offset, args.dump), args.dump_offset))
    if args.entropy_end:
        print_entropy_map(args.path, 0, args.entropy_end, args.entropy_step)

    return 0


if __name__ == "__main__":
    sys.exit(main())
