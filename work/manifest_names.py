"""List the file manifest decoded from story000.rpf @ 0x35ff74000: file name, category hash, and mission-ID match."""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

NAME_FIELD = "6204d173"
CATEGORY_FIELD = "66239f17"
ID_FIELD = "acec22be"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tree", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    document = json.loads(args.tree.read_text(encoding="utf-8"))
    rows = document["blocks"][0]["rows"]
    categories = Counter(row[CATEGORY_FIELD] for row in rows)
    entries = [{"name": row[NAME_FIELD], "category": row[CATEGORY_FIELD], "id": row[ID_FIELD],
                "fields": {key: value for key, value in row.items()
                           if key not in (NAME_FIELD, CATEGORY_FIELD, ID_FIELD)}} for row in rows]
    args.out.write_text(json.dumps(entries, indent=1), encoding="utf-8")
    print(f"{args.out.name}: files={len(entries)} categories={dict(categories)}")
    for category in categories:
        names = [entry["name"].replace(".pso.meta", "") for entry in entries if entry["category"] == category]
        print(f"-- {category} ({len(names)}): " + " ".join(names))

    return 0


if __name__ == "__main__":
    sys.exit(main())
