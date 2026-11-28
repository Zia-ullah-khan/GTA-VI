"""Test which 64-bit hash function maps a known name to a known 64-bit value taken from game data."""

import argparse
import hashlib
import struct
import sys
import zlib

from decomp_common import joaat

MASK64 = (1 << 64) - 1


def fnv1a64(data: bytes) -> int:
    value = 0xCBF29CE484222325
    for byte in data:
        value = ((value ^ byte) * 0x100000001B3) & MASK64

    return value


def fnv164(data: bytes) -> int:
    value = 0xCBF29CE484222325
    for byte in data:
        value = ((value * 0x100000001B3) & MASK64) ^ byte

    return value


def joaat64(data: bytes) -> int:
    value = 0
    for byte in data:
        value = (value + byte) & MASK64
        value = (value + (value << 10)) & MASK64
        value ^= value >> 6

    value = (value + (value << 3)) & MASK64
    value ^= value >> 11
    return (value + (value << 15)) & MASK64


def candidates(name: str) -> dict[str, int]:
    found = {}
    for label, text in (("lower", name.lower()), ("upper", name.upper()), ("as-is", name)):
        data = text.encode("ascii")
        found[f"fnv1a64 {label}"] = fnv1a64(data)
        found[f"fnv1-64 {label}"] = fnv164(data)
        found[f"joaat64 {label}"] = joaat64(data)
        found[f"joaat32 {label}"] = joaat(text)
        found[f"crc32 {label}"] = zlib.crc32(data)
        found[f"md5 low64 {label}"] = struct.unpack("<Q", hashlib.md5(data).digest()[:8])[0]
        found[f"sha1 low64 {label}"] = struct.unpack("<Q", hashlib.sha1(data).digest()[:8])[0]

    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("value", type=lambda text: int(text, 16))
    args = parser.parse_args()

    low = args.value & 0xFFFFFFFF
    high = args.value >> 32
    matched = False
    for label, value in candidates(args.name).items():
        hit = value == args.value or value in (low, high) or (value & 0xFFFFFFFF) in (low, high)
        if hit:
            matched = True
            print(f"MATCH {label}: {value:x}")

    if not matched:
        print(f"no tested function maps {args.name!r} to {args.value:016x}")
        print(f"  joaat32(lower)={joaat(args.name.lower()):08x} fnv1a64(lower)={fnv1a64(args.name.lower().encode()):016x}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
