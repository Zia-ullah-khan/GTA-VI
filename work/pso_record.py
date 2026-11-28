"""Find records in a decoded PSO tree whose given field holds a named hash, and write them out in full."""

import argparse
import json
import sys
from pathlib import Path


def find_records(value, field: str, name: str, path: str, found: list[tuple[str, dict]]) -> None:
    if isinstance(value, dict):
        held = value.get(field)
        if isinstance(held, str) and held.split(":", 1)[-1] == name:
            found.append((path, value))

        for key, item in value.items():
            find_records(item, field, name, f"{path}.{key}", found)

        return

    if isinstance(value, list):
        for index, item in enumerate(value):
            find_records(item, field, name, f"{path}[{index}]", found)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tree", type=Path)
    parser.add_argument("field")
    parser.add_argument("name")
    parser.add_argument("--blocks", type=int, nargs="*")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    document = json.loads(args.tree.read_text(encoding="utf-8"))
    wanted = set(args.blocks) if args.blocks else set(document["roots"])
    found = []
    for block in document["blocks"]:
        if block["number"] in wanted:
            find_records(block["rows"], args.field, args.name, f"b{block['number']}", found)

    lines = []
    for path, record in found:
        lines.append(f"-- {path}")
        lines.append(json.dumps(record, indent=1))

    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{args.out.name}: records={len(found)} lines={sum(line.count(chr(10)) + 1 for line in lines)}")
    for path, _ in found[:10]:
        print(f"  {path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
