"""Look up raw key hashes in a parsed text table (hash -> string)."""

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("table", type=Path)
    parser.add_argument("hashes", nargs="+")
    args = parser.parse_args()

    table = json.loads(args.table.read_text(encoding="utf-8"))
    entries = table.get("strings", table)
    normalized = {int(key, 16) if isinstance(key, str) and not key.isdigit() else int(key): value
                  for key, value in entries.items()}
    for text in args.hashes:
        value = int(text, 16)
        print(f"{value:08x}: {normalized.get(value)!r}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
