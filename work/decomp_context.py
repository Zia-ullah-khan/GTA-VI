"""Locate mission-ID hash constants in one decompiled script and group the hits by enclosing function."""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from hash_probe import joaat

HEX_CONSTANT = re.compile(r"0x([0-9A-Fa-f]{8})U?\b")
FUNCTION_HEADER = re.compile(r"^\s*public static \S+ (func_[0-9A-F]{6})\(")


def collect_hits(path: Path, hash_to_id: dict[int, str]) -> dict[str, list[tuple[int, str, str]]]:
    hits = defaultdict(list)
    function = "<none>"
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for number, line in enumerate(handle, start=1):
            header = FUNCTION_HEADER.match(line)
            if header:
                function = header.group(1)
                continue

            for constant in HEX_CONSTANT.findall(line):
                mission_id = hash_to_id.get(int(constant, 16))
                if mission_id:
                    hits[function].append((number, mission_id, line.strip()))

    return hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("script", type=Path)
    parser.add_argument("missions_json", type=Path)
    parser.add_argument("--lines", type=int, default=6)
    parser.add_argument("--width", type=int, default=150)
    args = parser.parse_args()

    if not args.script.is_file():
        print(f"Not a file: {args.script}", file=sys.stderr)
        return 1

    missions = json.loads(args.missions_json.read_text(encoding="utf-8"))
    hash_to_id = {joaat(m["id"].lower()): m["id"] for m in missions}
    hits = collect_hits(args.script, hash_to_id)
    print(f"functions with hits: {len(hits)}")
    for function, entries in sorted(hits.items(), key=lambda item: -len(item[1])):
        distinct = len({mission_id for _, mission_id, _ in entries})
        print(f"{function}: hits={len(entries)} missions={distinct} lines {entries[0][0]}..{entries[-1][0]}")
        for number, mission_id, text in entries[:args.lines]:
            print(f"    {number:>8} {mission_id:<18} {text[:args.width]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
