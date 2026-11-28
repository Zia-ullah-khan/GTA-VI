"""Survey decompiled script sources: string literal usage, call vocabulary, and mission-ID hash constants."""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from hash_probe import joaat

STRING_LITERAL = re.compile(r'"((?:[^"\\\n]|\\.){1,200})"')
HEX_CONSTANT = re.compile(r"0x([0-9A-Fa-f]{8})U?\b")
CALL_NAME = re.compile(r"\b([A-Za-z_][A-Za-z0-9_.]*)\(")
SKIPPED_LITERALS = ("Unexpected bytecode fallthrough.",)


def survey_file(path: Path, hash_to_id: dict[int, str]) -> tuple[Counter, Counter, dict[str, int], int]:
    strings = Counter()
    calls = Counter()
    mission_hits = defaultdict(int)
    line_count = 0
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line_count += 1
            for literal in STRING_LITERAL.findall(line):
                if literal not in SKIPPED_LITERALS and not literal.startswith("type_"):
                    strings[literal] += 1

            for name in CALL_NAME.findall(line):
                if not name.startswith("func_"):
                    calls[name] += 1

            for constant in HEX_CONSTANT.findall(line):
                mission_id = hash_to_id.get(int(constant, 16))
                if mission_id:
                    mission_hits[mission_id] += 1

    return strings, calls, mission_hits, line_count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("missions_json", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    if not args.source_dir.is_dir():
        print(f"Not a directory: {args.source_dir}", file=sys.stderr)
        return 1

    missions = json.loads(args.missions_json.read_text(encoding="utf-8"))
    hash_to_id = {joaat(m["id"].lower()): m["id"] for m in missions}
    control = {joaat(f"control_probe_{index}"): f"control_{index}" for index in range(len(hash_to_id))}
    hash_to_id.update(control)

    files = sorted(args.source_dir.glob("*.ysc.cs"))
    if args.limit:
        files = files[:args.limit]

    all_strings = Counter()
    all_calls = Counter()
    per_file = {}
    total_lines = 0
    for path in files:
        strings, calls, mission_hits, line_count = survey_file(path, hash_to_id)
        all_strings.update(strings)
        all_calls.update(calls)
        total_lines += line_count
        if mission_hits:
            per_file[path.name] = dict(mission_hits)

    control_hits = sum(count for hits in per_file.values() for name, count in hits.items() if name.startswith("control_"))
    real_missions = {name for hits in per_file.values() for name in hits if not name.startswith("control_")}
    real_hits = sum(count for hits in per_file.values() for name, count in hits.items() if not name.startswith("control_"))
    args.out.write_text(json.dumps({"mission_hash_hits": per_file, "strings": all_strings.most_common(),
                                    "calls": all_calls.most_common(400)}, indent=1), encoding="utf-8")

    print(f"files={len(files)} lines={total_lines}")
    print(f"distinct string literals={len(all_strings)} total={sum(all_strings.values())}")
    print(f"mission-id hash constants: missions={len(real_missions)} hits={real_hits} "
          f"files={sum(1 for hits in per_file.values() if any(not n.startswith('control_') for n in hits))} "
          f"control_hits={control_hits}")
    print("top calls: " + ", ".join(f"{name}={count}" for name, count in all_calls.most_common(25)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
