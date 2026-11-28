"""Print, for chosen scripts, each mission-ID reference with the call that consumes it."""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("callees_json", type=Path)
    parser.add_argument("scripts", nargs="+")
    parser.add_argument("--skip-functions", nargs="*", default=[])
    args = parser.parse_args()

    index = json.loads(args.callees_json.read_text(encoding="utf-8"))
    for script in args.scripts:
        records = index.get(script + ".ysc.cs")
        if records is None:
            print(f"{script}: no mission references with a following call", file=sys.stderr)
            continue

        grouped = defaultdict(list)
        for record in records:
            if record["function"] in args.skip_functions:
                continue

            grouped[(record["function"], record["callee"])].append(f"{record['mission']}@{record['line']}")

        print(f"== {script}")
        for (function, callee), missions in sorted(grouped.items()):
            print(f"   {function} {callee}: {', '.join(missions[:10])}{' ...' if len(missions) > 10 else ''}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
