"""Parse the block directory of a PSIN section and resolve block-relative pointers.

Directory entries are 16 bytes: 8 placeholder bytes (0xaa), u32 type (struct name hash or builtin id), u32 size.
A pointer is a u64 whose low 12 bits are a 1-based block number and whose remaining bits are the byte offset.
Validated on story000.rpf @ 0x3e30b5000: the last block ends exactly at the PSIN section size.
"""

import struct
from dataclasses import dataclass

PLACEHOLDER = b"\xaa" * 8
DIRECTORY_START = 0x10
ENTRY_SIZE = 16
ALIGNMENT = 16
TERMINATOR = 0x70707070


@dataclass
class Block:
    number: int
    kind: int
    offset: int
    size: int


def read_blocks(data: bytes) -> list[Block]:
    """Block 1 is described by the section header itself; the directory ends with a 0x70-filled entry."""
    entries = [struct.unpack_from("<II", data, 8)]
    cursor = DIRECTORY_START
    while data[cursor:cursor + 8] == PLACEHOLDER:
        kind, size = struct.unpack_from("<II", data, cursor + 8)
        cursor += ENTRY_SIZE
        if kind == TERMINATOR:
            break

        entries.append((kind, size))

    blocks = []
    for number, (kind, size) in enumerate(entries, start=1):
        cursor = (cursor + ALIGNMENT - 1) // ALIGNMENT * ALIGNMENT
        blocks.append(Block(number, kind, cursor, size))
        cursor += size

    return blocks


def resolve(blocks: list[Block], pointer: int) -> int | None:
    number = pointer & 0xFFF
    offset = pointer >> 12
    if not 1 <= number <= len(blocks) or offset > blocks[number - 1].size:
        return None

    return blocks[number - 1].offset + offset


def block_at(blocks: list[Block], offset: int) -> Block | None:
    for block in blocks:
        if block.offset <= offset < block.offset + block.size:
            return block

    return None
