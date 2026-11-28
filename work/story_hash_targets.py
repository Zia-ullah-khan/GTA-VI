"""Collect every unnamed hash that appears on mission records (property keys, values, tags, group fields)."""

import argparse
import json
import re
import sys
from pathlib import Path

HEX8 = re.compile(r"^[0-9a-f]{8}$")


def collect(value, found: set[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            collect(key, found)
            collect(item, found)

        return

    if isinstance(value, list):
        for item in value:
            collect(item, found)

        return

    if isinstance(value, str) and HEX8.match(value) and value != "00000000":
        found.add(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("records", type=Path)
    parser.add_argument("--lists", type=Path, help="decoded list tree whose hashes should be included")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    found = set()
    for row in json.loads(args.records.read_text(encoding="utf-8")):
        if ":" in row["id"]:
            collect({key: value for key, value in row.items() if key != "placements"}, found)

    if args.lists is not None:
        collect(json.loads(args.lists.read_text(encoding="utf-8"))["blocks"], found)

    args.out.write_text("\n".join(sorted(found)) + "\n", encoding="utf-8")
    print(f"{args.out.name}: hashes={len(found)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
