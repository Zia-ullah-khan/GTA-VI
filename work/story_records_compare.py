"""Compare mission records between two flattened map-data files on the properties used for routing."""

import argparse
import json
import sys
from pathlib import Path

KEYS = ("db880157", "f0af2c92", "1fd5bb99", "b376ad2b")


def load(path: Path) -> dict[str, dict]:
    records = {}
    for row in json.loads(path.read_text(encoding="utf-8")):
        if ":" not in row["id"]:
            continue

        properties = {**row["hash_properties"], **row["int_properties"]}
        name = row["id"].split(":", 1)[1]
        records[name] = {key: properties.get(key) for key in KEYS}
        records[name]["position"] = row["positions"][0] if row["positions"] else None

    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("first", type=Path)
    parser.add_argument("second", type=Path)
    args = parser.parse_args()

    first = load(args.first)
    second = load(args.second)
    print(f"first={len(first)} second={len(second)} both={len(first.keys() & second.keys())}")
    print("only first: " + " ".join(sorted(first.keys() - second.keys())))
    print("only second: " + " ".join(sorted(second.keys() - first.keys())))
    for name in sorted(first.keys() & second.keys()):
        differences = [f"{key}: {first[name][key]} vs {second[name][key]}" for key in KEYS
                       if first[name][key] != second[name][key]]
        if differences:
            print(f"  {name}: " + "; ".join(differences))

    return 0


if __name__ == "__main__":
    sys.exit(main())
