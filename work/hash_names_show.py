"""Show the recovered names for chosen hashes from hash_names.json."""

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("names", type=Path)
    parser.add_argument("hashes", nargs="+")
    args = parser.parse_args()

    names = json.loads(args.names.read_text(encoding="utf-8"))
    for text in args.hashes:
        print(f"{text}: {names.get(text.lower())}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
