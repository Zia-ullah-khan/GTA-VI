"""Report which candidate names hash (joaat) to a hash that is present in a PSO file.

Schema names (structs, members, enums, enum entries) are matched case-sensitively, which is how this game hashes
them (verified: joaat("Name") = acec22be, the first member of the layout struct). Data values are matched against
the lowercased candidate. Only exact matches are printed; the expected number of chance matches is reported.
"""

import argparse
import itertools
import json
import re
import sys
from pathlib import Path

from decomp_common import joaat
from pso_enum_dump import read_enums
from pso_schema_dump import read_schema

HEX32 = re.compile(r'"([0-9a-f]{8})"')


def collect_schema_targets(data: bytes) -> dict[int, str]:
    targets = {}
    for entry in read_schema(data):
        targets.setdefault(entry["name"], "struct")
        for member in entry["members"]:
            targets.setdefault(member["name"], "member")

    for enum in read_enums(data):
        targets.setdefault(enum["name"], "enum")
        for entry in enum["entries"]:
            targets.setdefault(entry["name"], f"enum-entry {enum['name']:08x}={entry['value']}")

    return targets


def collect_value_targets(tree: Path) -> set[int]:
    return {int(text, 16) for text in HEX32.findall(tree.read_text(encoding="utf-8"))}


def load_candidates(names: list[str], words: Path | None, combine: int, separator: str) -> list[str]:
    candidates = list(names)
    if words is None:
        return candidates

    vocabulary = [line.strip() for line in words.read_text(encoding="utf-8").split() if line.strip()]
    for length in range(1, combine + 1):
        candidates += (separator.join(parts) for parts in itertools.product(vocabulary, repeat=length))

    return candidates


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pso", type=Path)
    parser.add_argument("names", nargs="*")
    parser.add_argument("--tree", type=Path, help="decoded tree JSON; its 32-bit values become lowercase targets")
    parser.add_argument("--words", type=Path, help="whitespace-separated vocabulary, combined up to --combine words")
    parser.add_argument("--combine", type=int, default=1)
    parser.add_argument("--separator", default="", help="text placed between combined words")
    parser.add_argument("--out", type=Path, help="write matches as JSON {hash: name}")
    args = parser.parse_args()

    schema = collect_schema_targets(args.pso.read_bytes())
    values = collect_value_targets(args.tree) if args.tree is not None else set()
    candidates = list(dict.fromkeys(load_candidates(args.names, args.words, args.combine, args.separator)))
    matches = {}
    for name in candidates:
        exact = joaat(name)
        if exact in schema:
            matches[f"{exact:08x}"] = name
            print(f"{exact:08x} {name} [{schema[exact]}]")

        lowered = joaat(name.lower())
        if lowered in values and lowered not in schema:
            matches[f"{lowered:08x}"] = name.lower()
            print(f"{lowered:08x} {name.lower()} [value]")

    expected = len(candidates) * (len(schema) + len(values)) / 2 ** 32
    print(f"candidates={len(candidates)} matched={len(matches)} schema targets={len(schema)} "
          f"value targets={len(values)} expected chance matches={expected:.3f}")
    if args.out is not None:
        args.out.write_text(json.dumps(matches, indent=1, sort_keys=True), encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
