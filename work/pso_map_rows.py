"""Summarise map-like blocks of a decoded PSO tree: one line per populated row with key, value type and field sizes."""

import argparse
import json
import sys
from pathlib import Path


def describe(value) -> str:
    if isinstance(value, list):
        return f"[{len(value)}]"

    if isinstance(value, dict):
        return "{" + ",".join(value) + "}" if len(value) <= 3 else f"{{{len(value)} fields}}"

    return str(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tree", type=Path)
    parser.add_argument("blocks", type=int, nargs="+")
    parser.add_argument("--limit", type=int, default=40)
    args = parser.parse_args()

    document = json.loads(args.tree.read_text(encoding="utf-8"))
    for block in document["blocks"]:
        if block["number"] not in args.blocks:
            continue

        print(f"block {block['number']} kind={block['kind']} rows={len(block['rows'])}")
        shown = 0
        for index, row in enumerate(block["rows"]):
            if not isinstance(row, dict):
                continue

            values = [value for value in row.values() if isinstance(value, dict)]
            if not values or shown >= args.limit:
                continue

            keys = " ".join(f"{name}={value}" for name, value in row.items() if not isinstance(value, (dict, list)))
            for value in values:
                fields = " ".join(f"{name}={describe(item)}" for name, item in value.items())
                print(f"  row {index}: {keys} -> {fields[:400]}")

            shown += 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
