"""Print a condensed, annotated view of one decompiled function: branches, calls and named hash constants."""

import argparse
import re
import sys
from pathlib import Path

from decomp_common import FUNCTION_HEADER, iter_hash_constants, load_mission_hashes

KEEP = re.compile(r"\b(if|return|goto|Virtual\.|Native\.|Imports\.|Builtins\.|func_[0-9A-F]{6}\()|^\s*label_")
NOISE = re.compile(r"^\s*(\{|\}|else)\s*$")


def find_function(path: Path, function: str) -> list[tuple[int, str]]:
    lines = []
    inside = False
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for number, line in enumerate(handle, start=1):
            header = FUNCTION_HEADER.match(line)
            if header:
                if inside:
                    break

                inside = header.group(1) == function

            if inside:
                lines.append((number, line.rstrip("\n")))

    return lines


def annotate(line: str, names: dict[int, str]) -> str:
    found = [f"{value:08X}={names[value]}" for value in iter_hash_constants(line) if value in names]
    return "   <== " + ", ".join(found) if found else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("script", type=Path)
    parser.add_argument("function")
    parser.add_argument("missions_json", type=Path)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=0)
    parser.add_argument("--width", type=int, default=130)
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    if not args.script.is_file():
        print(f"Not a file: {args.script}", file=sys.stderr)
        return 1

    names = load_mission_hashes(args.missions_json)
    lines = find_function(args.script, args.function)
    if not lines:
        print(f"Function not found: {args.function}", file=sys.stderr)
        return 1

    print(f"{args.function}: lines {lines[0][0]}..{lines[-1][0]}")
    for number, line in lines:
        if args.start and number < args.start:
            continue

        if args.end and number > args.end:
            break

        note = annotate(line, names)
        has_hash = any(True for _ in iter_hash_constants(line))
        if NOISE.match(line):
            continue

        if args.all or note or has_hash or KEEP.search(line):
            print(f"{number:>8} {line.strip()[:args.width]}{note}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
