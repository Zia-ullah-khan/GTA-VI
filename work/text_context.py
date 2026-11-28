"""Classify readable text in a binary file: string statistics and short context around given phrases."""

import argparse
import re
import sys
from pathlib import Path

TEXT_RUN = re.compile(rb"[\x20-\x7e]{6,}")
CONTEXT_BEFORE = 50
CONTEXT_AFTER = 30


def clean(data: bytes) -> str:
    return "".join(chr(b) if 32 <= b < 127 else "." for b in data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("phrases", nargs="+")
    args = parser.parse_args()

    if not args.path.is_file():
        print(f"Not a file: {args.path}", file=sys.stderr)
        return 1

    data = args.path.read_bytes()
    runs = [m.group() for m in TEXT_RUN.finditer(data)]
    lengths = sorted(len(run) for run in runs)
    with_space = sum(1 for run in runs if b" " in run)
    print(f"{args.path.name}: text_runs={len(runs)} with_spaces={with_space} "
          f"median_len={lengths[len(lengths) // 2]} max_len={lengths[-1]} total_text_bytes={sum(lengths)}")

    for phrase in args.phrases:
        needle = phrase.encode("utf-8")
        cursor = data.find(needle)
        count = 0
        while cursor != -1:
            count += 1
            if count <= 3:
                start = max(0, cursor - CONTEXT_BEFORE)
                print(f"   {phrase!r} @0x{cursor:x}: ...{clean(data[start:cursor + len(needle) + CONTEXT_AFTER])}...")

            cursor = data.find(needle, cursor + 1)

        print(f"   {phrase!r}: occurrences={count}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
