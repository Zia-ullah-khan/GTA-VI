"""Decode the small PSO tables that contain mission-ID hashes: schema, record stride, and per-record contents."""

import argparse
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

from hash_probe import joaat
from pso_survey import parse_schema, split_sections


def mission_hash_offsets(data: bytes, hash_to_id: dict[int, str]) -> list[tuple[int, str]]:
    found = []
    for offset in range(0, len(data) - 3, 4):
        value = struct.unpack_from("<I", data, offset)[0]
        if value in hash_to_id:
            found.append((offset, hash_to_id[value]))

    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("missions_json", type=Path)
    parser.add_argument("paths", type=Path, nargs="+")
    parser.add_argument("--records", type=int, default=6)
    args = parser.parse_args()

    missions = json.loads(args.missions_json.read_text(encoding="utf-8"))
    hash_to_id = {joaat(m["id"].lower()): m["id"] for m in missions}

    digests = Counter()
    for path in args.paths:
        if not path.is_file():
            print(f"Not a file: {path}", file=sys.stderr)
            return 1

        digests[hashlib.sha256(path.read_bytes()).hexdigest()[:16]] += 1

    print(f"files={len(args.paths)} distinct_contents={len(digests)} {dict(digests)}")

    data = args.paths[0].read_bytes()
    sections = split_sections(data)
    print("sections: " + ", ".join(f"{tag}@0x{start:x}+0x{size:x}" for tag, start, size in sections))
    for tag, start, size in sections:
        if tag != "LSCH":
            continue

        for item in parse_schema(data, start, size):
            members = ", ".join(f"{m['name']}@0x{m['offset']:x}:0x{m['type']:x}" for m in item["members"])
            print(f"   struct {item['name']} size=0x{item['size']:x}: {members}")

    offsets = mission_hash_offsets(data, hash_to_id)
    strides = Counter(b[0] - a[0] for a, b in zip(offsets, offsets[1:]))
    print(f"mission hashes found={len(offsets)} distinct={len({m for _, m in offsets})} strides={dict(strides.most_common(4))}")
    if not offsets:
        return 0

    stride = strides.most_common(1)[0][0]
    order = [mission_id for _, mission_id in offsets]
    print("order of first 12 mission hashes: " + " | ".join(order[:12]))
    print(f"first {args.records} records (stride 0x{stride:x}):")
    for offset, mission_id in offsets[:args.records]:
        record = data[offset:offset + stride]
        words = struct.unpack_from(f"<{len(record) // 4}I", record)
        print(f"   0x{offset:05x} {mission_id:<16} " + " ".join(f"{word:08x}" for word in words))

    return 0


if __name__ == "__main__":
    sys.exit(main())
