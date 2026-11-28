"""Check how replay-menu item fields (label, ID, UnlockId) relate to CMissions IDs, and report duplicates."""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("progress_json", type=Path)
    parser.add_argument("cmissions_json", type=Path)
    args = parser.parse_args()

    for path in (args.progress_json, args.cmissions_json):
        if not path.is_file():
            print(f"Not a file: {path}", file=sys.stderr)
            return 1

    known = {entry["id"].upper() for entry in json.loads(args.cmissions_json.read_text(encoding="utf-8"))}
    items = []
    for category in json.loads(args.progress_json.read_text(encoding="utf-8")):
        for group in category["filters"]:
            for item in group["items"]:
                items.append((group["filter_id"], item))

    for field in ("label", "item_id", "unlock_id"):
        values = [item[field].upper() for _, item in items]
        duplicates = {value: count for value, count in Counter(values).items() if count > 1}
        in_table = sum(1 for value in values if value in known)
        print(f"{field}: distinct={len(set(values))}/{len(values)} matches_cmissions={in_table} duplicates={duplicates}")

    print("items where the three fields do not agree (label | ID | UnlockId | evaluator):")
    for filter_id, item in items:
        label, item_id, unlock_id = item["label"].upper(), item["item_id"].upper(), item["unlock_id"].upper()
        if label == item_id == unlock_id:
            continue

        print(f"   {filter_id[-1]}:{item['position']:>2}  {item['label']} | {item['item_id']} | {item['unlock_id']} "
              f"| {item['evaluator']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
