"""Print a PSIN block directory with the schema struct each block uses and the mission IDs found inside it."""

import argparse
import struct
import sys
from pathlib import Path

from decomp_common import load_mission_hashes
from pso_blocks import read_blocks
from pso_survey import parse_schema, split_sections


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pso", type=Path)
    parser.add_argument("missions_json", type=Path)
    parser.add_argument("--names", type=int, default=5)
    args = parser.parse_args()

    data = args.pso.read_bytes()
    names = load_mission_hashes(args.missions_json)
    sections = split_sections(data)
    psin_size = sections[0][2]
    structs = {}
    for tag, start, size in sections:
        if tag == "LSCH":
            structs = {int(entry["name"], 16): entry for entry in parse_schema(data, start, size)}

    blocks = read_blocks(data)
    end = blocks[-1].offset + blocks[-1].size
    print(f"{args.pso.name}: blocks={len(blocks)} layout end=0x{end:x} PSIN=0x{psin_size:x} structs={len(structs)}")
    for block in blocks:
        entry = structs.get(block.kind)
        shape = f"struct size=0x{entry['size']:x} x{block.size // entry['size']}" if entry else "builtin"
        found = []
        for offset in range(block.offset, min(block.offset + block.size, psin_size) - 3, 4):
            value = struct.unpack_from("<I", data, offset)[0]
            if value in names:
                found.append(names[value])

        missions = f" missions={len(found)} {found[:args.names]}" if found else ""
        print(f"  #{block.number:<3} kind={block.kind:08x} off=0x{block.offset:05x} size=0x{block.size:05x} "
              f"{shape}{missions}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
