"""Parse a text-table resource (magic '0DRP') into {key hash: string}.

Layout, as observed in data.rpf @ 0x19be000 (all little endian, pointers are 0x50000000 + offset):
  0x38  pointer to a block table, 0x4c u16 block count
  block table entry (16 bytes): u32 kind, u32 byte size, u64 pointer
    kind 0x101      hash table: groups of 16 control bytes + 16 entries; control 0x80 = empty slot
                    entry (16 bytes): u32 key hash, u32 zero, u64 value; string index = value >> 24
    kind 0x10       string pool block of NUL-terminated UTF-8
    other, 16 | n   index array: 16-byte entries; second u64 = (offset in block << 20) | 1-based block number
"""

import argparse
import json
import struct
import sys
from pathlib import Path

VIRTUAL_BASE = 0x50000000
MAGIC = b"0DRP"
KIND_HASH_TABLE = 0x101
KIND_POOL = 0x10
GROUP_SLOTS = 16
ENTRY_SIZE = 16
GROUP_SIZE = GROUP_SLOTS + GROUP_SLOTS * ENTRY_SIZE
EMPTY_SLOT = 0x80


class TextTableError(ValueError):
    pass


def to_offset(pointer: int, size: int) -> int:
    offset = pointer - VIRTUAL_BASE
    if not 0 <= offset < size:
        raise TextTableError(f"Pointer 0x{pointer:x} is outside the resource")

    return offset


def read_blocks(data: bytes) -> list[tuple[int, int, int]]:
    if data[0x10:0x14] != MAGIC:
        raise TextTableError("Missing 0DRP magic at 0x10")

    table = to_offset(struct.unpack_from("<Q", data, 0x38)[0], len(data))
    count = struct.unpack_from("<H", data, 0x4C)[0]
    blocks = []
    for index in range(count):
        kind, size, pointer = struct.unpack_from("<IIQ", data, table + index * 16)
        blocks.append((kind, size, to_offset(pointer, len(data))))

    return blocks


def read_hash_table(data: bytes, offset: int, size: int) -> dict[int, int]:
    if size % GROUP_SIZE:
        raise TextTableError(f"Hash table size 0x{size:x} is not a multiple of the group size")

    entries = {}
    for group in range(offset, offset + size, GROUP_SIZE):
        control = data[group:group + GROUP_SLOTS]
        for slot in range(GROUP_SLOTS):
            if control[slot] == EMPTY_SLOT:
                continue

            key, _, value = struct.unpack_from("<IIQ", data, group + GROUP_SLOTS + slot * ENTRY_SIZE)
            entries[key] = value >> 24

    return entries


def read_string(pool: bytes, offset: int) -> str:
    end = pool.find(b"\x00", offset)
    if end == -1:
        raise TextTableError(f"Unterminated string at pool offset 0x{offset:x}")

    return pool[offset:end].decode("utf-8")


def parse(data: bytes) -> dict[int, str]:
    blocks = read_blocks(data)
    tables = [block for block in blocks if block[0] == KIND_HASH_TABLE]
    pools = [block for block in blocks if block[0] == KIND_POOL]
    indexes = [block for block in blocks if block[0] not in (KIND_HASH_TABLE, KIND_POOL) and block[1] > 16]
    if len(tables) != 1 or len(indexes) != 1 or not pools:
        raise TextTableError(f"Unexpected block layout: {[(hex(kind), hex(size)) for kind, size, _ in blocks]}")

    entries = read_hash_table(data, tables[0][2], tables[0][1])
    _, index_size, index_offset = indexes[0]
    index_count = index_size // 16
    strings = {}
    for key, index in entries.items():
        if index >= index_count:
            raise TextTableError(f"String index {index} beyond index array of {index_count}")

        locator = struct.unpack_from("<Q", data, index_offset + index * 16 + 8)[0]
        block_number = (locator & 0xFFFFF) - 1
        if not 0 <= block_number < len(blocks) or blocks[block_number][0] != KIND_POOL:
            raise TextTableError(f"String index {index} names block {block_number + 1}, which is not a pool")

        _, size, offset = blocks[block_number]
        strings[key] = read_string(data[offset:offset + size], locator >> 20)

    return strings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("resource", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    if not args.resource.is_file():
        print(f"Not a file: {args.resource}", file=sys.stderr)
        return 1

    try:
        strings = parse(args.resource.read_bytes())
    except (TextTableError, UnicodeDecodeError, struct.error) as error:
        print(f"Cannot parse text table: {error}", file=sys.stderr)
        return 1

    args.out.write_text(json.dumps({f"{key:08x}": text for key, text in sorted(strings.items())},
                                   ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"entries={len(strings)} distinct strings={len(set(strings.values()))} "
          f"empty={sum(1 for text in strings.values() if not text)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
