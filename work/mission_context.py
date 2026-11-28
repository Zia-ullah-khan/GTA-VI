"""Show the printable context around each mission-ID occurrence in a binary file, grouped by surrounding pattern."""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

CONTEXT_CHARS = re.compile(rb"[\x20-\x7e]+")


def printable_span(data: bytes, start: int, end: int) -> str:
    left = start
    while left > 0 and 32 <= data[left - 1] < 127:
        left -= 1

    right = end
    while right < len(data) and 32 <= data[right] < 127:
        right += 1

    return data[left:right].decode("ascii")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("missions_json", type=Path)
    parser.add_argument("--limit", type=int, default=40)
    args = parser.parse_args()

    for path in (args.path, args.missions_json):
        if not path.is_file():
            print(f"Not a file: {path}", file=sys.stderr)
            return 1

    data = args.path.read_bytes()
    mission_ids = sorted((m["id"] for m in json.loads(args.missions_json.read_text(encoding="utf-8"))),
                         key=len, reverse=True)
    spans = {}
    for mission_id in mission_ids:
        needle = mission_id.encode("ascii")
        cursor = data.find(needle)
        while cursor != -1:
            spans.setdefault(printable_span(data, cursor, cursor + len(needle)), mission_id)
            cursor = data.find(needle, cursor + 1)

    patterns = Counter(text.replace(mission_id, "<ID>") for text, mission_id in spans.items())
    print(f"distinct context strings={len(spans)}")
    print("patterns:")
    for pattern, count in patterns.most_common(12):
        print(f"   {count:>4}  {pattern[:100]}")

    print("examples:")
    for text in sorted(spans)[:args.limit]:
        print(f"   {text[:110]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
