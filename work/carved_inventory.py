"""Inventory carved files: group by leading magic and extract printable strings to a searchable index."""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

ASCII_RUN = re.compile(rb"[\x20-\x7e]{4,}")
UTF16_RUN = re.compile(rb"(?:[\x20-\x7e]\x00){4,}")


def magic_label(data: bytes) -> str:
    head = data[:4]
    if head and all(32 <= b < 127 for b in head) and len(head) == 4:
        return head.decode("ascii")

    return "hex:" + head.hex()


def extract_strings(data: bytes) -> list[str]:
    found = [m.decode("ascii") for m in ASCII_RUN.findall(data)]
    found += [m.decode("utf-16-le") for m in UTF16_RUN.findall(data)]
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("carved_dir", type=Path)
    parser.add_argument("--strings-out", type=Path, required=True)
    args = parser.parse_args()

    if not args.carved_dir.is_dir():
        print(f"Not a directory: {args.carved_dir}", file=sys.stderr)
        return 1

    groups = defaultdict(lambda: [0, 0])
    with args.strings_out.open("w", encoding="utf-8") as index:
        for path in sorted(args.carved_dir.glob("*.bin")):
            data = path.read_bytes()
            label = magic_label(data)
            groups[label][0] += 1
            groups[label][1] += len(data)
            for text in extract_strings(data):
                index.write(f"{path.name}\t{text}\n")

    print(f"{'magic':<16}{'files':>8}{'bytes':>14}")
    for label, (count, size) in sorted(groups.items(), key=lambda item: -item[1][1]):
        print(f"{label:<16}{count:>8}{size:>14}")

    print(f"strings index: {args.strings_out} ({args.strings_out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
