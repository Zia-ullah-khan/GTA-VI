"""Infer the byte size of each PSO member kind from offset gaps between consecutive fields in the schema."""

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

from pso_schema_dump import read_schema

ELEMENT_DESCRIPTOR = 0x100


def field_gaps(entry: dict) -> list[tuple[int, int]]:
    fields = sorted((m for m in entry["members"] if m["name"] != ELEMENT_DESCRIPTOR), key=lambda m: m["offset"])
    gaps = []
    for index, member in enumerate(fields):
        end = fields[index + 1]["offset"] if index + 1 < len(fields) else entry["size"]
        gaps.append((member["kind"] & 0xFFFF, end - member["offset"]))

    return gaps


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pso", type=Path, nargs="+")
    args = parser.parse_args()

    sizes = defaultdict(Counter)
    for path in args.pso:
        for entry in read_schema(path.read_bytes()):
            for kind, gap in field_gaps(entry):
                sizes[kind][gap] += 1

    for kind in sorted(sizes):
        print(f"kind {kind:04x}: " + ", ".join(f"{gap}x{count}" for gap, count in sorted(sizes[kind].items())))

    return 0


if __name__ == "__main__":
    sys.exit(main())
