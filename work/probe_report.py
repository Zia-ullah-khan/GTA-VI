"""Summarize hash_probe output: which extracted files reference the most distinct mission IDs, and how."""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def invert(hits: dict[str, list[str]]) -> dict[str, dict[str, int]]:
    by_file = defaultdict(lambda: defaultdict(int))
    for mission_id, files in hits.items():
        for name in files:
            by_file[name][mission_id] += 1

    return by_file


def file_magic(directory: Path, name: str) -> str:
    head = (directory / name).read_bytes()[:4]
    if all(32 <= b < 127 for b in head):
        return head.decode("ascii")

    return "hex:" + head.hex()


def print_section(title: str, directory: Path, by_file: dict[str, dict[str, int]], top: int) -> None:
    ranked = sorted(by_file.items(), key=lambda item: (-len(item[1]), -sum(item[1].values())))
    print(f"{title}: files_with_hits={len(ranked)}")
    for name, missions in ranked[:top]:
        size = (directory / name).stat().st_size
        sample = ", ".join(sorted(missions)[:5])
        print(f"   {name:<34} magic={file_magic(directory, name):<6} size={size:>9} "
              f"distinct_missions={len(missions):>3} hits={sum(missions.values()):>4}  e.g. {sample}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("probe_json", type=Path)
    parser.add_argument("--top", type=int, default=14)
    args = parser.parse_args()

    if not args.probe_json.is_file():
        print(f"Not a file: {args.probe_json}", file=sys.stderr)
        return 1

    report = json.loads(args.probe_json.read_text(encoding="utf-8"))
    for directory_name, sections in report.items():
        directory = Path(directory_name)
        print(f"=== {directory_name}")
        print_section("plain-text", directory, invert(sections["text"]), args.top)
        print_section("joaat", directory, invert(sections["hash"]), args.top)

    return 0


if __name__ == "__main__":
    sys.exit(main())
