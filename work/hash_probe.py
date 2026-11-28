"""Search extracted payloads for mission IDs, both as plain text and as 32-bit Jenkins one-at-a-time hashes."""

import argparse
import json
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

MASK = 0xFFFFFFFF


def joaat(text: str) -> int:
    value = 0
    for byte in text.encode("utf-8"):
        value = (value + byte) & MASK
        value = (value + (value << 10)) & MASK
        value ^= value >> 6

    value = (value + (value << 3)) & MASK
    value ^= value >> 11
    value = (value + (value << 15)) & MASK
    return value


def build_hash_table(mission_ids: list[str]) -> dict[bytes, tuple[str, str]]:
    table = {}
    for mission_id in mission_ids:
        variants = {
            "lower": mission_id.lower(),
            "exact": mission_id,
            "upper": mission_id.upper(),
            "prog_desc": f"prog_{mission_id.lower()}_desc_replay",
            "prog": f"prog_{mission_id.lower()}",
        }
        for label, text in variants.items():
            table.setdefault(struct.pack("<I", joaat(text)), (mission_id, label))

    return table


def scan_hashes(data: bytes, table: dict[bytes, tuple[str, str]]) -> list[tuple[str, str]]:
    hits = []
    for offset in range(0, len(data) - 3, 4):
        match = table.get(data[offset:offset + 4])
        if match:
            hits.append(match)

    return hits


def scan_text(data: bytes, mission_ids: list[str]) -> list[str]:
    return [mission_id for mission_id in mission_ids if mission_id.encode("ascii") in data]


def random_control(count: int) -> dict[bytes, tuple[str, str]]:
    return {struct.pack("<I", joaat(f"control_probe_{index}")): (f"control_{index}", "control") for index in range(count)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("missions_json", type=Path)
    parser.add_argument("extracted_dirs", type=Path, nargs="+")
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    mission_ids = [m["id"] for m in json.loads(args.missions_json.read_text(encoding="utf-8"))]
    table = build_hash_table(mission_ids)
    control = random_control(len(table))
    report = {}
    for directory in args.extracted_dirs:
        if not directory.is_dir():
            print(f"Not a directory: {directory}", file=sys.stderr)
            return 1

        text_hits = defaultdict(list)
        hash_hits = defaultdict(list)
        label_counts = Counter()
        control_hits = 0
        scanned = 0
        for path in sorted(directory.glob("*.bin")):
            if path.name in args.exclude:
                continue

            data = path.read_bytes()
            scanned += len(data)
            for mission_id in scan_text(data, mission_ids):
                text_hits[mission_id].append(path.name)

            for mission_id, label in scan_hashes(data, table):
                hash_hits[mission_id].append(path.name)
                label_counts[label] += 1

            control_hits += len(scan_hashes(data, control))

        expected_random = len(table) * (scanned / 4) / 2**32
        print(f"{directory}: scanned_bytes={scanned}")
        print(f"   plain-text: missions_found={len(text_hits)} file_hits={sum(len(v) for v in text_hits.values())}")
        print(f"   joaat: missions_found={len(hash_hits)} hits={sum(len(v) for v in hash_hits.values())} "
              f"by_variant={dict(label_counts)}")
        print(f"   control: hits={control_hits} expected_random_hits={expected_random:.2f}")
        report[str(directory)] = {"text": text_hits, "hash": hash_hits, "control_hits": control_hits,
                                  "expected_random_hits": expected_random}

    args.out.write_text(json.dumps(report, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
