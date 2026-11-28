"""Summarise value usage in a decoded container layout file (tree JSON from pso_tree.py)."""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT_KIND = "77fba0be"
LAYOUTS = "c19c0de4"
ITEMS = "9a18c89f"
CONTENT = "0e3117bd"
CONDITION = "86c3d806"
ACTIONS = "18526e8a"
TRANSFORM = "8b424621"


def load_root(path: Path) -> dict:
    document = json.loads(path.read_text(encoding="utf-8"))
    roots = [block for block in document["blocks"] if block["kind"] == ROOT_KIND]
    if len(roots) != 1:
        raise ValueError(f"{path.name}: expected one root block of kind {ROOT_KIND}, found {len(roots)}")

    return roots[0]["rows"][0]


def freeze(value) -> str:
    return json.dumps(value, sort_keys=True)


def count_fields(rows: list[dict], skip: set[str]) -> dict[str, Counter]:
    counters: dict[str, Counter] = {}
    for row in rows:
        for key, value in row.items():
            if key in skip:
                continue

            counters.setdefault(key, Counter())[freeze(value)] += 1

    return counters


def print_counters(title: str, counters: dict[str, Counter], limit: int) -> None:
    print(title)
    for key, counter in counters.items():
        shown = ", ".join(f"{value} x{count}" for value, count in counter.most_common(limit))
        more = "" if len(counter) <= limit else f" ...{len(counter) - limit} more distinct"
        print(f"  {key}: {shown}{more}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tree", type=Path)
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args()

    root = load_root(args.tree)
    layouts = root[LAYOUTS]
    items = [item for layout in layouts for item in layout[ITEMS]]
    print(f"layouts={len(layouts)} items={len(items)} "
          f"items per layout min={min(len(l[ITEMS]) for l in layouts)} max={max(len(l[ITEMS]) for l in layouts)}")
    print_counters("layout fields", count_fields(layouts, {ITEMS, "acec22be"}), args.limit)
    print_counters("item fields", count_fields(items, {TRANSFORM, CONTENT, CONDITION, ACTIONS}), args.limit)
    print_counters("item transform fields",
                   count_fields([item[TRANSFORM] for item in items], {"0c928991", "38d2b66e"}), args.limit)

    for label, values in (("content", [item[CONTENT] for item in items]),
                          ("condition", [item[CONDITION] for item in items]),
                          ("action", [action for item in items for action in item[ACTIONS]])):
        kinds = Counter("null" if value is None else value["type"] for value in values)
        print(f"{label} types: {dict(kinds)}")
        for kind in kinds:
            if kind == "null":
                continue

            rows = [value for value in values if value is not None and value["type"] == kind]
            print_counters(f"  {label} {kind}", count_fields(rows, {"type"}), args.limit)

    print("actions per item:", dict(Counter(len(item[ACTIONS]) for item in items)))
    for key, value in root.items():
        if key in (LAYOUTS, "bec3b730"):
            continue

        size = len(value) if isinstance(value, (dict, list)) else value
        print(f"root {key}: entries={size}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
