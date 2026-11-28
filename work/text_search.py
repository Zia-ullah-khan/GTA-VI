"""Search the parsed text table for strings matching a regular expression; print key hash and text."""

import argparse
import json
import re
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("table", type=Path)
    parser.add_argument("pattern")
    parser.add_argument("--limit", type=int, default=40)
    args = parser.parse_args()

    pattern = re.compile(args.pattern, re.IGNORECASE)
    table = json.loads(args.table.read_text(encoding="utf-8"))
    hits = [(key, text) for key, text in table.items() if text and pattern.search(text)]
    print(f"pattern={args.pattern!r} hits={len(hits)}")
    for key, text in hits[:args.limit]:
        print(f"  {key}: {text[:260]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
