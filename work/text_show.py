"""Print full strings from the parsed text table, by key hash or by regular expression."""

import argparse
import json
import re
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("table", type=Path)
    parser.add_argument("--keys", nargs="*", default=[])
    parser.add_argument("--pattern")
    parser.add_argument("--max-length", type=int, default=900)
    args = parser.parse_args()

    table = json.loads(args.table.read_text(encoding="utf-8"))
    selected = [(key.lower(), table.get(key.lower())) for key in args.keys]
    if args.pattern:
        pattern = re.compile(args.pattern, re.IGNORECASE)
        selected += [(key, text) for key, text in table.items() if text and pattern.search(text)]

    for key, text in selected:
        if text is None:
            print(f"{key}: <not in table>")
            continue

        if len(text) > args.max_length:
            continue

        print(f"{key}: {text}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
