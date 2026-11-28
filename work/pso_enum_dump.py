"""Read the enum section (LENM) of a PSO file: enum name hash -> ordered {value, entry name hash}."""

import argparse
import struct
import sys
from pathlib import Path

from pso_sections import read_sections

HEADER_SIZE = 0x18
ENTRY_SIZE = 0x10
PLACEHOLDER = b"\xee" * 8


def read_enums(data: bytes) -> list[dict]:
    section = next((offset, size) for tag, offset, size in read_sections(data) if tag == "LENM")
    position = section[0] + 8
    end = section[0] + section[1]
    headers = []
    while position + HEADER_SIZE <= end and data[position + 8:position + 16] == PLACEHOLDER:
        name, signature = struct.unpack_from("<II", data, position)
        count = struct.unpack_from("<Q", data, position + 16)[0]
        headers.append({"name": name, "signature": signature, "count": count})
        position += HEADER_SIZE

    for header in headers:
        entries = []
        for _ in range(header["count"]):
            value, name = struct.unpack_from("<qI", data, position)
            entries.append({"value": value, "name": name})
            position += ENTRY_SIZE

        header["entries"] = entries

    if position != end:
        raise ValueError(f"Enum section ends at 0x{end:x}, parsing stopped at 0x{position:x}")

    return headers


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pso", type=Path)
    parser.add_argument("--max-entries", type=int, default=12)
    args = parser.parse_args()

    for enum in read_enums(args.pso.read_bytes()):
        shown = " ".join(f"{entry['value']}={entry['name']:08x}" for entry in enum["entries"][:args.max_entries])
        more = "" if enum["count"] <= args.max_entries else f" ...{enum['count'] - args.max_entries} more"
        print(f"enum {enum['name']:08x} count={enum['count']}: {shown}{more}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
