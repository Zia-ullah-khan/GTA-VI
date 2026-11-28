"""Summarize gxt_scan.json: magic hits, stream counts and the leading-bytes inventory of compressed files."""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("scan_json", type=Path)
    parser.add_argument("--top", type=int, default=40)
    args = parser.parse_args()

    if not args.scan_json.is_file():
        print(f"Not a file: {args.scan_json}", file=sys.stderr)
        return 1

    reports = json.loads(args.scan_json.read_text(encoding="utf-8"))
    raw_hits = [hit for report in reports for hit in report["raw_magic_hits"]]
    print(f"files={len(reports)} bytes={sum(report['size'] for report in reports):,}")
    print(f"raw magic hits={len(raw_hits)} with plausible header={sum(hit['header_plausible'] for hit in raw_hits)}")
    print(f"zlib streams starting with the magic={sum(len(r['zlib_start_magic_hits']) for r in reports)}")
    print(f"zlib streams 16-aligned={sum(r['zlib_streams_16_aligned'] for r in reports):,} "
          f"page-aligned={sum(r['zlib_streams_page_aligned'] for r in reports):,}")

    totals = Counter()
    files = defaultdict(set)
    for report in reports:
        for entry in report["page_stream_magics"]:
            totals[entry["magic_hex"]] += entry["count"]
            files[entry["magic_hex"]].add(Path(report["file"]).name)

    for magic, count in totals.most_common(args.top):
        print(f"{count:>8} {magic} {bytes.fromhex(magic)!r:<22} {sorted(files[magic])[:5]}")

    for report in reports:
        print(f"{report['file']:<58} streams={report['zlib_streams_16_aligned']:>9,} "
              f"page={report['zlib_streams_page_aligned']:>6,} magics={report['distinct_page_stream_magics']:>5} "
              f"raw={len(report['raw_magic_hits'])}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
