"""Index every mission-ID hash reference in the decompiled scripts by file and enclosing function."""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from decomp_common import FUNCTION_HEADER, control_hashes, iter_hash_constants, load_mission_hashes


def index_file(path: Path, names: dict[int, str]) -> dict[str, list[list]]:
    refs = defaultdict(list)
    function = "<none>"
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for number, line in enumerate(handle, start=1):
            header = FUNCTION_HEADER.match(line)
            if header:
                function = header.group(1)
                continue

            if "0x" not in line:
                continue

            for value in iter_hash_constants(line):
                name = names.get(value)
                if name:
                    refs[function].append([number, name])

    return refs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("missions_json", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    if not args.source_dir.is_dir():
        print(f"Not a directory: {args.source_dir}", file=sys.stderr)
        return 1

    missions = load_mission_hashes(args.missions_json)
    names = dict(missions)
    names.update(control_hashes(len(missions)))

    index = {}
    for path in sorted(args.source_dir.glob("*.ysc.cs")):
        refs = index_file(path, names)
        if refs:
            index[path.name] = refs

    hits = Counter()
    files = defaultdict(set)
    for file_name, functions in index.items():
        for entries in functions.values():
            for _, name in entries:
                hits[name] += 1
                files[name].add(file_name)

    control_hits = sum(count for name, count in hits.items() if name.startswith("control_"))
    found = sorted(name for name in hits if not name.startswith("control_"))
    missing = sorted(set(missions.values()) - set(found))
    args.out.write_text(json.dumps(index, indent=1), encoding="utf-8")

    print(f"mission ids={len(missions)} referenced={len(found)} control_hits={control_hits}")
    print(f"files with references={len(index)}")
    print(f"never referenced ({len(missing)}): {', '.join(missing)}")
    ranked = sorted(index.items(), key=lambda item: -len({n for e in item[1].values() for _, n in e}))
    for file_name, functions in ranked[:12]:
        distinct = len({name for entries in functions.values() for _, name in entries})
        total = sum(len(entries) for entries in functions.values())
        print(f"  {file_name:<34} missions={distinct:>3} hits={total:>4} functions={len(functions)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
