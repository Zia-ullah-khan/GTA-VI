"""Print recovered mission titles in replay-menu order, then titles of table rows that have no menu entry."""

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mission_text_json", type=Path)
    parser.add_argument("--cmissions", type=Path, required=True)
    parser.add_argument("--progress", type=Path, required=True)
    parser.add_argument("--descriptions", action="store_true")
    parser.add_argument("--width", type=int, default=230)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.out:
        sys.stdout = args.out.open("w", encoding="utf-8")

    text = json.loads(args.mission_text_json.read_text(encoding="utf-8"))["missions"]
    listed = set()
    for category in json.loads(args.progress.read_text(encoding="utf-8")):
        for group in category["filters"]:
            print(f"== {group['filter_id']}")
            for item in group["items"]:
                mission_id = item["item_id"].upper()
                listed.add(mission_id)
                found = text.get(mission_id, {})
                label = item["label"].upper()
                title = text.get(label, {}).get(label)
                note = "" if label == mission_id else f" (label {label}; own-ID text: {found.get(mission_id)!r})"
                print(f"  {item['position']:>2} {mission_id:<22} {title!r}{note}")
                if args.descriptions:
                    for key, value in found.items():
                        if key != mission_id:
                            print(f"       {key}: {value[:args.width]}")

    print("== CMissions rows without a menu entry")
    for mission in json.loads(args.cmissions.read_text(encoding="utf-8")):
        if mission["id"].upper() in listed:
            continue

        found = text.get(mission["id"].upper(), {})
        print(f"  {mission['id']:<38} {found.get(mission['id'].upper())!r}")
        if args.descriptions:
            for key, value in found.items():
                if key != mission["id"].upper():
                    print(f"       {key}: {value[:args.width]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
