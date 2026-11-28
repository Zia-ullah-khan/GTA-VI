"""Scan dump files for GXT2 text containers, both raw and at the start of zlib streams, without modifying them.

Raw scan: every byte offset is checked for the magics. zlib scan: every 16-byte-aligned zlib header is inflated
for its first bytes, so a container that starts a compressed file is found, and the leading 4 bytes of every
page-aligned stream are counted to inventory the file types present.
"""

import argparse
import json
import struct
import sys
import time
import zlib
from collections import Counter
from pathlib import Path

import numpy as np

MAGICS = (b"GXT2", b"2TXG")
ZLIB_SECOND_BYTES = (0x01, 0x5E, 0x9C, 0xDA)
CHUNK_SIZE = 64 * 1024 * 1024
LOOKAHEAD = 4096
ALIGNMENT = 16
PAGE = 0x1000
PEEK_INPUT = 2048
PEEK_OUTPUT = 64
MAX_SAMPLES = 6
MAX_RAW_HITS = 200


def find_all(data: bytes, pattern: bytes, limit: int) -> list[int]:
    hits = []
    position = data.find(pattern)
    while position != -1 and position < limit:
        hits.append(position)
        position = data.find(pattern, position + 1)

    return hits


def gxt2_header_plausible(data: bytes, position: int) -> bool:
    """GXT2: magic, u32 count, count x (hash, offset), magic again."""
    if position + 8 > len(data):
        return False

    for endian in ("<", ">"):
        count = struct.unpack_from(endian + "I", data, position + 4)[0]
        second = position + 8 + count * 8
        if 0 < count < 2_000_000 and second + 4 <= len(data) and data[second:second + 4] in MAGICS:
            return True

    return False


def zlib_candidates(view: np.ndarray) -> np.ndarray:
    first = view[0::ALIGNMENT]
    second = view[1::ALIGNMENT]
    count = min(len(first), len(second))
    mask = (first[:count] == 0x78) & np.isin(second[:count], ZLIB_SECOND_BYTES)
    return np.nonzero(mask)[0] * ALIGNMENT


def peek_inflate(data: bytes, position: int) -> bytes:
    try:
        return zlib.decompressobj().decompress(data[position:position + PEEK_INPUT], PEEK_OUTPUT)
    except zlib.error:
        return b""


class FileScan:
    def __init__(self, path: Path):
        self.path = path
        self.raw_hits = []
        self.zlib_hits = []
        self.zlib_streams = 0
        self.page_streams = 0
        self.page_magics = Counter()
        self.samples = {}

    def scan_chunk(self, data: bytes, base: int, body: int) -> None:
        for magic in MAGICS:
            for position in find_all(data, magic, body):
                if len(self.raw_hits) < MAX_RAW_HITS:
                    self.raw_hits.append({"offset": base + position, "magic": magic.decode(),
                                          "header_plausible": gxt2_header_plausible(data, position),
                                          "context": data[position:position + 24].hex()})

        view = np.frombuffer(data, dtype=np.uint8, count=body)
        for position in zlib_candidates(view).tolist():
            head = peek_inflate(data, position)
            if len(head) < 4:
                continue

            self.zlib_streams += 1
            offset = base + position
            if head[:4] in MAGICS:
                self.zlib_hits.append({"offset": offset, "inflated_head": head[:32].hex()})

            if offset % PAGE:
                continue

            self.page_streams += 1
            magic = head[:4].hex()
            self.page_magics[magic] += 1
            samples = self.samples.setdefault(magic, [])
            if len(samples) < MAX_SAMPLES:
                samples.append(offset)

    def run(self, log) -> None:
        size = self.path.stat().st_size
        started = time.time()
        with self.path.open("rb") as handle:
            base = 0
            while base < size:
                handle.seek(base)
                data = handle.read(CHUNK_SIZE + LOOKAHEAD)
                body = min(CHUNK_SIZE, len(data))
                self.scan_chunk(data, base, body)
                base += body
                if (base // CHUNK_SIZE) % 32 == 0:
                    log(f"  {self.path.name} {base / size:6.1%} {base / max(time.time() - started, 0.01) / 1e6:7.0f} MB/s")

    def report(self, root: Path) -> dict:
        top = self.page_magics.most_common(60)
        return {
            "file": str(self.path.relative_to(root)),
            "size": self.path.stat().st_size,
            "raw_magic_hits": self.raw_hits,
            "zlib_start_magic_hits": self.zlib_hits,
            "zlib_streams_16_aligned": self.zlib_streams,
            "zlib_streams_page_aligned": self.page_streams,
            "distinct_page_stream_magics": len(self.page_magics),
            "page_stream_magics": [{"magic_hex": magic, "ascii": bytes.fromhex(magic).decode("latin-1"),
                                    "count": count, "sample_offsets": self.samples[magic]} for magic, count in top],
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--ext", nargs="+", default=[".rpf", ".bin"])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--exclude", nargs="*", default=["work", "output"])
    args = parser.parse_args()

    if not args.root.is_dir():
        print(f"Not a directory: {args.root}", file=sys.stderr)
        return 1

    extensions = {extension.lower() for extension in args.ext}
    files = sorted((path for path in args.root.rglob("*")
                    if path.is_file() and path.suffix.lower() in extensions
                    and path.relative_to(args.root).parts[0] not in args.exclude),
                   key=lambda path: path.stat().st_size)

    reports = []
    with args.log.open("w", encoding="utf-8") as log_handle:
        def log(message: str) -> None:
            log_handle.write(message + "\n")
            log_handle.flush()

        log(f"Scanning {len(files)} files, {sum(path.stat().st_size for path in files) / 1e9:.1f} GB")
        for path in files:
            scan = FileScan(path)
            scan.run(log)
            report = scan.report(args.root)
            reports.append(report)
            args.out.write_text(json.dumps(reports, indent=1), encoding="utf-8")
            log(f"Done {report['file']} raw_hits={len(scan.raw_hits)} zlib_hits={len(scan.zlib_hits)} "
                f"streams={scan.zlib_streams} page_streams={scan.page_streams}")

        log("Scan complete")

    return 0


if __name__ == "__main__":
    sys.exit(main())
