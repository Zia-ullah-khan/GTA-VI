"""Name unnamed IDs from the story lists by hashing ID-shaped candidates built from tokens already in the dump.

Candidates are PREFIX_TOKEN[_TOKEN] strings assembled from CMissions ID tokens and manifest file-name tokens, plus
known IDs extended or shortened by one token. A name is reported only on an exact joaat match.
"""

import argparse
import json
import sys
from pathlib import Path

from decomp_common import joaat, load_mission_hashes


def tokens_of(names: list[str]) -> tuple[set[str], set[str]]:
    prefixes = set()
    tokens = set()
    for name in names:
        parts = [part for part in name.upper().replace("-", "_").split("_") if part]
        if not parts:
            continue

        prefixes.add(parts[0])
        tokens.update(parts)

    return prefixes, tokens


def candidates(mission_ids: list[str], manifest_names: list[str]) -> set[str]:
    prefixes, tokens = tokens_of(mission_ids)
    _, manifest_tokens = tokens_of(manifest_names)
    pool = tokens | manifest_tokens
    found = set(name.upper() for name in manifest_names)
    for prefix in prefixes:
        for token in pool:
            found.add(f"{prefix}_{token}")
            for second in tokens:
                found.add(f"{prefix}_{token}_{second}")

    for name in mission_ids:
        parts = name.split("_")
        for cut in range(1, len(parts)):
            found.add("_".join(parts[:cut]))

        for token in pool:
            found.add(f"{name}_{token}")

    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("missions_json", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("hashes", nargs="+")
    args = parser.parse_args()

    mission_ids = list(load_mission_hashes(args.missions_json).values())
    manifest_names = [entry["name"].replace(".pso.meta", "")
                      for entry in json.loads(args.manifest.read_text(encoding="utf-8"))]
    targets = {int(text, 16) for text in args.hashes}
    pool = candidates(mission_ids, manifest_names)
    named = {}
    for candidate in pool:
        value = joaat(candidate.lower())
        if value in targets:
            named.setdefault(f"{value:08x}", []).append(candidate)

    args.out.write_text(json.dumps(named, indent=1, sort_keys=True), encoding="utf-8")
    print(f"candidates={len(pool)} targets={len(targets)} named={len(named)}")
    for key, names in sorted(named.items()):
        print(f"  {key} = {sorted(names)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
