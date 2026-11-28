"""Count how often the joaat hashes of candidate words occur as constants in the decompiled scripts.

A word is only credible if it is hit while equally many random control words are not, so the control count is
always reported next to the result.
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from decomp_common import FUNCTION_HEADER, iter_hash_constants
from hash_probe import joaat


def load_words(paths: list[Path]) -> list[str]:
    words = set()
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            word = line.strip()
            if word and not word.startswith("#"):
                words.add(word.lower())

    return sorted(words)


def scan(source_dir: Path, names: dict[int, str]) -> dict[str, dict[str, list[list]]]:
    index = defaultdict(lambda: defaultdict(list))
    for path in sorted(source_dir.glob("*.ysc.cs")):
        function = "<none>"
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for number, line in enumerate(handle, start=1):
                header = FUNCTION_HEADER.match(line)
                if header:
                    function = header.group(1)
                    continue

                if "0x" not in line:
                    continue

                for value in iter_hash_constants(line):
                    name = names.get(value)
                    if name:
                        index[name][path.name].append([function, number])

    return index


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("wordlists", type=Path, nargs="+")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--top", type=int, default=80)
    args = parser.parse_args()

    for path in args.wordlists:
        if not path.is_file():
            print(f"Not a file: {path}", file=sys.stderr)
            return 1

    words = load_words(args.wordlists)
    names = {joaat(word): word for word in words}
    controls = {joaat(f"zq_control_word_{index}"): f"control_{index}" for index in range(len(words))}
    names.update({value: name for value, name in controls.items() if value not in names})

    index = scan(args.source_dir, names)
    hits = Counter({name: sum(len(refs) for refs in files.values()) for name, files in index.items()})
    control_words = [name for name in hits if name.startswith("control_")]
    real = [(name, count) for name, count in hits.most_common() if not name.startswith("control_")]
    args.out.write_text(json.dumps({name: files for name, files in index.items()}, indent=1), encoding="utf-8")

    print(f"words={len(words)} words hit={len(real)} control words hit={len(control_words)} "
          f"control hits={sum(hits[name] for name in control_words)}")
    for name, count in real[:args.top]:
        print(f"  {count:>6} hits {len(index[name]):>4} files  {name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
