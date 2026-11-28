"""List the hash values tested for equality in one decompiled function and compare them with the mission table."""

import argparse
import re
import sys
from pathlib import Path

from decomp_annotate import find_function
from decomp_common import iter_hash_constants, load_mission_hashes

EQUALITY = re.compile(r"(==|!=) as_i32\(0x[0-9A-Fa-f]+\)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("script", type=Path)
    parser.add_argument("function")
    parser.add_argument("missions_json", type=Path)
    args = parser.parse_args()

    names = load_mission_hashes(args.missions_json)
    lines = find_function(args.script, args.function)
    if not lines:
        print(f"Function not found: {args.function}", file=sys.stderr)
        return 1

    tested = set()
    for _, line in lines:
        if EQUALITY.search(line):
            tested.update(iter_hash_constants(line))

    known = sorted(names[value] for value in tested if value in names)
    unknown = sorted(f"{value:08X}" for value in tested if value not in names)
    absent = sorted(set(names.values()) - set(known))
    print(f"{args.function}: equality-tested values={len(tested)} mission ids={len(known)} unnamed={len(unknown)}")
    print(f"unnamed: {', '.join(unknown)}")
    print(f"mission ids not tested ({len(absent)}): {', '.join(absent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
