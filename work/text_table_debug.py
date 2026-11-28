"""Print layout facts of a text-table resource to validate the parser's assumptions."""

import argparse
import struct
import sys
from collections import Counter
from pathlib import Path

from hash_probe import joaat
from text_table import KIND_HASH_TABLE, KIND_POOL, read_blocks, read_hash_table


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("resource", type=Path)
    parser.add_argument("--keys", nargs="*", default=[])
    args = parser.parse_args()

    data = args.resource.read_bytes()
    blocks = read_blocks(data)
    for kind, size, offset in blocks:
        print(f"block kind=0x{kind:08x} size=0x{size:x} offset=0x{offset:x}")

    table = next(block for block in blocks if block[0] == KIND_HASH_TABLE)
    pools = [block for block in blocks if block[0] == KIND_POOL]
    index = next(block for block in blocks if block[0] not in (KIND_HASH_TABLE, KIND_POOL) and block[1] > 16)
    entries = read_hash_table(data, table[2], table[1])
    count = index[1] // 16
    values = [struct.unpack_from("<QQ", data, index[2] + position * 16) for position in range(count)]
    print(f"table entries={len(entries)} index entries={count} max index={max(entries.values())}")
    print(f"first u64 values: {Counter(first for first, _ in values).most_common(3)}")
    print(f"low 20 bits of second u64: {Counter(second & 0xFFFFF for _, second in values).most_common(6)}")
    offsets = [second >> 20 for _, second in values]
    print(f"offset range: {min(offsets):#x}..{max(offsets):#x} pool total={sum(size for _, size, _ in pools):#x} "
          f"monotonic={all(a <= b for a, b in zip(offsets, offsets[1:]))}")
    pool = b"".join(data[offset:offset + size] for _, size, offset in pools)
    bad = [position for position, offset in enumerate(offsets) if offset and pool[offset - 1] != 0]
    print(f"offsets not preceded by NUL: {len(bad)} first={bad[:5]}")
    for key in args.keys:
        position = entries.get(joaat(key.lower()))
        if position is None:
            print(f"{key}: not in table")
            continue

        offset = offsets[position]
        end = pool.find(b"\x00", offset)
        print(f"{key}: index={position} offset={offset:#x} raw={pool[offset:min(end, offset + 90)]!r}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
