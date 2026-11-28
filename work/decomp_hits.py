"""Report where mission-ID hash constants occur in the decompiled scripts and what non-decompiler strings exist."""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

DECOMPILER_LITERAL = re.compile(
    r"^(System\.|box|unbox|array_|packed_|replication_barrier_|func_[0-9A-F]{6}:|stack_|abs_|weak_|invoke_|"
    r"type_|program_|[a-z0-9_]+$)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("survey_json", type=Path)
    parser.add_argument("--top-files", type=int, default=15)
    parser.add_argument("--samples", type=int, default=60)
    args = parser.parse_args()

    if not args.survey_json.is_file():
        print(f"Not a file: {args.survey_json}", file=sys.stderr)
        return 1

    survey = json.loads(args.survey_json.read_text(encoding="utf-8"))
    hits = survey["mission_hash_hits"]
    per_mission = Counter()
    files_per_mission = Counter()
    for file_hits in hits.values():
        for mission_id, count in file_hits.items():
            per_mission[mission_id] += count
            files_per_mission[mission_id] += 1

    print(f"files with mission hash constants: {len(hits)}")
    ranked = sorted(hits.items(), key=lambda item: (-len(item[1]), -sum(item[1].values())))
    for name, file_hits in ranked[:args.top_files]:
        print(f"  {name}  missions={len(file_hits)} hits={sum(file_hits.values())}")

    print("missions by hit count: " + ", ".join(f"{mission_id}={count}/{files_per_mission[mission_id]}f"
                                                 for mission_id, count in per_mission.most_common()))

    strings = survey["strings"]
    other = [(text, count) for text, count in strings if not DECOMPILER_LITERAL.match(text)]
    print(f"string literals total={len(strings)} non-decompiler-shaped={len(other)}")
    for text, count in other[:args.samples]:
        print(f"  {count:>6}  {text[:100]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
