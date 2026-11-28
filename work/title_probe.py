"""Search extracted payloads for candidate mission titles as ASCII and UTF-16LE, case-insensitively."""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

QUOTED_TITLE = re.compile(r"\*\"?([A-Z][^*\"\n]{3,40}?)\"?\*")
NUMBERED_TITLE = re.compile(r"\"\d+\.\s+([^<\"(]{4,40}?)(?:<br/>|\"|\s*\()")
MIN_TITLE_LENGTH = 8


def collect_titles(chart_path: Path) -> list[str]:
    text = chart_path.read_text(encoding="utf-8")
    titles = set()
    for pattern in (QUOTED_TITLE, NUMBERED_TITLE):
        for match in pattern.findall(text):
            title = match.strip()
            if len(title) >= MIN_TITLE_LENGTH and " " in title:
                titles.add(title)

    return sorted(titles)


def encodings(title: str) -> list[bytes]:
    variants = {title, title.upper(), title.lower(), title.replace("'", "\u2019")}
    encoded = set()
    for variant in variants:
        encoded.add(variant.encode("utf-8"))
        encoded.add(variant.encode("utf-16-le"))

    return list(encoded)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("chart", type=Path)
    parser.add_argument("extracted_dirs", type=Path, nargs="+")
    parser.add_argument("--control", nargs="+", default=["uiProgressDataset", "PROG_RECORD", "CMovieSubtitleContainer"])
    args = parser.parse_args()

    if not args.chart.is_file():
        print(f"Not a file: {args.chart}", file=sys.stderr)
        return 1

    titles = collect_titles(args.chart)
    needles = {title: encodings(title) for title in titles}
    controls = {text: encodings(text) for text in args.control}
    hits = defaultdict(set)
    control_hits = defaultdict(int)
    scanned = 0
    for directory in args.extracted_dirs:
        if not directory.is_dir():
            print(f"Not a directory: {directory}", file=sys.stderr)
            return 1

        for path in sorted(directory.glob("*.bin")):
            data = path.read_bytes()
            scanned += len(data)
            for title, variants in needles.items():
                if any(variant in data for variant in variants):
                    hits[title].add(path.name)

            for text, variants in controls.items():
                if any(variant in data for variant in variants):
                    control_hits[text] += 1

    print(f"candidate titles={len(titles)} scanned_bytes={scanned}")
    print(f"titles found in readable data: {len(hits)}")
    for title, files in sorted(hits.items()):
        print(f"   {title!r}: {sorted(files)[:3]}")

    print(f"control strings found (files): {dict(control_hits)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
