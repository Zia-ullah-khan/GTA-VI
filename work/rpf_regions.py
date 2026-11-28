"""Read-only region mapper: finds non-zero data runs in an archive and classifies them."""

import argparse
import math
import re
import sys
import zlib
from collections import Counter
from pathlib import Path

BLOCK_SIZE = 0x1000
SAMPLE_SIZE = 0x10000
KNOWN_MAGICS = {
    b"RSC": "RAGE resource (RSC*)",
    b"9FPR": "nested RPF9",
    b"8FPR": "nested RPF8",
    b"PSIN": "PSO metadata",
    b"RBF0": "RBF metadata",
    b"<?xm": "XML",
    b"2TXG": "GXT2 text table",
    b"\x78\x9c": "zlib stream",
    b"\x78\xda": "zlib stream",
    b"\x8c\x06": "Oodle Kraken block",
    b"\x8c\x0a": "Oodle Mermaid block",
    b"\x28\xb5\x2f\xfd": "Zstandard frame",
}
PRINTABLE_RUN = re.compile(rb"[\x20-\x7e]{6,}")


def entropy(data: bytes) -> float:
    if not data:
        return 0.0

    counts = Counter(data)
    total = len(data)
    return -sum((n / total) * math.log2(n / total) for n in counts.values())


def find_runs(path: Path) -> list[tuple[int, int]]:
    runs = []
    run_start = None
    offset = 0
    with path.open("rb") as handle:
        while True:
            block = handle.read(BLOCK_SIZE)
            if not block:
                break

            is_zero = block.count(0) == len(block)
            if not is_zero and run_start is None:
                run_start = offset
            if is_zero and run_start is not None:
                runs.append((run_start, offset))
                run_start = None

            offset += len(block)

    if run_start is not None:
        runs.append((run_start, offset))

    return runs


def identify_magic(sample: bytes) -> str:
    for magic, label in KNOWN_MAGICS.items():
        if sample.startswith(magic):
            return label

    return "unrecognized"


def compressibility(sample: bytes) -> float:
    if not sample:
        return 1.0

    return len(zlib.compress(sample, 6)) / len(sample)


def describe_run(path: Path, start: int, end: int) -> str:
    with path.open("rb") as handle:
        handle.seek(start)
        sample = handle.read(min(SAMPLE_SIZE, end - start))

    strings = PRINTABLE_RUN.findall(sample)
    head = " ".join(f"{b:02x}" for b in sample[:16])
    return (
        f"0x{start:010x}..0x{end:010x} size={end - start:>12} "
        f"entropy={entropy(sample):.3f} zlib_ratio={compressibility(sample):.3f} "
        f"ascii_runs={len(strings):>4} magic={identify_magic(sample)} head=[{head}]"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--max-runs", type=int, default=60)
    args = parser.parse_args()

    if not args.path.is_file():
        print(f"Not a file: {args.path}", file=sys.stderr)
        return 1

    runs = find_runs(args.path)
    print(f"file: {args.path} size={args.path.stat().st_size} nonzero_runs={len(runs)}")
    for start, end in runs[:args.max_runs]:
        print(describe_run(args.path, start, end))

    if len(runs) > args.max_runs:
        print(f"... {len(runs) - args.max_runs} more runs not shown")

    return 0


if __name__ == "__main__":
    sys.exit(main())
