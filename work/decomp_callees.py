"""For every mission-ID hash reference, record the first call that follows it, to learn which APIs take mission IDs."""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

from decomp_common import FUNCTION_HEADER, iter_hash_constants, load_mission_hashes
from hash_probe import joaat

CALLEE = re.compile(r"\b(Virtual\.type_[0-9A-F]+\.Method_\d+|Native\.[A-Za-z0-9_.]+|Imports\.[a-z0-9_]+\.func_[0-9A-F]{6}|"
                    r"func_[0-9A-F]{6})\(")
LOOKAHEAD = 14


def index_file(path: Path, names: dict[int, str]) -> list[dict]:
    records = []
    pending = deque()
    function = "<none>"
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for number, line in enumerate(handle, start=1):
            header = FUNCTION_HEADER.match(line)
            if header:
                function = header.group(1)
                pending.clear()
                continue

            callee = CALLEE.search(line)
            if callee:
                while pending:
                    origin, mission, same_line = pending.popleft()
                    if number - origin <= LOOKAHEAD:
                        records.append({"function": function, "line": origin, "mission": mission,
                                        "callee": callee.group(1), "call_line": number})

            if "0x" not in line:
                continue

            for value in iter_hash_constants(line):
                mission = names.get(value)
                if mission is None:
                    continue

                if callee:
                    records.append({"function": function, "line": number, "mission": mission,
                                    "callee": callee.group(1), "call_line": number})
                else:
                    pending.append((number, mission, False))

    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("missions_json", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--top", type=int, default=30)
    parser.add_argument("--words", nargs="*", help="Index these words' hashes instead of the mission IDs")
    args = parser.parse_args()

    if not args.source_dir.is_dir():
        print(f"Not a directory: {args.source_dir}", file=sys.stderr)
        return 1

    names = load_mission_hashes(args.missions_json)
    if args.words:
        names = {joaat(word.lower()): word for word in args.words}
    index = {}
    for path in sorted(args.source_dir.glob("*.ysc.cs")):
        records = index_file(path, names)
        if records:
            index[path.name] = records

    callee_hits = Counter()
    callee_files = defaultdict(set)
    callee_missions = defaultdict(set)
    for file_name, records in index.items():
        for record in records:
            callee_hits[record["callee"]] += 1
            callee_files[record["callee"]].add(file_name)
            callee_missions[record["callee"]].add(record["mission"])

    args.out.write_text(json.dumps(index, indent=1), encoding="utf-8")
    print(f"files={len(index)} records={sum(callee_hits.values())} distinct callees={len(callee_hits)}")
    for callee, count in callee_hits.most_common(args.top):
        print(f"  {count:>4} hits  {len(callee_files[callee]):>3} files  {len(callee_missions[callee]):>3} missions  {callee}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
