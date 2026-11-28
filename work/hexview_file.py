"""Hexdump ranges of an extracted file and summarize where printable text runs occur."""

import argparse
import re
import sys
from pathlib import Path

from text_resource_probe import hexdump

TEXT_RUN = re.compile(rb"[\x20-\x7e]{12,}")
BUCKET = 0x40000


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--range", nargs=2, action="append", default=[], metavar=("START", "LENGTH"))
    parser.add_argument("--text-map", action="store_true")
    parser.add_argument("--samples", type=int, default=3)
    args = parser.parse_args()

    if not args.path.is_file():
        print(f"Not a file: {args.path}", file=sys.stderr)
        return 1

    data = args.path.read_bytes()
    print(f"size={len(data)} (0x{len(data):x})")
    for start_text, length_text in args.range:
        start = int(start_text, 0)
        length = int(length_text, 0)
        print(f"-- 0x{start:x}")
        print(hexdump(data[start:start + length], start, length))

    if args.text_map:
        for bucket in range(0, len(data), BUCKET):
            runs = TEXT_RUN.findall(data[bucket:bucket + BUCKET])
            printable = sum(len(run) for run in runs)
            samples = " | ".join(run[:40].decode("latin-1") for run in runs[:args.samples])
            print(f"0x{bucket:07x} text_runs={len(runs):>5} printable={printable / BUCKET:5.1%}  {samples}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
