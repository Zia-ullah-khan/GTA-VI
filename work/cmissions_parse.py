"""Parse the extracted CMissions table into JSON and print a compact structural summary."""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ElementTree
from collections import Counter
from pathlib import Path

TEXTURE_PATTERN = re.compile(r"^GRID_(?P<size>[A-Z]+)_(?P<letter>[A-Z]+)_(?P<chapter>CH\d+|[A-Z0-9]+?)_(?P<rest>.+)$")


def parse_missions(path: Path) -> list[dict]:
    root = ElementTree.parse(path).getroot()
    missions = []
    for item in root.iter("Item"):
        mission_id = item.findtext("MissionId", default="").strip()
        texture = item.findtext("TextureName", default="").strip()
        match = TEXTURE_PATTERN.match(texture)
        missions.append({
            "index": int(item.find("UniqueMissionIndex").get("value")),
            "id": mission_id,
            "description_key": item.findtext("Description", default="").strip(),
            "texture": texture,
            "grid_size": match.group("size") if match else None,
            "grid_letter": match.group("letter") if match else None,
            "grid_chapter": match.group("chapter") if match else None,
            "texture_matches_id": bool(match) and match.group("rest") == mission_id,
            "id_prefix": mission_id.split("_", 1)[0],
        })

    return missions


def print_summary(missions: list[dict]) -> None:
    indices = [m["index"] for m in missions]
    print(f"missions={len(missions)} index_min={min(indices)} index_max={max(indices)} "
          f"unique_indices={len(set(indices))} unique_ids={len({m['id'] for m in missions})}")
    for field in ("grid_chapter", "grid_letter", "grid_size", "id_prefix"):
        counts = Counter(m[field] for m in missions)
        print(f"{field}: {dict(sorted(counts.items(), key=lambda item: str(item[0])))}")

    mismatched = [m["id"] for m in missions if not m["texture_matches_id"]]
    print(f"texture suffix differs from MissionId: {len(mismatched)} {mismatched[:12]}")
    odd_desc = [m["id"] for m in missions if m["description_key"] != f"PROG_{m['id']}_DESC_REPLAY"]
    print(f"description key not PROG_<id>_DESC_REPLAY: {len(odd_desc)} {odd_desc[:12]}")


def print_table(missions: list[dict]) -> None:
    for mission in sorted(missions, key=lambda m: m["index"]):
        print(f"{mission['index']:>4} {str(mission['grid_chapter']):<5} {str(mission['grid_letter']):<3} "
              f"{str(mission['grid_size']):<4} {mission['id']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("xml_path", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--table", action="store_true")
    args = parser.parse_args()

    if not args.xml_path.is_file():
        print(f"Not a file: {args.xml_path}", file=sys.stderr)
        return 1

    missions = parse_missions(args.xml_path)
    args.out.write_text(json.dumps(missions, indent=1), encoding="utf-8")
    print_summary(missions)
    if args.table:
        print_table(missions)

    return 0


if __name__ == "__main__":
    sys.exit(main())
