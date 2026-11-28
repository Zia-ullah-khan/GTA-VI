"""List printable strings in a PSO file, flagging which are known mission IDs, with section offsets for context."""

import argparse
import json
import re
import struct
import sys
from collections import Counter
from pathlib import Path

ASCII_RUN = re.compile(rb"[A-Za-z0-9_\-./ ]{4,}")
SECTION_TAGS = (b"PSIN", b"LSCH", b"LENM", b"LSNS", b"LGID", b"LRSC", b"CHKS", b"STRF", b"STRS", b"STRE", b"PMAP")


def section_map(data: bytes) -> list[tuple[str, int, int]]:
    sections = []
    cursor = 0
    while cursor + 8 <= len(data) and data[cursor:cursor + 4] in SECTION_TAGS:
        size = struct.unpack_from(">I", data, cursor + 4)[0]
        if size < 8:
            break

        sections.append((data[cursor:cursor + 4].decode("ascii"), cursor, size))
        cursor += size

    return sections


def section_of(offset: int, sections: list[tuple[str, int, int]]) -> str:
    for tag, start, size in sections:
        if start <= offset < start + size:
            return tag

    return "?"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("missions_json", type=Path)
    parser.add_argument("--limit", type=int, default=60)
    args = parser.parse_args()

    for path in (args.path, args.missions_json):
        if not path.is_file():
            print(f"Not a file: {path}", file=sys.stderr)
            return 1

    data = args.path.read_bytes()
    mission_ids = {m["id"] for m in json.loads(args.missions_json.read_text(encoding="utf-8"))}
    sections = section_map(data)
    print("sections: " + ", ".join(f"{tag}@0x{start:x}+0x{size:x}" for tag, start, size in sections))

    strings = [(m.start(), m.group().decode("ascii")) for m in ASCII_RUN.finditer(data)]
    by_section = Counter(section_of(offset, sections) for offset, _ in strings)
    mission_strings = [(offset, text) for offset, text in strings if text in mission_ids]
    print(f"strings={len(strings)} by_section={dict(by_section)} exact_mission_ids={len(mission_strings)}")

    identifier_like = [(offset, text) for offset, text in strings if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{5,}", text)]
    print(f"identifier-like strings={len(identifier_like)}; first {args.limit}:")
    for offset, text in identifier_like[:args.limit]:
        flag = "*" if text in mission_ids else " "
        print(f"   0x{offset:06x} {section_of(offset, sections):<4} {flag} {text}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
