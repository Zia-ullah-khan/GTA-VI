"""Describe a PSO that holds mission-ID hashes: sections, blocks, schema, and which block and stride the IDs sit in."""

import argparse
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

from decomp_common import load_mission_hashes
from pso_survey import parse_block_table, parse_schema, split_sections

BLOCK_ALIGNMENT = 16


def block_layout(data: bytes) -> list[dict]:
    table_size = struct.unpack_from("<I", data, 0x0C)[0]
    cursor = 0x10 + table_size
    blocks = []
    for name_hash, byte_size in parse_block_table(data):
        cursor = (cursor + BLOCK_ALIGNMENT - 1) // BLOCK_ALIGNMENT * BLOCK_ALIGNMENT
        blocks.append({"name": f"{name_hash:08x}", "offset": cursor, "size": byte_size})
        cursor += byte_size

    return blocks


def find_block(blocks: list[dict], offset: int) -> int | None:
    for index, block in enumerate(blocks):
        if block["offset"] <= offset < block["offset"] + block["size"]:
            return index

    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pso", type=Path)
    parser.add_argument("missions_json", type=Path)
    parser.add_argument("--blocks", type=int, default=25)
    parser.add_argument("--structs", type=int, default=0)
    args = parser.parse_args()

    data = args.pso.read_bytes()
    names = load_mission_hashes(args.missions_json)
    sections = split_sections(data)
    print(f"{args.pso.name}: size={len(data)}")
    print("sections: " + ", ".join(f"{tag}@0x{start:x}+0x{size:x}" for tag, start, size in sections))
    psin_size = sections[0][2]
    blocks = block_layout(data)
    end = blocks[-1]["offset"] + blocks[-1]["size"] if blocks else 0
    print(f"blocks={len(blocks)} layout end=0x{end:x} PSIN size=0x{psin_size:x}")

    per_block = defaultdict(list)
    outside = 0
    for offset in range(0, psin_size - 3, 4):
        value = struct.unpack_from("<I", data, offset)[0]
        if value not in names:
            continue

        index = find_block(blocks, offset)
        if index is None:
            outside += 1
            continue

        per_block[index].append((offset - blocks[index]["offset"], names[value]))

    print(f"mission hash hits: in blocks={sum(len(hits) for hits in per_block.values())} outside={outside}")
    kinds = Counter(block["name"] for block in blocks)
    print("block kinds: " + ", ".join(f"{name}x{count}" for name, count in kinds.most_common(12)))
    ranked = sorted(per_block.items(), key=lambda item: -len(item[1]))
    for index, hits in ranked[:args.blocks]:
        block = blocks[index]
        deltas = Counter(b[0] - a[0] for a, b in zip(hits, hits[1:]))
        distinct = len({name for _, name in hits})
        print(f"  block#{index} kind={block['name']} offset=0x{block['offset']:x} size=0x{block['size']:x} "
              f"hits={len(hits)} distinct={distinct} first_rel=0x{hits[0][0]:x} "
              f"deltas={deltas.most_common(3)} e.g. {[name for _, name in hits[:4]]}")

    if args.structs:
        for tag, start, size in sections:
            if tag != "LSCH":
                continue

            for entry in parse_schema(data, start, size)[:args.structs]:
                members = ", ".join(f"{m['name']}@{m['offset']:x}:{m['type']:x}" for m in entry["members"][:40])
                print(f"  struct {entry['name']} size=0x{entry['size']:x} members={len(entry['members'])}: {members}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
