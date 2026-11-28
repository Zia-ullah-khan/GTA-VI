"""Name raw joaat hashes by hashing candidate words (wordlists, manifest file names, simple affix variants).

A name is only reported when its joaat equals the target hash exactly; nothing is guessed.
"""

import argparse
import json
import sys
from pathlib import Path

from decomp_common import joaat

PREFIXES = ("", "player_", "cs_", "ig_", "char_", "contact_", "blip_", "is_", "story_", "mission_", "flow_")
SUFFIXES = ("", "_only", "s", "_id", "_name", "_hash", "_blip", "_contact", "_mission", "_missions")


def load_words(paths: list[Path], manifest: Path | None) -> set[str]:
    words = set()
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            word = line.strip().lower()
            if not word:
                continue

            words.add(word)
            words.update(part for part in word.replace("-", "_").split("_") if part)

    if manifest is not None:
        for entry in json.loads(manifest.read_text(encoding="utf-8")):
            stem = entry["name"].lower().replace(".pso.meta", "")
            words.add(stem)
            words.add(entry["name"].lower())
            words.update(part for part in stem.split("_") if part)

    return words


def build_index(words: set[str], targets: set[int]) -> dict[int, list[str]]:
    found = {}
    for word in words:
        for prefix in PREFIXES:
            for suffix in SUFFIXES:
                candidate = f"{prefix}{word}{suffix}"
                value = joaat(candidate)
                if value in targets:
                    found.setdefault(value, []).append(candidate)

    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--words", type=Path, nargs="+", required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--targets", type=Path, help="text file with hex hashes separated by whitespace")
    parser.add_argument("--out", type=Path)
    parser.add_argument("hashes", nargs="*")
    args = parser.parse_args()

    texts = list(args.hashes)
    if args.targets is not None:
        texts += args.targets.read_text(encoding="utf-8").split()

    targets = {int(text, 16) for text in texts}
    words = load_words(args.words, args.manifest)
    found = build_index(words, targets)
    print(f"candidates={len(words)} targets={len(targets)} named={len(found)}")
    for value in sorted(found):
        print(f"  {value:08x} = {sorted(set(found[value]))}")

    if args.out is not None:
        document = {f"{value:08x}": sorted(set(names)) for value, names in found.items()}
        args.out.write_text(json.dumps(document, indent=1, sort_keys=True), encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
