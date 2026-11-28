"""Cross-check the required-player property against the names used in each mission's recap text."""

import argparse
import json
import sys
from pathlib import Path

NAMES = ("Jason", "Lucia")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mission_order", type=Path)
    args = parser.parse_args()

    document = json.loads(args.mission_order.read_text(encoding="utf-8"))
    entries = document["main_story_missions"] + document["side_missions"]
    counts = {"named_in_recap": 0, "other_only": 0, "neither_named": 0, "no_recap": 0}
    conflicts = []
    for entry in entries:
        if entry["protagonist"] not in NAMES:
            continue

        recap = entry["recap_description"]
        if not recap:
            counts["no_recap"] += 1
            continue

        other = NAMES[1 - NAMES.index(entry["protagonist"])]
        if entry["protagonist"] in recap:
            counts["named_in_recap"] += 1
        elif other in recap:
            counts["other_only"] += 1
            conflicts.append(f"{entry['id']} requires {entry['protagonist']}: {recap}")
        else:
            counts["neither_named"] += 1

    print(counts)
    for line in conflicts:
        print("  " + line)

    return 0


if __name__ == "__main__":
    sys.exit(main())
