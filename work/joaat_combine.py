"""Match PascalCase word combinations against the schema hashes of a PSO file (case-sensitive joaat).

Vectorised with numpy so three-word names are affordable. The expected number of chance matches is printed, and
--targets restricts matching to specific hashes so long combinations stay statistically meaningful.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from joaat_match import collect_schema_targets

MASK = np.uint32(0xFFFFFFFF)


def extend(states: np.ndarray, word: str) -> np.ndarray:
    value = states.copy()
    for byte in word.encode("ascii"):
        value += np.uint32(byte)
        value += value << np.uint32(10)
        value ^= value >> np.uint32(6)

    return value


def finalise(states: np.ndarray) -> np.ndarray:
    value = states + (states << np.uint32(3))
    value ^= value >> np.uint32(11)
    return value + (value << np.uint32(15))


def search(vocabulary: list[str], last_words: list[str], depth: int, targets: np.ndarray) -> list[tuple[int, str]]:
    """Names are (depth - 1) vocabulary words followed by one word from last_words."""
    states = np.zeros(1, dtype=np.uint32)
    prefixes = [""]
    for _ in range(depth - 1):
        states = np.concatenate([extend(states, word) for word in vocabulary])
        prefixes = [prefix + word for word in vocabulary for prefix in prefixes]

    found = []
    for word in last_words:
        hashes = finalise(extend(states, word))
        for index in np.nonzero(np.isin(hashes, targets))[0]:
            found.append((int(hashes[index]), prefixes[index] + word))

    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pso", type=Path)
    parser.add_argument("--words", type=Path, required=True)
    parser.add_argument("--last", type=Path, help="vocabulary for the final word (default: same as --words)")
    parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--targets", nargs="*", help="restrict to these hex hashes")
    parser.add_argument("--known", type=Path, nargs="*", default=[], help="JSON {hash: name} files to skip")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    schema = collect_schema_targets(args.pso.read_bytes())
    known = {int(key, 16) for path in args.known for key in json.loads(path.read_text(encoding="utf-8"))}
    wanted = {int(text, 16) for text in args.targets} if args.targets else set(schema) - known
    vocabulary = list(dict.fromkeys(args.words.read_text(encoding="utf-8").split()))
    last_words = vocabulary if args.last is None else list(dict.fromkeys(args.last.read_text(encoding="utf-8").split()))

    with np.errstate(over="ignore"):
        found = search(vocabulary, last_words, args.depth, np.array(sorted(wanted), dtype=np.uint32))

    for value, name in sorted(found):
        print(f"{value:08x} {name} [{schema.get(value, 'target')}]")

    candidates = len(vocabulary) ** (args.depth - 1) * len(last_words)
    print(f"candidates={candidates} matched={len(found)} targets={len(wanted)} "
          f"expected chance matches={candidates * len(wanted) / 2 ** 32:.3f}")
    if args.out is not None:
        args.out.write_text(json.dumps({f"{value:08x}": name for value, name in found}, indent=1, sort_keys=True),
                            encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
