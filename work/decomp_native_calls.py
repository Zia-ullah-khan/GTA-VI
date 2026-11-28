"""List every call to selected natives with the hash constant that feeds the first argument and the literal args."""

import argparse
import json
import re
import sys
from collections import Counter, deque
from pathlib import Path

from decomp_common import FUNCTION_HEADER, iter_hash_constants, load_mission_hashes
from hash_probe import joaat

LOOKBACK = 10
ARGUMENTS = re.compile(r"\((.*)\);")


def collect(path: Path, natives: list[str], names: dict[int, str]) -> list[dict]:
    pattern = re.compile(r"Native\.(" + "|".join(re.escape(native) for native in natives) + r")\(")
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

            match = pattern.search(line)
            if match:
                arguments = ARGUMENTS.search(line[match.start():])
                nearest = recent[-1] if recent else None
                calls.append({
                    "script": path.name.replace(".ysc.cs", ""),
                    "function": function,
                    "line": number,
                    "native": match.group(1),
                    "id_hash": f"0x{nearest[1]:08X}" if nearest else None,
                    "id_line": nearest[0] if nearest else None,
                    "id_name": names.get(nearest[1]) if nearest else None,
                    "arguments": arguments.group(1)[:120] if arguments else None,
                    "result_used": line.strip().startswith("v_"),
                })
                recent.clear()
                continue

            for value in iter_hash_constants(line):
                recent.append((number, value))

    return calls


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("missions_json", type=Path)
    parser.add_argument("natives", nargs="+")
    parser.add_argument("--words", type=Path, nargs="*", default=[])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    names = {}
    for path in args.words:
        for word in path.read_text(encoding="utf-8").split():
            if not word.startswith("#"):
                names[joaat(word.lower())] = word.lower()

    names.update(load_mission_hashes(args.missions_json))
    calls = []
    for path in sorted(args.source_dir.glob("*.ysc.cs")):
        calls.extend(collect(path, args.natives, names))

    args.out.write_text(json.dumps(calls, indent=1), encoding="utf-8")
    for native in args.natives:
        subset = [call for call in calls if call["native"] == native]
        named = [call for call in subset if call["id_name"]]
        scripts = {call["script"] for call in subset}
        used = sum(call["result_used"] for call in subset)
        ids = Counter(call["id_name"] for call in named)
        print(f"{native}: calls={len(subset)} scripts={len(scripts)} id named={len(named)} "
              f"distinct named ids={len(ids)} result used={used}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
