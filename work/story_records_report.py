"""Print one compact line per mission record of story_records.json, and value histograms per property key."""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def short(value: str) -> str:
    return value.split(":", 1)[1] if isinstance(value, str) and ":" in value else str(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("records", type=Path)
    parser.add_argument("--all", action="store_true", help="include records whose id is not a known mission ID")
    parser.add_argument("--group", type=int)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    rows = json.loads(args.records.read_text(encoding="utf-8"))
    lines = []
    histograms = defaultdict(Counter)
    for row in rows:
        if args.group is not None and row["group_index"] != args.group:
            continue

        if not args.all and ":" not in row["id"]:
            continue

        properties = {**row["hash_properties"], **row["int_properties"]}
        for key, value in properties.items():
            histograms[short(key)][short(value)] += 1

        for key, value in row["fields"].items():
            if isinstance(value, str):
                histograms[f"field {key}"][short(value)] += 1

        fields = " ".join(f"{key}={short(value)}" for key, value in row["fields"].items()
                          if value not in ("00000000", [], None))
        text = " ".join(f"{short(key)}={short(value)}" for key, value in properties.items())
        position = row["positions"][0] if row["positions"] else None
        lines.append(f"g{row['group_index']} {short(row['id'])}: {fields} | {text} | pos={position} "
                     f"n={len(row['positions'])}")

    lines.append("")
    for key, counter in sorted(histograms.items()):
        values = ", ".join(f"{value}x{count}" for value, count in counter.most_common(14))
        lines.append(f"{key} ({len(counter)} distinct): {values}")

    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{args.out.name}: lines={len(lines)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
