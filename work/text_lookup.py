"""Resolve mission text keys against a parsed text table and write the per-mission result."""

import argparse
import json
import sys
from pathlib import Path

from hash_probe import joaat

KEY_PATTERNS = ("{id}", "PROG_{id}", "PROG_{id}_DESC_REPLAY", "PROG_{id}_DESC", "{id}_DESC", "{id}_NAME",
                "{id}_TITLE", "MISSION_{id}", "PROG_{id}_NAME", "PROG_{id}_TITLE")


def lookup(table: dict[str, str], key: str) -> str | None:
    return table.get(f"{joaat(key.lower()):08x}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("table_json", type=Path)
    parser.add_argument("--cmissions", type=Path, required=True)
    parser.add_argument("--progress", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    table = json.loads(args.table_json.read_text(encoding="utf-8"))
    ids = {mission["id"] for mission in json.loads(args.cmissions.read_text(encoding="utf-8"))}
    extra_keys = set()
    for category in json.loads(args.progress.read_text(encoding="utf-8")):
        extra_keys.add(category["category_label"])
        for group in category["filters"]:
            extra_keys.add(group["filter_label"])
            for item in group["items"]:
                ids.add(item["item_id"].upper())
                ids.add(item["label"].upper())

    resolved = {}
    pattern_hits = dict.fromkeys(KEY_PATTERNS, 0)
    for mission_id in sorted(ids):
        found = {}
        for pattern in KEY_PATTERNS:
            key = pattern.format(id=mission_id)
            text = lookup(table, key)
            if text is not None:
                found[key] = text
                pattern_hits[pattern] += 1

        resolved[mission_id] = found

    other = {key: lookup(table, key) for key in sorted(extra_keys)}
    args.out.write_text(json.dumps({"missions": resolved, "other_keys": other}, ensure_ascii=False, indent=1),
                        encoding="utf-8")
    print(f"ids={len(ids)} with any text={sum(1 for found in resolved.values() if found)}")
    print(f"pattern hits: {pattern_hits}")
    print(f"other keys: {other}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
