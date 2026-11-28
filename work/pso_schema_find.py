"""Print schema structs by hash, plus every struct that owns a member of a given kind (e.g. 0x75 group maps)."""

import argparse
import sys
from pathlib import Path

from pso_schema_dump import read_schema


def show(entry: dict) -> None:
    print(f"struct {entry['name']:08x} size=0x{entry['size']:x} header={entry['header'][:16]}")
    for index, member in enumerate(entry["members"]):
        print(f"    [{index}] {member['name']:08x} @0x{member['offset']:03x} kind={member['kind']:08x} "
              f"extra={member['extra']:08x}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pso", type=Path)
    parser.add_argument("--struct", action="append", default=[])
    parser.add_argument("--owning-kind", type=lambda text: int(text, 16))
    args = parser.parse_args()

    structs = read_schema(args.pso.read_bytes())
    wanted = {int(text, 16) for text in args.struct}
    for entry in structs:
        owns = args.owning_kind is not None and any((m["kind"] & 0xFF) == args.owning_kind
                                                     and m["name"] != 0x100 for m in entry["members"])
        if entry["name"] in wanted or owns:
            show(entry)

    return 0


if __name__ == "__main__":
    sys.exit(main())
