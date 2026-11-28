"""Summarize the string-literal vocabulary found by decomp_survey: keyword families and sample values."""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

KEYWORDS = ("mission", "flow", "strand", "chapter", "prereq", "unlock", "complete", "passed", "phone", "call",
            "blip", "trigger", "launch", "jason", "lucia", "replay", "checkpoint", "stat", "prog_")
IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_]{3,}$")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("survey_json", type=Path)
    parser.add_argument("missions_json", type=Path)
    parser.add_argument("--samples", type=int, default=12)
    args = parser.parse_args()

    for path in (args.survey_json, args.missions_json):
        if not path.is_file():
            print(f"Not a file: {path}", file=sys.stderr)
            return 1

    survey = json.loads(args.survey_json.read_text(encoding="utf-8"))
    strings = survey["strings"]
    mission_ids = {m["id"].upper() for m in json.loads(args.missions_json.read_text(encoding="utf-8"))}
    print(f"string literals in survey (top by frequency): {len(strings)}")

    exact = [text for text, _ in strings if text.upper() in mission_ids]
    prefixed = [text for text, _ in strings
                if any(text.upper().startswith(mission_id + "_") for mission_id in mission_ids)]
    print(f"literals equal to a mission ID: {len(exact)} {exact[:10]}")
    print(f"literals starting with a mission ID + '_': {len(prefixed)} e.g. {prefixed[:8]}")

    shapes = Counter()
    for text, _ in strings:
        if IDENTIFIER.match(text):
            shapes["identifier"] += 1
        elif " " in text:
            shapes["sentence_or_format"] += 1
        else:
            shapes["other"] += 1

    print(f"shapes: {dict(shapes)}")
    for keyword in KEYWORDS:
        matches = [(text, count) for text, count in strings if keyword in text.lower()]
        sample = "; ".join(text[:60] for text, _ in matches[:args.samples])
        print(f"{keyword:<11} n={len(matches):>4}  {sample}")

    print("most frequent literals: " + "; ".join(f"{text[:40]}={count}" for text, count in strings[:25]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
