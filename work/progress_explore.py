"""Explore the parsed uiProgressDataset tree: where mission IDs occur and what unlock data accompanies them."""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


def node_text(node: dict) -> str:
    return node["content"] or ""


def child(node: dict, name: str) -> dict | None:
    for item in node["children"]:
        if item["name"] == name:
            return item

    return None


def child_text(node: dict, name: str) -> str:
    found = child(node, name)
    return node_text(found) if found else ""


def walk(node: dict, path: tuple[str, ...]):
    yield node, path
    for item in node["children"]:
        yield from walk(item, path + (item["name"],))


def render(node: dict, depth: int, max_depth: int, lines: list[str]) -> None:
    attributes = " ".join(f"{key}={value!r}" for key, value in node["attributes"].items())
    text = f" = {node_text(node)!r}" if node["content"] else ""
    lines.append(f"{'  ' * depth}<{node['name']}{' ' + attributes if attributes else ''}>{text}")
    if depth >= max_depth:
        if node["children"]:
            lines.append(f"{'  ' * (depth + 1)}... {len(node['children'])} children")
        return

    for item in node["children"]:
        render(item, depth + 1, max_depth, lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tree_json", type=Path)
    parser.add_argument("missions_json", type=Path)
    parser.add_argument("--sample", default="INT_CHASE")
    parser.add_argument("--depth", type=int, default=6)
    args = parser.parse_args()

    for path in (args.tree_json, args.missions_json):
        if not path.is_file():
            print(f"Not a file: {path}", file=sys.stderr)
            return 1

    root = json.loads(args.tree_json.read_text(encoding="utf-8"))
    mission_ids = {m["id"] for m in json.loads(args.missions_json.read_text(encoding="utf-8"))}

    print("top-level topics:")
    topics = child(root, "Topics")
    for topic in topics["children"]:
        categories = child(topic, "Categories")
        count = len(categories["children"]) if categories else 0
        print(f"   ID={child_text(topic, 'ID')!r} label={child_text(topic, 'LabelText')!r} categories={count}")

    tag_hits = Counter()
    path_hits = Counter()
    sample_parent = None
    parents = {}
    for node, path in walk(root, (root["name"],)):
        for item in node["children"]:
            parents[id(item)] = node

        if node_text(node) in mission_ids:
            tag_hits[node["name"]] += 1
            path_hits[" > ".join(path[-5:])] += 1
            if node_text(node) == args.sample and sample_parent is None:
                sample_parent = parents.get(id(node))

    print(f"nodes whose text is exactly a mission ID, by tag: {dict(tag_hits)}")
    for path, count in path_hits.most_common(6):
        print(f"   {count:>5}  ...{path}")

    evaluators = Counter()
    for node, _ in walk(root, ()):
        if node["name"] == "UnlockEvaluator":
            evaluators[(node["attributes"].get("type"), tuple(sorted(c["name"] for c in node["children"])))] += 1

    print("UnlockEvaluator shapes (type attribute, child tags):")
    for shape, count in evaluators.most_common(10):
        print(f"   {count:>5}  {shape}")

    if sample_parent:
        print(f"sample entry containing {args.sample}:")
        lines = []
        render(sample_parent, 0, args.depth, lines)
        print("\n".join(lines[:70]))

    return 0


if __name__ == "__main__":
    sys.exit(main())
