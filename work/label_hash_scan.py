"""Find text-table candidates by content instead of by header.

A localization table keyed by label hash must contain the joaat hashes of the mission text keys close together.
Every 64 KB window of raw data and every fully inflated zlib stream is checked for the number of distinct key
hashes it holds. The same number of control hashes is counted alongside to measure the chance rate.
"""

import argparse
import json
import os
import sys
import time
import zlib
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from hash_probe import joaat

SEGMENT = 128 * 1024 * 1024
LOOKAHEAD = 128 * 1024
WINDOW = 0x10000
ALIGNMENT = 16
ZLIB_SECOND_BYTES = (0x01, 0x5E, 0x9C, 0xDA)
MAX_INFLATE = 0x40000
MIN_DISTINCT = 4

_real = None
_control = None
_low_table = None


def build_key_hashes(cmissions: Path, progress: Path) -> tuple[list[int], list[int]]:
    keys = set()
    for mission in json.loads(cmissions.read_text(encoding="utf-8")):
        keys.add(mission["id"])
        keys.add(mission["description_key"])

    for category in json.loads(progress.read_text(encoding="utf-8")):
        for group in category["filters"]:
            keys.add(group["filter_label"])
            for item in group["items"]:
                keys.add(item["label"])
                keys.add("PROG_" + item["label"])

    real = sorted({joaat(key.lower()) for key in keys})
    control = sorted({joaat(f"zq_label_control_{index}") for index in range(len(real))})
    return real, control


def init_worker(real: list[int], control: list[int]) -> None:
    global _real, _control, _low_table
    _real = np.array(real, dtype=np.uint32)
    _control = np.array(control, dtype=np.uint32)
    _low_table = np.zeros(0x10000, dtype=bool)
    _low_table[np.concatenate([_real, _control]) & 0xFFFF] = True


def distinct_key_hashes(data: bytes) -> tuple[int, int]:
    real_found = set()
    control_found = set()
    usable = len(data) - 3
    if usable <= 0:
        return 0, 0

    for shift in range(4):
        count = (len(data) - shift) // 4
        values = np.frombuffer(data, dtype="<u4", count=count, offset=shift)
        candidates = values[_low_table[values & 0xFFFF]]
        if not len(candidates):
            continue

        real_found.update(candidates[np.isin(candidates, _real)].tolist())
        control_found.update(candidates[np.isin(candidates, _control)].tolist())

    return len(real_found), len(control_found)


def zlib_positions(data: bytes, body: int) -> list[int]:
    view = np.frombuffer(data, dtype=np.uint8, count=body)
    first = view[0::ALIGNMENT]
    second = view[1::ALIGNMENT]
    count = min(len(first), len(second))
    mask = (first[:count] == 0x78) & np.isin(second[:count], ZLIB_SECOND_BYTES)
    return (np.nonzero(mask)[0] * ALIGNMENT).tolist()


def inflate(data: bytes, position: int) -> bytes:
    try:
        return zlib.decompressobj().decompress(data[position:position + LOOKAHEAD], MAX_INFLATE)
    except zlib.error:
        return b""


def scan_segment(task: tuple[str, int, int]) -> dict:
    path, start, length = task
    with open(path, "rb") as handle:
        handle.seek(start)
        data = handle.read(length + LOOKAHEAD)

    body = min(length, len(data))
    hits = []
    control_windows = 0
    for offset in range(0, body, WINDOW):
        real, control = distinct_key_hashes(data[offset:offset + WINDOW + 3])
        control_windows += control >= MIN_DISTINCT
        if real >= MIN_DISTINCT:
            hits.append({"kind": "raw", "offset": start + offset, "distinct_keys": real, "distinct_controls": control})

    streams = 0
    inflated_bytes = 0
    for position in zlib_positions(data, body):
        content = inflate(data, position)
        if len(content) < 16:
            continue

        streams += 1
        inflated_bytes += len(content)
        real, control = distinct_key_hashes(content)
        control_windows += control >= MIN_DISTINCT
        if real >= MIN_DISTINCT:
            hits.append({"kind": "zlib", "offset": start + position, "inflated_size": len(content),
                         "distinct_keys": real, "distinct_controls": control, "head": content[:16].hex()})

    return {"file": path, "start": start, "bytes": body, "streams": streams, "inflated_bytes": inflated_bytes,
            "control_windows": control_windows, "hits": hits}


def build_tasks(root: Path, extensions: set[str], exclude: list[str]) -> list[tuple[str, int, int]]:
    tasks = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in extensions:
            continue

        if path.relative_to(root).parts[0] in exclude:
            continue

        size = path.stat().st_size
        tasks.extend((str(path), start, min(SEGMENT, size - start)) for start in range(0, size, SEGMENT))

    return tasks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--cmissions", type=Path, required=True)
    parser.add_argument("--progress", type=Path, required=True)
    parser.add_argument("--ext", nargs="+", default=[".rpf", ".bin"])
    parser.add_argument("--exclude", nargs="*", default=["work", "output"])
    parser.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    args = parser.parse_args()

    if not args.root.is_dir():
        print(f"Not a directory: {args.root}", file=sys.stderr)
        return 1

    real, control = build_key_hashes(args.cmissions, args.progress)
    tasks = build_tasks(args.root, {extension.lower() for extension in args.ext}, args.exclude)
    totals = {"key_hashes": len(real), "segments": len(tasks), "bytes": 0, "streams": 0, "inflated_bytes": 0,
              "control_windows": 0}
    hits = []
    started = time.time()
    with args.log.open("w", encoding="utf-8") as log, Pool(args.workers, init_worker, (real, control)) as pool:
        log.write(f"Scanning {len(tasks)} segments with {args.workers} workers, {len(real)} key hashes\n")
        log.flush()
        for done, result in enumerate(pool.imap_unordered(scan_segment, tasks), start=1):
            for key in ("bytes", "streams", "inflated_bytes", "control_windows"):
                totals[key] += result[key]

            for hit in result["hits"]:
                hit["file"] = str(Path(result["file"]).relative_to(args.root))
                hits.append(hit)

            if done % 8 == 0 or done == len(tasks):
                log.write(f"{done}/{len(tasks)} segments {totals['bytes'] / 1e9:.1f} GB raw "
                          f"{totals['inflated_bytes'] / 1e9:.1f} GB inflated hits={len(hits)} "
                          f"{time.time() - started:.0f}s\n")
                log.flush()
                args.out.write_text(json.dumps({"totals": totals, "hits": hits}, indent=1), encoding="utf-8")

        log.write("Scan complete\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
