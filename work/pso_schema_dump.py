"""Dump the LSCH schema of a PSO with raw member records, and a histogram of member type codes."""

import argparse
import struct
import sys
from collections import Counter
from pathlib import Path

from pso_survey import MEMBER_SIZE, STRUCT_HEADER_SIZE, split_sections


def read_schema(data: bytes) -> list[dict]:
    for tag, start, size in split_sections(data):
        if tag == "LSCH":
            return parse(data, start, size)

    return []


def parse(data: bytes, start: int, size: int) -> list[dict]:
    cursor = start + 8
    end = start + size
    headers = []
    while cursor + STRUCT_HEADER_SIZE <= end and data[cursor + 0x10:cursor + 0x18] == b"\xaa" * 8:
        headers.append(data[cursor:cursor + STRUCT_HEADER_SIZE])
        cursor += STRUCT_HEADER_SIZE

    structs = []
    for header in headers:
        name_hash, signature = struct.unpack_from("<II", header, 0)
        struct_size = struct.unpack_from("<I", header, 0x18)[0]
        member_count = struct.unpack_from("<H", header, 0x1E)[0]
        members = []
        for _ in range(member_count):
            raw = data[cursor:cursor + MEMBER_SIZE]
            name, offset, kind, extra = struct.unpack("<IIII", raw)
            members.append({"name": name, "offset": offset, "kind": kind, "extra": extra})
            cursor += MEMBER_SIZE

        structs.append({"name": name_hash, "signature": signature, "size": struct_size,
                        "header": header.hex(), "members": members})

    return structs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pso", type=Path)
    parser.add_argument("--struct", action="append", default=[], help="struct name hash to print (hex)")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    structs = read_schema(args.pso.read_bytes())
    wanted = {int(text, 16) for text in args.struct}
    kinds = Counter()
    for entry in structs:
        for member in entry["members"]:
            kinds[member["kind"] & 0xFFFF] += 1

    print(f"{args.pso.name}: structs={len(structs)}")
    print("member kind histogram: " + ", ".join(f"{kind:04x}x{count}" for kind, count in kinds.most_common()))
    for entry in structs:
        if not args.all and entry["name"] not in wanted:
            continue

        print(f"struct {entry['name']:08x} sig={entry['signature']:08x} size=0x{entry['size']:x} "
              f"members={len(entry['members'])} header={entry['header'][16:]}")
        for member in entry["members"]:
            print(f"    {member['name']:08x} @0x{member['offset']:03x} kind={member['kind']:08x} "
                  f"extra={member['extra']:08x}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
