"""Read-only carver: inflates zlib streams found at page-aligned offsets and writes them under work/carved."""

import argparse
import hashlib
import re
import sys
import zlib
from pathlib import Path

PAGE_SIZE = 0x1000
ZLIB_HEADERS = (b"\x78\x01", b"\x78\x5e", b"\x78\x9c", b"\x78\xda")
READ_CHUNK = 1 << 20
PRINTABLE_RUN = re.compile(rb"[\x20-\x7e]{5,}")


def find_candidates(path: Path) -> list[int]:
    offsets = []
    with path.open("rb") as handle:
        offset = 0
        while True:
            handle.seek(offset)
            head = handle.read(2)
            if len(head) < 2:
                break

            if head in ZLIB_HEADERS:
                offsets.append(offset)

            offset += PAGE_SIZE

    return offsets


def inflate_at(path: Path, offset: int) -> tuple[bytes, int, bool]:
    inflater = zlib.decompressobj()
    output = bytearray()
    consumed = 0
    with path.open("rb") as handle:
        handle.seek(offset)
        while not inflater.eof:
            chunk = handle.read(READ_CHUNK)
            if not chunk:
                break

            output += inflater.decompress(chunk)
            consumed += len(chunk) - len(inflater.unused_data)

    return bytes(output), consumed, inflater.eof


def summarize(data: bytes) -> str:
    strings = PRINTABLE_RUN.findall(data[:0x4000])
    preview = [s.decode("ascii") for s in strings[:8]]
    head = " ".join(f"{b:02x}" for b in data[:24])
    return f"head=[{head}] strings={preview}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    if not args.path.is_file():
        print(f"Not a file: {args.path}", file=sys.stderr)
        return 1

    args.out.mkdir(parents=True, exist_ok=True)
    for offset in find_candidates(args.path):
        try:
            data, consumed, complete = inflate_at(args.path, offset)
        except zlib.error as error:
            print(f"0x{offset:010x}: inflate failed: {error}")
            continue

        target = args.out / f"{args.path.stem}_0x{offset:010x}.bin"
        target.write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()[:16]
        print(
            f"0x{offset:010x}: compressed={consumed} inflated={len(data)} complete={complete} "
            f"sha256={digest} -> {target.name}"
        )
        print(f"    {summarize(data)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
