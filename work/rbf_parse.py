"""Parser for RAGE RBF0 binary XML. Emits a JSON tree and a tag histogram; fails loudly on unknown opcodes."""

import argparse
import json
import struct
import sys
from collections import Counter
from pathlib import Path

RBF_MAGIC = b"RBF0"
PREAMBLE_MARKER = b"\xfb\xff"
CLOSE_MARKER = 0xFF
BYTES_MARKER = 0xFD
TYPE_STRUCT = 0x00
TYPE_UINT = 0x10
TYPE_TRUE = 0x20
TYPE_FALSE = 0x30
TYPE_FLOAT = 0x40
TYPE_FLOAT3 = 0x50
TYPE_STRING = 0x60


class RbfError(Exception):
    pass


class Reader:
    def __init__(self, data: bytes):
        self._data = data
        self.position = 0

    def at_end(self) -> bool:
        return self.position >= len(self._data)

    def take(self, size: int) -> bytes:
        if self.position + size > len(self._data):
            raise RbfError(f"Read past end at 0x{self.position:x}")

        chunk = self._data[self.position:self.position + size]
        self.position += size
        return chunk

    def unpack(self, fmt: str):
        return struct.unpack(fmt, self.take(struct.calcsize(fmt)))


def read_value(reader: Reader, data_type: int, numeric_padding: int):
    if data_type == TYPE_UINT:
        value = reader.unpack("<I")[0]
        reader.take(numeric_padding)
        return value
    if data_type == TYPE_TRUE:
        return True
    if data_type == TYPE_FALSE:
        return False
    if data_type == TYPE_FLOAT:
        value = reader.unpack("<f")[0]
        reader.take(numeric_padding)
        return value
    if data_type == TYPE_FLOAT3:
        value = list(reader.unpack("<3f"))
        reader.take(numeric_padding)
        return value
    if data_type == TYPE_STRING:
        length = reader.unpack("<h")[0]
        return reader.take(length).rstrip(b"\x00").decode("utf-8", errors="replace")

    raise RbfError(f"Unknown data type 0x{data_type:02x} at 0x{reader.position:x}")


def new_node(name: str) -> dict:
    return {"name": name, "attributes": {}, "children": [], "content": None}


def read_descriptor(reader: Reader, descriptors: list[tuple[str, int]], index: int, data_type: int) -> str:
    if index == len(descriptors):
        length = reader.unpack("<h")[0]
        name = reader.take(length).decode("ascii", errors="replace")
        descriptors.append((name, data_type))
        return name

    if index > len(descriptors):
        raise RbfError(f"Descriptor index {index} beyond table size {len(descriptors)} at 0x{reader.position:x}")

    return descriptors[index][0]


def parse(data: bytes, numeric_padding: int = 0) -> tuple[dict, list[tuple[str, int]]]:
    if data[:4] != RBF_MAGIC:
        raise RbfError("Missing RBF0 magic")

    reader = Reader(data)
    reader.take(4)
    if data[4:6] == PREAMBLE_MARKER:
        reader.take(4)

    descriptors = []
    stack = []
    root = None
    current = None
    while not reader.at_end():
        index, data_type = reader.unpack("<BB")
        if index == CLOSE_MARKER:
            if not stack:
                break

            current = stack.pop()
            continue

        if index == BYTES_MARKER:
            length = reader.unpack("<i")[0]
            current["content"] = reader.take(length).rstrip(b"\x00").decode("utf-8", errors="replace")
            continue

        name = read_descriptor(reader, descriptors, index, data_type)
        if data_type == TYPE_STRUCT:
            node = new_node(name)
            reader.take(6)
            if current is None:
                root = node
            else:
                current["children"].append(node)
                stack.append(current)

            current = node
            continue

        if current is None:
            raise RbfError(f"Value before root element at 0x{reader.position:x}")

        current["attributes"][name] = read_value(reader, data_type, numeric_padding)

    if root is None:
        raise RbfError("No root element")

    return root, descriptors


def count_tags(node: dict, counts: Counter, depth: int, max_depth: list[int]) -> None:
    counts[node["name"]] += 1
    max_depth[0] = max(max_depth[0], depth)
    for child in node["children"]:
        count_tags(child, counts, depth + 1, max_depth)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--top", type=int, default=70)
    parser.add_argument("--numeric-padding", type=int, default=0)
    args = parser.parse_args()

    if not args.path.is_file():
        print(f"Not a file: {args.path}", file=sys.stderr)
        return 1

    try:
        root, descriptors = parse(args.path.read_bytes(), args.numeric_padding)
    except RbfError as error:
        print(f"Parse failed: {error}", file=sys.stderr)
        return 2

    counts = Counter()
    max_depth = [0]
    count_tags(root, counts, 0, max_depth)
    print(f"root=<{root['name']}> descriptors={len(descriptors)} nodes={sum(counts.values())} max_depth={max_depth[0]}")
    for name, count in counts.most_common(args.top):
        print(f"   {count:>6}  {name}")

    if args.out:
        args.out.write_text(json.dumps(root), encoding="utf-8")
        print(f"saved: {args.out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
