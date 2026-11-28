"""Decode a PSO data section into a JSON tree using its own schema.

Field names stay as schema hashes (the dump ships no name table). Hash values are annotated with a readable name
only when the name is a known mission ID or text key whose joaat matches.
Unknown member kinds are kept as raw hex so nothing is silently interpreted.
"""

import argparse
import json
import struct
import sys
from pathlib import Path

from decomp_common import load_mission_hashes
from pso_blocks import Block, read_blocks
from pso_schema_dump import read_schema

ELEMENT_DESCRIPTOR = 0x100
KIND_BOOL = 0x01
KIND_STRUCT = 0x05
KIND_POINTER = 0x07
KIND_HASH = 0x4D
KIND_HASH64 = 0x4F
KIND_ARRAY = 0x52
KIND_ARRAY_COUNT_FIRST = 0x5C
FOUR_BYTE_KINDS = {0x14, 0x15, 0x4A, 0x60, 0x61, 0x62, 0x65}
SIGNED_KINDS = {0x14, 0x15}
KIND_MAP = 0x73
KIND_GROUP_MAP = 0x75
GROUP_SLOTS = 16
GROUP_EMPTY = 0x80
MAP_KEY_FIELD = "6098a50e"
MAP_VALUE_FIELD = "063fa3f2"
KIND_VECTOR = 0x33
KIND_INLINE_STRING = 0x40
FLOAT_KIND = 0x21
POINTER_BLOCK_BITS = 20
MAX_DEPTH = 12


class PsoTree:
    def __init__(self, data: bytes, names: dict[int, str]):
        self._data = data
        self._names = names
        self._blocks = read_blocks(data)
        self._structs = {entry["name"]: entry for entry in read_schema(data)}
        self.referenced = set()

    @property
    def blocks(self) -> list[Block]:
        return self._blocks

    def Label(self, value: int) -> str:
        name = self._names.get(value)
        return f"{value:08x}" if name is None else f"{value:08x}:{name}"

    def Resolve(self, pointer: int) -> tuple[Block, int] | None:
        number = pointer & ((1 << POINTER_BLOCK_BITS) - 1)
        offset = pointer >> POINTER_BLOCK_BITS
        if not 1 <= number <= len(self._blocks):
            return None

        block = self._blocks[number - 1]
        if offset > block.size:
            return None

        self.referenced.add(number)
        return block, block.offset + offset

    def DecodeStruct(self, struct_hash: int, offset: int, depth: int) -> dict:
        entry = self._structs[struct_hash]
        members = entry["members"]
        fields = sorted((m for m in members if m["name"] != ELEMENT_DESCRIPTOR), key=lambda m: m["offset"])
        row = {}
        for index, member in enumerate(fields):
            end = fields[index + 1]["offset"] if index + 1 < len(fields) else entry["size"]
            row[f"{member['name']:08x}"] = self._DecodeMember(members, member, offset + member["offset"],
                                                              end - member["offset"], depth)

        return row

    def DecodeBlock(self, block: Block, depth: int = 0) -> list:
        entry = self._structs.get(block.kind)
        if entry is None:
            return [self._data[block.offset:block.offset + block.size].hex()]

        count = block.size // entry["size"]
        return [self.DecodeStruct(block.kind, block.offset + i * entry["size"], depth) for i in range(count)]

    def _DecodeMember(self, members: list[dict], member: dict, offset: int, size: int, depth: int):
        kind = member["kind"] & 0xFFFF
        base = kind & 0xFF
        if base == KIND_HASH:
            return self.Label(struct.unpack_from("<I", self._data, offset)[0])

        if base == KIND_HASH64:
            return f"{struct.unpack_from('<Q', self._data, offset)[0]:016x}"

        if base == KIND_BOOL:
            return self._data[offset]

        if base == KIND_STRUCT and member["extra"] in self._structs:
            return self.DecodeStruct(member["extra"], offset, depth + 1)

        if base == KIND_POINTER:
            return self._DecodePointer(struct.unpack_from("<Q", self._data, offset)[0], depth)

        if base in (KIND_ARRAY, KIND_ARRAY_COUNT_FIRST):
            return self._DecodeArray(members[member["kind"] >> 16], offset, base, depth)

        if base == KIND_MAP:
            extra = member["extra"]
            return self._DecodeMap(members[extra & 0xFFFF], members[extra >> 16], offset)

        if base == KIND_GROUP_MAP:
            return self._DecodeGroupMap(offset, depth)

        if base == KIND_INLINE_STRING:
            return self._data[offset:offset + size].split(b"\x00", 1)[0].decode("utf-8", "replace")

        if base == KIND_VECTOR:
            return [round(value, 3) for value in struct.unpack_from("<3f", self._data, offset)]

        if base == FLOAT_KIND:
            return round(struct.unpack_from("<f", self._data, offset)[0], 4)

        if base in FOUR_BYTE_KINDS:
            return self.Label(struct.unpack_from("<I", self._data, offset)[0])

        return {"kind": f"{kind:04x}", "raw": self._data[offset:offset + size].hex()}

    def _DecodePointer(self, pointer: int, depth: int):
        if pointer == 0:
            return None

        target = self.Resolve(pointer)
        if target is None:
            return {"bad_pointer": f"{pointer:x}"}

        block, offset = target
        if block.kind not in self._structs or depth >= MAX_DEPTH:
            return {"pointer": f"block{block.number}+0x{offset - block.offset:x}"}

        row = self.DecodeStruct(block.kind, offset, depth + 1)
        return {"type": f"{block.kind:08x}", **row}

    def _DecodeMap(self, key: dict, value: dict, offset: int):
        """Open-addressing table: u32 slot count, u32 used count, u64 pointer; 8-byte slots, all-zero = empty."""
        slots, used, pointer = struct.unpack_from("<IIQ", self._data, offset)
        if used == 0 or pointer == 0:
            return {}

        four_byte = FOUR_BYTE_KINDS | {KIND_HASH}
        target = self.Resolve(pointer)
        if target is None or (key["kind"] & 0xFF) not in four_byte or (value["kind"] & 0xFF) not in four_byte:
            return {"unparsed_map": self._data[offset:offset + 16].hex()}

        _, start = target
        signed = (value["kind"] & 0xFF) in SIGNED_KINDS
        entries = {}
        for index in range(slots):
            slot_key, slot_value = struct.unpack_from("<II", self._data, start + index * 8)
            if slot_key == 0 and slot_value == 0:
                continue

            entries[self.Label(slot_key)] = slot_value if signed else self.Label(slot_value)

        if len(entries) != used:
            raise ValueError(f"Map at 0x{offset:x} holds {len(entries)} entries, header says {used}")

        return entries

    def _DecodeGroupMap(self, offset: int, depth: int):
        """Grouped table: u32 group count, u32 used count, u64 pointer to groups.

        Each group is 16 control bytes (0x80 = empty slot) followed by 16 entries; the group and entry layouts
        come from the schema struct that types the pointed block.
        """
        groups, used, pointer = struct.unpack_from("<IIQ", self._data, offset)
        if used == 0 or pointer == 0:
            return {}

        target = self.Resolve(pointer)
        if target is None or target[0].kind not in self._structs:
            return {"unparsed_map": self._data[offset:offset + 16].hex()}

        block, start = target
        group = self._structs[block.kind]
        entry_hash = next(m["extra"] for m in group["members"]
                          if m["name"] == ELEMENT_DESCRIPTOR and (m["kind"] & 0xFF) == KIND_STRUCT)
        entry_size = self._structs[entry_hash]["size"]
        entries = {}
        for group_index in range(groups):
            base = start + group_index * group["size"]
            for slot in range(GROUP_SLOTS):
                if self._data[base + slot] & GROUP_EMPTY:
                    continue

                row = self.DecodeStruct(entry_hash, base + GROUP_SLOTS + slot * entry_size, depth + 1)
                entries[row[MAP_KEY_FIELD]] = row[MAP_VALUE_FIELD]

        if len(entries) != used:
            raise ValueError(f"Group map at 0x{offset:x} holds {len(entries)} entries, header says {used}")

        return entries

    def _DecodeArray(self, element: dict, offset: int, base: int, depth: int):
        if base == KIND_ARRAY:
            pointer, count = struct.unpack_from("<QH", self._data, offset)
        else:
            count, _, pointer = struct.unpack_from("<IIQ", self._data, offset)

        if count == 0 or pointer == 0:
            return []

        target = self.Resolve(pointer)
        if target is None:
            return {"bad_pointer": f"{pointer:x}", "count": count}

        _, start = target
        element_base = element["kind"] & 0xFF
        if element_base == KIND_STRUCT and element["extra"] in self._structs:
            size = self._structs[element["extra"]]["size"]
            return [self.DecodeStruct(element["extra"], start + i * size, depth + 1) for i in range(count)]

        if element_base == KIND_POINTER:
            pointers = struct.unpack_from(f"<{count}Q", self._data, start)
            return [self._DecodePointer(pointer, depth + 1) for pointer in pointers]

        if element_base == KIND_HASH or element_base in FOUR_BYTE_KINDS:
            return [self.Label(value) for value in struct.unpack_from(f"<{count}I", self._data, start)]

        return {"element_kind": f"{element['kind']:08x}", "count": count, "at": f"0x{start:x}"}


def load_names(missions_json: Path, text_json: Path | None) -> dict[int, str]:
    names = dict(load_mission_hashes(missions_json))
    if text_json is None:
        return names

    from decomp_common import joaat

    for keys in json.loads(text_json.read_text(encoding="utf-8"))["missions"].values():
        for key in keys:
            names.setdefault(joaat(key.lower()), key)

    return names


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pso", type=Path)
    parser.add_argument("missions_json", type=Path)
    parser.add_argument("--text", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    tree = PsoTree(args.pso.read_bytes(), load_names(args.missions_json, args.text))
    decoded = {block.number: tree.DecodeBlock(block) for block in tree.blocks}
    roots = [block.number for block in tree.blocks if block.number not in tree.referenced]
    document = {"source": args.pso.name, "roots": roots,
                "blocks": [{"number": block.number, "kind": f"{block.kind:08x}", "offset": block.offset,
                            "size": block.size, "rows": decoded[block.number]} for block in tree.blocks]}
    args.out.write_text(json.dumps(document, indent=1), encoding="utf-8")
    print(f"{args.out.name}: blocks={len(tree.blocks)} unreferenced={roots}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
