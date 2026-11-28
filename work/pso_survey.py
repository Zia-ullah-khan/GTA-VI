"""Survey extracted PSO files: section layout, schema struct hashes, block table, LSNS name-block statistics."""

import argparse
import hashlib
import json
import math
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

SECTION_TAGS = {b"PSIN", b"LSCH", b"LENM", b"LSNS", b"LGID", b"LRSC", b"CHKS", b"LMAP", b"PMAP", b"PSCH", b"PSIG",
                b"STRF", b"STRS", b"STRE", b"LSIG"}
STRUCT_HEADER_SIZE = 0x20
MEMBER_SIZE = 0x10


def entropy(data: bytes) -> float:
    if not data:
        return 0.0

    counts = Counter(data)
    total = len(data)
    return -sum((n / total) * math.log2(n / total) for n in counts.values())


def split_sections(data: bytes) -> list[tuple[str, int, int]]:
    sections = []
    cursor = 0
    while cursor + 8 <= len(data):
        tag = data[cursor:cursor + 4]
        if tag not in SECTION_TAGS:
            break

        size = struct.unpack_from(">I", data, cursor + 4)[0]
        if size < 8 or cursor + size > len(data):
            break

        sections.append((tag.decode("ascii"), cursor, size))
        cursor += size

    return sections


def parse_block_table(data: bytes) -> list[tuple[int, int]]:
    table_size = struct.unpack_from("<I", data, 0x0C)[0]
    entries = []
    for offset in range(0x10, 0x10 + table_size, 0x10):
        name_hash, byte_size = struct.unpack_from("<II", data, offset + 8)
        entries.append((name_hash, byte_size))

    return entries


def parse_schema(data: bytes, start: int, size: int) -> list[dict]:
    structs = []
    headers = []
    cursor = start + 8
    end = start + size
    while cursor + STRUCT_HEADER_SIZE <= end:
        name_hash, signature = struct.unpack_from("<II", data, cursor)
        placeholder = data[cursor + 0x10:cursor + 0x18]
        if placeholder != b"\xaa" * 8:
            break

        struct_size = struct.unpack_from("<I", data, cursor + 0x18)[0]
        member_count = struct.unpack_from("<H", data, cursor + 0x1E)[0]
        headers.append((name_hash, signature, struct_size, member_count))
        cursor += STRUCT_HEADER_SIZE

    for name_hash, signature, struct_size, member_count in headers:
        members = []
        for _ in range(member_count):
            if cursor + MEMBER_SIZE > end:
                break

            member_hash, member_offset, member_type = struct.unpack_from("<III", data, cursor)
            members.append({"name": f"{member_hash:08x}", "offset": member_offset, "type": member_type & 0xFFFF})
            cursor += MEMBER_SIZE

        structs.append({"name": f"{name_hash:08x}", "signature": f"{signature:08x}", "size": struct_size,
                        "members": members})

    return structs


def survey_file(path: Path) -> dict | None:
    data = path.read_bytes()
    if data[:4] != b"PSIN":
        return None

    sections = split_sections(data)
    record = {"file": path.name, "size": len(data), "sections": [tag for tag, _, _ in sections],
              "blocks": [(f"{h:08x}", s) for h, s in parse_block_table(data)], "structs": [], "lsns": None}
    for tag, start, size in sections:
        if tag == "LSCH":
            record["structs"] = parse_schema(data, start, size)
        if tag == "LSNS":
            body = data[start + 8:start + size]
            record["lsns"] = {"size": size, "header": body[:16].hex(), "entropy": round(entropy(body[16:]), 3),
                              "body_sha256": hashlib.sha256(body[16:]).hexdigest()}

    covered = sum(size for _, _, size in sections)
    record["trailing"] = len(data) - covered
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("extracted_dir", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    if not args.extracted_dir.is_dir():
        print(f"Not a directory: {args.extracted_dir}", file=sys.stderr)
        return 1

    records = []
    other_magics = Counter()
    for path in sorted(args.extracted_dir.glob("*.bin")):
        record = survey_file(path)
        if record is None:
            other_magics[path.read_bytes()[:4].hex()] += 1
            continue

        records.append(record)

    args.out.write_text(json.dumps(records), encoding="utf-8")

    layout_counts = Counter(" ".join(r["sections"]) for r in records)
    root_counts = Counter(r["structs"][0]["name"] if r["structs"] else "none" for r in records)
    struct_usage = defaultdict(int)
    for record in records:
        for item in record["structs"]:
            struct_usage[item["name"]] += 1

    print(f"PSO files: {len(records)}  non-PSO: {dict(other_magics)}")
    print("section layouts:")
    for layout, count in layout_counts.most_common():
        print(f"  {count:>5}  {layout}")

    print(f"distinct first-schema structs: {len(root_counts)}")
    for name, count in root_counts.most_common(25):
        print(f"  {count:>5}  {name}")

    print(f"distinct struct hashes overall: {len(struct_usage)}")
    lsns_entropy = [r["lsns"]["entropy"] for r in records if r["lsns"]]
    if lsns_entropy:
        print(f"LSNS blocks: {len(lsns_entropy)} entropy min={min(lsns_entropy)} max={max(lsns_entropy)} "
              f"mean={sum(lsns_entropy) / len(lsns_entropy):.3f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
