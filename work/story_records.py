"""Flatten the content records (struct a1d21aab) of the decoded story data tree into one JSON row per record.

Each row keeps its parent group (struct 26002175) fields so group-level settings stay attached to the record.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

GROUP_BLOCK_KIND = "26002175"
RECORDS_FIELD = "d566f590"
ID_FIELD = "acec22be"
PROPERTIES_FIELD = "c09087bb"
HASH_MAP_FIELD = "091d160c"
INT_MAP_FIELD = "f4d4a92e"
PLACEMENTS_FIELD = "ce559722"
POSITION_FIELD = "f6852ab6"


def flatten(document: dict) -> list[dict]:
    rows = []
    for block in document["blocks"]:
        if block["kind"] != GROUP_BLOCK_KIND:
            continue

        for group_index, group in enumerate(block["rows"]):
            group_fields = {key: value for key, value in group.items() if key != RECORDS_FIELD}
            for record in group[RECORDS_FIELD]:
                properties = record.get(PROPERTIES_FIELD) or {}
                placements = record.get(PLACEMENTS_FIELD) or []
                rows.append({
                    "id": record[ID_FIELD],
                    "group_index": group_index,
                    "group": group_fields,
                    "fields": {key: value for key, value in record.items()
                               if key not in (ID_FIELD, PROPERTIES_FIELD, PLACEMENTS_FIELD)},
                    "hash_properties": properties.get(HASH_MAP_FIELD, {}),
                    "int_properties": properties.get(INT_MAP_FIELD, {}),
                    "positions": [placement[POSITION_FIELD] for placement in placements],
                    "placements": placements,
                })

    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tree", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    rows = flatten(json.loads(args.tree.read_text(encoding="utf-8")))
    args.out.write_text(json.dumps(rows, indent=1), encoding="utf-8")
    named = [row for row in rows if ":" in row["id"]]
    hash_keys = Counter(key for row in named for key in row["hash_properties"])
    int_keys = Counter(key for row in named for key in row["int_properties"])
    print(f"{args.out.name}: records={len(rows)} mission records={len(named)} "
          f"groups with missions={sorted({row['group_index'] for row in named})}")
    print("hash property keys on mission records: " + ", ".join(f"{k}x{n}" for k, n in hash_keys.most_common()))
    print("int property keys on mission records: " + ", ".join(f"{k}x{n}" for k, n in int_keys.most_common()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
