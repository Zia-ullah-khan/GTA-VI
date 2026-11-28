"""Summarize label_hash_scan.json: totals and every stream or window holding a cluster of mission key hashes."""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("scan_json", type=Path)
    args = parser.parse_args()

    if not args.scan_json.is_file():
        print(f"Not a file: {args.scan_json}", file=sys.stderr)
        return 1

    scan = json.loads(args.scan_json.read_text(encoding="utf-8"))
    totals = scan["totals"]
    print(f"raw bytes={totals['bytes']:,} zlib streams={totals['streams']:,} "
          f"inflated bytes={totals['inflated_bytes']:,} control windows={totals['control_windows']}")

    groups = defaultdict(list)
    for hit in scan["hits"]:
        groups[(hit["file"], hit["kind"], hit.get("inflated_size"), hit["distinct_keys"])].append(hit)

    for (file, kind, size, keys), hits in sorted(groups.items(), key=lambda item: -item[0][3]):
        offsets = ", ".join(f"0x{hit['offset']:x}" for hit in sorted(hits, key=lambda hit: hit["offset"])[:14])
        print(f"{file} {kind} inflated={size} distinct_keys={keys} count={len(hits)} head={hits[0].get('head')}")
        print(f"    {offsets}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
