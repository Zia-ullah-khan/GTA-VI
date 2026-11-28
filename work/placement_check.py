"""Compare the game's ordered story list with the replay-menu order and the CMissions table."""

import argparse
import sys
from pathlib import Path

from build_outputs import build_listed_missions
from flow_sources import STORY_LIST_KEY, IdResolver, load_json, load_named_list


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cmissions", type=Path, required=True)
    parser.add_argument("--progress", type=Path, required=True)
    parser.add_argument("--lists", type=Path, required=True)
    parser.add_argument("--id-names", type=Path, required=True)
    args = parser.parse_args()

    table = {entry["id"].upper(): entry for entry in load_json(args.cmissions)}
    menu = build_listed_missions(load_json(args.progress), table)
    resolver = IdResolver(load_json(args.id_names), {})
    story = [resolver.Name(item) for item in load_named_list(load_json(args.lists), STORY_LIST_KEY)["items"]]
    menu_chapter = {m["id"]: int(m["chapter_or_act"].split()[-1]) for m in menu}
    menu_ids = [m["id"] for m in menu]

    print(f"story list={len(story)} menu={len(menu_ids)} cmissions={len(table)}")
    print("menu not in story list: " + " ".join(i for i in menu_ids if i not in story))
    print("story list not in menu: " + " ".join(i for i in story if i not in menu_chapter))
    chapters = [(i, menu_chapter[i]) for i in story if i in menu_chapter]
    drops = [(a, b) for a, b in zip(chapters, chapters[1:]) if b[1] < a[1]]
    print(f"chapter decreases along story list: {drops}")
    shared = [i for i in story if i in menu_chapter]
    menu_rank = {i: n for n, i in enumerate(menu_ids)}
    inversions = [(a, b) for a, b in zip(shared, shared[1:]) if menu_rank[b] < menu_rank[a]]
    print(f"adjacent story-list pairs in opposite menu order ({len(inversions)}): {inversions}")
    placed = set(story) | set(menu_ids)
    print("cmissions rows not in either list: " + " ".join(e["id"] for e in table.values() if e["id"] not in placed))
    letters = {}
    for entry in table.values():
        letters.setdefault(entry.get("grid_letter"), []).append(entry["id"])

    for letter, ids in letters.items():
        print(f"texture letter {letter}: {len(ids)} e.g. {ids[:8]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
