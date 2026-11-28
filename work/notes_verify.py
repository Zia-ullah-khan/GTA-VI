"""Recompute figures quoted in the notes: chapter-source agreement and truncated PSO count."""

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mission_order", type=Path)
    parser.add_argument("pso_survey", type=Path)
    args = parser.parse_args()

    for path in (args.mission_order, args.pso_survey):
        if not path.is_file():
            print(f"Not a file: {path}", file=sys.stderr)
            return 1

    missions = json.loads(args.mission_order.read_text(encoding="utf-8"))["missions"]
    in_table = [m for m in missions if m["in_cmissions_table"]]
    comparable = [m for m in in_table if m["texture_chapter_tag"] is not None]
    agree = [m for m in comparable if m["chapter_sources_agree"]]
    untagged = [m["id"] for m in in_table if m["texture_chapter_tag"] is None]
    print(f"menu entries in table={len(in_table)} with CH tag={len(comparable)} agree={len(agree)} "
          f"disagree={len(comparable) - len(agree)} no CH tag={untagged}")

    records = json.loads(args.pso_survey.read_text(encoding="utf-8"))
    incomplete = [r for r in records if "CHKS" not in r["sections"]]
    with_lsns = [r for r in records if r["lsns"]]
    print(f"script PSO files={len(records)} with LSNS={len(with_lsns)} incomplete (no CHKS section)={len(incomplete)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
