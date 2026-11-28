"""List every call to a virtual type's methods with its enclosing function and the hash constant feeding it."""

import argparse
import json
import re
import sys
from collections import deque
from pathlib import Path

from decomp_common import FUNCTION_HEADER, iter_hash_constants, load_mission_hashes

LOOKBACK = 8


def collect_calls(path: Path, type_name: str, names: dict[int, str]) -> list[dict]:
    call = re.compile(r"Virtual\." + re.escape(type_name) + r"\.Method_(\d+)\(")
    calls = []
    recent = deque(maxlen=LOOKBACK)
    function = "<none>"
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for number, line in enumerate(handle, start=1):
            header = FUNCTION_HEADER.match(line)
            if header:
                function = header.group(1)
                recent.clear()
                continue

            match = call.search(line)
            if match:
                constants = [(origin, value) for origin, value in recent]
                constants += [(number, value) for value in iter_hash_constants(line)]
                nearest = constants[-1] if constants else None
                calls.append({
                    "script": path.name,
                    "function": function,
                    "line": number,
                    "method": int(match.group(1)),
                    "id_hash": f"0x{nearest[1]:08X}" if nearest else None,
                    "id_line": nearest[0] if nearest else None,
                    "id_name": names.get(nearest[1]) if nearest else None,
                    "result_used": "=" in line.split("Virtual.")[0],
                    "text": line.strip()[:160],
                })
                recent.clear()
                continue

            for value in iter_hash_constants(line):
                recent.append((number, value))

    return calls


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("type_name")
    parser.add_argument("missions_json", type=Path)
    parser.add_argument("--scripts", nargs="+", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    names = load_mission_hashes(args.missions_json)
    calls = []
    for script in args.scripts:
        path = args.source_dir / script
        if not path.is_file():
            print(f"Not a file: {path}", file=sys.stderr)
            return 1

        calls.extend(collect_calls(path, args.type_name, names))

    args.out.write_text(json.dumps(calls, indent=1), encoding="utf-8")
    for call in calls:
        print(f"{call['script'][:18]} {call['function']} L{call['line']:<8} Method_{call['method']} "
              f"id={call['id_name'] or call['id_hash']} (L{call['id_line']})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
