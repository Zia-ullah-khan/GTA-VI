"""Print the rows of a decoded PSO tree block whose JSON contains a given text, truncated for reading."""

import argparse
import json
import sys
from pathlib import Path

from pso_tree_view import shorten


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tree", type=Path)
    parser.add_argument("block", type=int)
    parser.add_argument("text")
    parser.add_argument("--depth", type=int, default=6)
    parser.add_argument("--items", type=int, default=12)
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()

    document = json.loads(args.tree.read_text(encoding="utf-8"))
    shown = 0
    for block in document["blocks"]:
        if block["number"] != args.block:
            continue

        for index, row in enumerate(block["rows"]):
            if args.text not in json.dumps(row):
                continue

            print(f"-- block {block['number']} row {index}")
            print(json.dumps(shorten(row, 0, args.depth, args.items), indent=1))
            shown += 1
            if shown >= args.limit:
                return 0

    print(f"rows shown={shown}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
