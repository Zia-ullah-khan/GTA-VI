"""Show, per callee, which script passes which mission IDs and one sample call line."""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def read_line(path: Path, wanted: int) -> str:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for number, line in enumerate(handle, start=1):
            if number == wanted:
                return line.strip()

    return ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("callees_json", type=Path)
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("callees", nargs="+")
    parser.add_argument("--width", type=int, default=150)
    args = parser.parse_args()

    index = json.loads(args.callees_json.read_text(encoding="utf-8"))
    for callee in args.callees:
        per_file = defaultdict(list)
        sample = None
        for file_name, records in index.items():
            for record in records:
                if record["callee"].endswith(callee):
                    per_file[file_name].append(record["mission"])
                    sample = sample or (file_name, record["call_line"])

        if sample is None:
            print(f"{callee}: no records", file=sys.stderr)
            continue

        print(f"== {callee}  files={len(per_file)}")
        print(f"   sample {sample[0]}:{sample[1]}: {read_line(args.source_dir / sample[0], sample[1])[:args.width]}")
        for file_name, missions in sorted(per_file.items()):
            ordered = sorted(set(missions))
            print(f"   {file_name.replace('.ysc.cs', ''):<26} {', '.join(ordered)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
