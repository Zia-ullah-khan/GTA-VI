"""Read-only RPF9 payload extractor.

The name table is encrypted, so files are located structurally: payloads begin on 0x1000 page boundaries and
large files continue as 16-byte-aligned zlib chunks that each inflate to exactly 0x10000 bytes.
"""

import argparse
import hashlib
import json
import sys
import zlib
from dataclasses import asdict, dataclass
from pathlib import Path

PAGE_SIZE = 0x1000
CHUNK_ALIGN = 0x10
FULL_CHUNK = 0x10000
ZLIB_HEADERS = (b"\x78\x01", b"\x78\x5e", b"\x78\x9c", b"\x78\xda")
RPF_MAGIC = b"9FPR"
READ_WINDOW = 1 << 20


@dataclass
class Payload:
    offset: int
    kind: str
    stored_size: int
    inflated_size: int
    chunks: int
    magic: str
    sha256: str
    output: str


def inflate_chunk(blob: bytes, start: int) -> tuple[bytes, int]:
    inflater = zlib.decompressobj()
    output = inflater.decompress(blob[start:start + READ_WINDOW])
    if not inflater.eof:
        raise zlib.error("stream did not terminate inside read window")

    consumed = min(READ_WINDOW, len(blob) - start) - len(inflater.unused_data)
    return output, consumed


def align_up(value: int, alignment: int) -> int:
    return (value + alignment - 1) // alignment * alignment


def read_zlib_file(blob: bytes, start: int) -> tuple[bytes, int, int]:
    parts = []
    cursor = start
    chunks = 0
    while blob[cursor:cursor + 2] in ZLIB_HEADERS:
        try:
            part, consumed = inflate_chunk(blob, cursor)
        except zlib.error:
            break

        parts.append(part)
        chunks += 1
        cursor = align_up(cursor + consumed, CHUNK_ALIGN)
        if len(part) != FULL_CHUNK:
            break

    return b"".join(parts), cursor, chunks


def magic_label(data: bytes) -> str:
    head = data[:4]
    if len(head) == 4 and all(32 <= b < 127 for b in head):
        return head.decode("ascii")

    return "hex:" + head.hex()


def next_nonzero_page(blob: bytes, cursor: int) -> int:
    cursor = align_up(cursor, PAGE_SIZE)
    zero_page = bytes(PAGE_SIZE)
    while cursor < len(blob) and blob[cursor:cursor + PAGE_SIZE] in (zero_page, zero_page[:len(blob) - cursor]):
        cursor += PAGE_SIZE

    return cursor


def opaque_end(blob: bytes, start: int) -> int:
    cursor = start + PAGE_SIZE
    zero_page = bytes(PAGE_SIZE)
    while cursor < len(blob):
        page = blob[cursor:cursor + PAGE_SIZE]
        if page == zero_page[:len(page)] or page[:2] in ZLIB_HEADERS or page[:4] == RPF_MAGIC:
            break

        cursor += PAGE_SIZE

    return min(cursor, len(blob))


def extract(path: Path, out_dir: Path) -> list[Payload]:
    blob = path.read_bytes()
    payloads = []
    cursor = 0
    while cursor < len(blob):
        cursor = next_nonzero_page(blob, cursor)
        if cursor >= len(blob):
            break

        data, end, chunks = read_zlib_file(blob, cursor)
        if chunks > 0:
            name = f"{path.stem}_{cursor:010x}.bin"
            (out_dir / name).write_bytes(data)
            payloads.append(Payload(cursor, "zlib", end - cursor, len(data), chunks, magic_label(data),
                                    hashlib.sha256(data).hexdigest(), name))
            cursor = end
            continue

        end = opaque_end(blob, cursor)
        kind = "rpf9_header" if blob[cursor:cursor + 4] == RPF_MAGIC else "opaque"
        region = blob[cursor:end]
        payloads.append(Payload(cursor, kind, end - cursor, 0, 0, magic_label(region),
                                hashlib.sha256(region).hexdigest(), ""))
        cursor = end

    return payloads


def print_summary(path: Path, payloads: list[Payload]) -> None:
    totals = {}
    for payload in payloads:
        count, stored, inflated = totals.get(payload.kind, (0, 0, 0))
        totals[payload.kind] = (count + 1, stored + payload.stored_size, inflated + payload.inflated_size)

    print(f"{path} size={path.stat().st_size}")
    for kind, (count, stored, inflated) in sorted(totals.items()):
        print(f"  {kind:<12} count={count:>5} stored={stored:>10} inflated={inflated:>10}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    if not args.path.is_file():
        print(f"Not a file: {args.path}", file=sys.stderr)
        return 1

    args.out.mkdir(parents=True, exist_ok=True)
    payloads = extract(args.path, args.out)
    manifest = args.out / f"{args.path.stem}_manifest.json"
    manifest.write_text(json.dumps([asdict(p) for p in payloads], indent=1), encoding="utf-8")
    print_summary(args.path, payloads)
    print(f"  manifest: {manifest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
