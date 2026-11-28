"""Map zlib streams in a byte range of an archive: offset, compressed length, inflated length and leading bytes."""

import argparse
import sys
import zlib
from pathlib import Path

ZLIB_SECOND_BYTES = (0x01, 0x5E, 0x9C, 0xDA)
ALIGNMENT = 16


def inflate_stream(data: bytes, position: int) -> tuple[bytes, int] | None:
    decompressor = zlib.decompressobj()
    try:
        content = decompressor.decompress(data[position:])
    except zlib.error:
        return None

    if not decompressor.eof:
        return None

    return content, len(data) - position - len(decompressor.unused_data)


def map_streams(data: bytes, base: int) -> list[dict]:
    streams = []
    position = 0
    while position + 2 <= len(data):
        if data[position] != 0x78 or data[position + 1] not in ZLIB_SECOND_BYTES:
            position += ALIGNMENT
            continue

        result = inflate_stream(data, position)
        if result is None:
            position += ALIGNMENT
            continue

        content, consumed = result
        streams.append({"offset": base + position, "compressed": consumed, "inflated": len(content),
                        "head": content[:12].hex()})
        position += (consumed + ALIGNMENT - 1) // ALIGNMENT * ALIGNMENT

    return streams


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("start", type=lambda text: int(text, 0))
    parser.add_argument("length", type=lambda text: int(text, 0))
    parser.add_argument("--min-inflated", type=int, default=0)
    args = parser.parse_args()

    if not args.archive.is_file():
        print(f"Not a file: {args.archive}", file=sys.stderr)
        return 1

    with args.archive.open("rb") as handle:
        handle.seek(args.start)
        data = handle.read(args.length)

    previous_end = None
    for stream in map_streams(data, args.start):
        if stream["inflated"] < args.min_inflated:
            continue

        gap = "" if previous_end is None else f" gap={stream['offset'] - previous_end}"
        page = " PAGE" if stream["offset"] % 0x1000 == 0 else ""
        print(f"0x{stream['offset']:09x} comp={stream['compressed']:>8} infl={stream['inflated']:>8} "
              f"head={stream['head']}{gap}{page}")
        previous_end = stream["offset"] + stream["compressed"]

    return 0


if __name__ == "__main__":
    sys.exit(main())
