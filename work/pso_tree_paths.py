"""List the field paths of a decoded PSO tree that hold named hashes (mission IDs or text keys), with counts."""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def walk(value, path: str, found: dict[str, list[str]]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            walk(item, f"{path}.{key}", found)

        return

    if isinstance(value, list):
        for item in value:
            walk(item, f"{path}[]", found)

        return

    if isinstance(value, str) and ":" in value:
        found[path].append(value.split(":", 1)[1])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tree", type=Path)
    parser.add_argument("--blocks", type=int, nargs="*")
    parser.add_argument("--examples", type=int, default=5)
    args = parser.parse_args()

    document = json.loads(args.tree.read_text(encoding="utf-8"))
    wanted = set(args.blocks) if args.blocks else set(document["roots"])
    for block in document["blocks"]:
        if block["number"] not in wanted:
            continue

        found = defaultdict(list)
        walk(block["rows"], "", found)
        if not found:
            continue

        print(f"block {block['number']} kind={block['kind']} rows={len(block['rows'])}")
        for path, names in sorted(found.items(), key=lambda item: -len(item[1])):
            distinct = Counter(names)
            print(f"  {path} hits={len(names)} distinct={len(distinct)} e.g. {names[:args.examples]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
