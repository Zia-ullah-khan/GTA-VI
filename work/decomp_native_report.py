"""Report calls to one native per script, next to the mission IDs that script references."""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def owner_missions(refs_index: dict, script: str) -> list[str]:
    functions = refs_index.get(script + ".ysc.cs", {})
    return sorted({mission for entries in functions.values() for _, mission in entries})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("calls_json", type=Path)
    parser.add_argument("refs_json", type=Path)
    parser.add_argument("native")
    parser.add_argument("--max-ids", type=int, default=12)
    parser.add_argument("--named-only", action="store_true")
    args = parser.parse_args()

    calls = [call for call in json.loads(args.calls_json.read_text(encoding="utf-8"))
             if call["native"] == args.native]
    refs_index = json.loads(args.refs_json.read_text(encoding="utf-8"))
    if not calls:
        print(f"No calls recorded for {args.native}", file=sys.stderr)
        return 1

    per_script = defaultdict(list)
    for call in calls:
        per_script[call["script"]].append(call)

    distinct = Counter(call["id_name"] or call["id_hash"] for call in calls)
    print(f"{args.native}: calls={len(calls)} distinct ids={len(distinct)} scripts={len(per_script)}")
    for script, entries in sorted(per_script.items()):
        if args.named_only and not any(entry["id_name"] for entry in entries):
            continue

        owners = owner_missions(refs_index, script)
        ids = []
        for entry in entries:
            tail = (entry["arguments"] or "").split(",", 1)[-1].strip()
            ids.append(f"{entry['id_name'] or entry['id_hash']}[{tail[:14]}]@{entry['line']}")

        shown = ", ".join(ids[:args.max_ids]) + (" ..." if len(ids) > args.max_ids else "")
        print(f"  {script[:18]:<18} refs={','.join(owners)[:60] or '-'}\n      {shown}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
