"""Validate RBF framing hypotheses by parsing every extracted RBF0 file and reporting the success rate."""

import argparse
import sys
from collections import Counter
from pathlib import Path

from rbf_parse import RBF_MAGIC, RbfError, parse


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("extracted_dir", type=Path)
    parser.add_argument("--numeric-padding", type=int, nargs="+", default=[0, 4])
    args = parser.parse_args()

    if not args.extracted_dir.is_dir():
        print(f"Not a directory: {args.extracted_dir}", file=sys.stderr)
        return 1

    files = [p for p in sorted(args.extracted_dir.glob("*.bin")) if p.read_bytes()[:4] == RBF_MAGIC]
    for padding in args.numeric_padding:
        passed = 0
        roots = Counter()
        failures = []
        for path in files:
            try:
                root, _ = parse(path.read_bytes(), padding)
            except (RbfError, KeyError, TypeError) as error:
                failures.append((path.name, str(error)))
                continue

            passed += 1
            roots[root["name"]] += 1

        print(f"numeric_padding={padding}: parsed {passed}/{len(files)}")
        for name, message in failures[:3]:
            print(f"   fail {name}: {message}")

        if passed:
            print("   roots: " + ", ".join(f"{name}={count}" for name, count in roots.most_common(12)))

    return 0


if __name__ == "__main__":
    sys.exit(main())
