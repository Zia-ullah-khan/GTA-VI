"""List where mission-ID hashes occur inside a PSO's data section, with spacing, and hexdump chosen ranges."""

import argparse
import struct
import sys
from pathlib import Path

from decomp_common import load_mission_hashes
from pso_survey import split_sections
from text_resource_probe import hexdump


def mission_hits(data: bytes, limit: int, names: dict[int, str]) -> list[tuple[int, str]]:
    hits = []
    for offset in range(0, limit - 3, 4):
        value = struct.unpack_from("<I", data, offset)[0]
        if value in names:
            hits.append((offset, names[value]))

    return hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pso", type=Path)
    parser.add_argument("missions_json", type=Path)
    parser.add_argument("--list", type=int, default=40)
    parser.add_argument("--skip", type=int, default=0)
    parser.add_argument("--range", nargs=2, action="append", default=[], metavar=("START", "LENGTH"))
    args = parser.parse_args()

    data = args.pso.read_bytes()
    names = load_mission_hashes(args.missions_json)
    psin_size = split_sections(data)[0][2]
    hits = mission_hits(data, psin_size, names)
    print(f"{args.pso.name}: PSIN=0x{psin_size:x} mission hash hits={len(hits)} "
          f"distinct={len({name for _, name in hits})}")
    previous = None
    for offset, name in hits[args.skip:args.skip + args.list]:
        delta = "" if previous is None else f" +0x{offset - previous:x}"
        print(f"  0x{offset:06x} {name}{delta}")
        previous = offset

    for start_text, length_text in args.range:
        start = int(start_text, 0)
        length = int(length_text, 0)
        print(f"-- 0x{start:x}")
        print(hexdump(data[start:start + length], start, length))

    return 0


if __name__ == "__main__":
    sys.exit(main())
