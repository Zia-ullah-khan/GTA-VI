"""Find extracted payloads that contain given names, either as ASCII text or as little-endian joaat hashes."""

import argparse
import struct
import sys
from pathlib import Path

from decomp_common import joaat


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("names", nargs="+")
    parser.add_argument("--min", type=int, default=2, help="minimum distinct names a file must contain")
    args = parser.parse_args()

    needles = {name: (name.encode("ascii"), struct.pack("<I", joaat(name.lower()))) for name in args.names}
    hits = []
    for path in sorted(args.directory.iterdir()):
        if not path.is_file():
            continue

        data = path.read_bytes()
        found = {name: ("text" if text in data else "hash") for name, (text, packed) in needles.items()
                 if text in data or packed in data}
        if len(found) >= args.min:
            hits.append((path, len(data), found))

    print(f"files scanned in {args.directory.name}, matches={len(hits)}")
    for path, size, found in hits:
        print(f"  {path.name} size={size} head={path.read_bytes()[:4]!r} "
              + " ".join(f"{name}:{kind}" for name, kind in found.items()))

    return 0


if __name__ == "__main__":
    sys.exit(main())
