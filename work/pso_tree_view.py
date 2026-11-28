"""Print one block of a decoded PSO tree with long arrays and deep rows truncated."""

import argparse
import json
import sys
from pathlib import Path


def shorten(value, depth: int, max_depth: int, max_items: int):
    if isinstance(value, dict):
        if depth >= max_depth:
            return f"{{...{len(value)} fields}}"

        return {key: shorten(item, depth + 1, max_depth, max_items) for key, item in value.items()}

    if isinstance(value, list):
        if depth >= max_depth:
            return f"[...{len(value)} items]"

        head = [shorten(item, depth + 1, max_depth, max_items) for item in value[:max_items]]
        if len(value) > max_items:
            head.append(f"...{len(value) - max_items} more")

        return head

    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tree", type=Path)
    parser.add_argument("block", type=int)
    parser.add_argument("--depth", type=int, default=4)
    parser.add_argument("--items", type=int, default=6)
    parser.add_argument("--rows", type=int, nargs=2, default=[0, 4], metavar=("START", "COUNT"))
    args = parser.parse_args()

    document = json.loads(args.tree.read_text(encoding="utf-8"))
    for block in document["blocks"]:
        if block["number"] != args.block:
            continue

        start, count = args.rows
        print(f"block {block['number']} kind={block['kind']} rows={len(block['rows'])}")
        print(json.dumps(shorten(block["rows"][start:start + count], 0, args.depth, args.items), indent=1))
        return 0

    print(f"Block {args.block} not found", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
