"""Extract one PSO file from an archive by offset, following 64 KB chunks that are either zlib or stored raw.

The PSO's own section headers give its total length, so extraction stops exactly at the end of the file.
"""

import argparse
import struct
import sys
import zlib
from pathlib import Path

from pso_survey import SECTION_TAGS

CHUNK = 0x10000
ALIGNMENT = 16
ZLIB_SECOND_BYTES = (0x01, 0x5E, 0x9C, 0xDA)
READ_SLACK = 0x12000


class ExtractError(ValueError):
    pass


def total_length(data: bytes) -> int | None:
    """Return the PSO length once every section header up to the end is available, else None."""
    cursor = 0
    while True:
        if cursor == len(data):
            return cursor

        if cursor + 8 > len(data):
            return None

        tag = data[cursor:cursor + 4]
        if tag not in SECTION_TAGS:
            return cursor if cursor else None

        size = struct.unpack_from(">I", data, cursor + 4)[0]
        if size < 8:
            raise ExtractError(f"Section {tag!r} at 0x{cursor:x} has size {size}")

        if cursor + size > len(data):
            return None

        cursor += size


def read_chunk(handle, position: int) -> tuple[bytes, int, str]:
    handle.seek(position)
    blob = handle.read(READ_SLACK)
    if len(blob) >= 2 and blob[0] == 0x78 and blob[1] in ZLIB_SECOND_BYTES:
        decompressor = zlib.decompressobj()
        try:
            content = decompressor.decompress(blob)
        except zlib.error:
            content = b""

        if content and decompressor.eof:
            return content, len(blob) - len(decompressor.unused_data), "zlib"

    return blob[:CHUNK], CHUNK, "raw"


def extract(archive: Path, offset: int, max_chunks: int) -> tuple[bytes, list[str]]:
    data = bytearray()
    kinds = []
    position = offset
    with archive.open("rb") as handle:
        for _ in range(max_chunks):
            content, consumed, kind = read_chunk(handle, position)
            data += content
            kinds.append(kind)
            length = total_length(bytes(data))
            if length is not None:
                return bytes(data[:length]), kinds

            if len(content) != CHUNK:
                raise ExtractError(f"Short chunk ({len(content)} bytes) at 0x{position:x} before the PSO ended")

            position = (position + consumed + ALIGNMENT - 1) // ALIGNMENT * ALIGNMENT

    raise ExtractError(f"PSO did not end within {max_chunks} chunks")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("offset", type=lambda text: int(text, 0))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-chunks", type=int, default=400)
    args = parser.parse_args()

    if not args.archive.is_file():
        print(f"Not a file: {args.archive}", file=sys.stderr)
        return 1

    try:
        data, kinds = extract(args.archive, args.offset, args.max_chunks)
    except ExtractError as error:
        print(f"Extraction failed: {error}", file=sys.stderr)
        return 1

    args.out.write_bytes(data)
    print(f"{args.out.name}: bytes={len(data)} chunks={len(kinds)} raw_chunks={kinds.count('raw')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
