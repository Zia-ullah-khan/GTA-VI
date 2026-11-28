"""Extract the mission replay listing (category > filter > ordered items) from the parsed uiProgressDataset tree."""

import argparse
import json
import sys
from pathlib import Path


def child(node: dict, name: str) -> dict | None:
    for item in node["children"]:
        if item["name"] == name:
            return item

    return None


def child_text(node: dict, name: str) -> str:
    found = child(node, name)
    return (found["content"] or "") if found else ""


def evaluator_type(node: dict) -> str:
    found = child(node, "UnlockEvaluator")
    return found["attributes"].get("type", "") if found else ""


def find_filter_nodes(node: dict, trail: tuple[str, ...]):
    for item in node["children"]:
        if item["name"] == "Filters":
            for filter_node in item["children"]:
                yield filter_node, trail
            continue

        label = child_text(item, "ID")
        yield from find_filter_nodes(item, trail + ((label,) if label else ()))


def collect_filters(category: dict, mission_ids: set[str]) -> list[dict]:
    collected = []
    for filter_node, trail in find_filter_nodes(category, ()):
        items = child(filter_node, "Items")
        entries = []
        for position, item in enumerate(items["children"] if items else []):
            label = child_text(item, "LabelText")
            entries.append({
                "position": position,
                "label": label,
                "item_id": child_text(item, "ID"),
                "unlock_id": child_text(item, "UnlockId"),
                "texture": child_text(item, "DisplayTiledTextureId"),
                "evaluator": evaluator_type(item),
                "hide_if_locked": item["attributes"].get("HideIfLocked"),
                "is_known_mission": label in mission_ids,
            })

        if any(entry["is_known_mission"] for entry in entries):
            collected.append({"filter_id": child_text(filter_node, "ID"), "trail": list(trail),
                              "filter_label": child_text(filter_node, "LabelText"), "items": entries})

    return collected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tree_json", type=Path)
    parser.add_argument("missions_json", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    for path in (args.tree_json, args.missions_json):
        if not path.is_file():
            print(f"Not a file: {path}", file=sys.stderr)
            return 1

    root = json.loads(args.tree_json.read_text(encoding="utf-8"))
    mission_ids = {m["id"] for m in json.loads(args.missions_json.read_text(encoding="utf-8"))}
    listing = []
    for topic in child(root, "Topics")["children"]:
        for category in child(topic, "Categories")["children"]:
            filters = collect_filters(category, mission_ids)
            if filters:
                listing.append({"category_id": child_text(category, "ID"),
                                "category_label": child_text(category, "LabelText"), "filters": filters})

    args.out.write_text(json.dumps(listing, indent=1), encoding="utf-8")
    for category in listing:
        print(f"category ID={category['category_id']!r} label={category['category_label']!r}")
        for group in category["filters"]:
            known = sum(1 for entry in group["items"] if entry["is_known_mission"])
            print(f"  filter ID={group['filter_id']!r} label={group['filter_label']!r} "
                  f"trail={'/'.join(group['trail'])} items={len(group['items'])} known_missions={known}")
            print("     " + " | ".join(entry["label"] for entry in group["items"]))

    return 0


if __name__ == "__main__":
    sys.exit(main())
