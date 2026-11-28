"""Test which 32-bit string hash maps known (text, hash) pairs, to identify the hash used for a set of names."""

import argparse
import sys
import zlib

MASK = 0xFFFFFFFF


def joaat_seeded(data: bytes, seed: int) -> int:
    value = seed
    for byte in data:
        value = (value + byte) & MASK
        value = (value + (value << 10)) & MASK
        value ^= value >> 6

    value = (value + (value << 3)) & MASK
    value ^= value >> 11
    return (value + (value << 15)) & MASK


def joaat_partial(data: bytes, seed: int) -> int:
    value = seed
    for byte in data:
        value = (value + byte) & MASK
        value = (value + (value << 10)) & MASK
        value ^= value >> 6

    return value


def fnv1a(data: bytes) -> int:
    value = 0x811C9DC5
    for byte in data:
        value = ((value ^ byte) * 0x01000193) & MASK

    return value


def fnv1(data: bytes) -> int:
    value = 0x811C9DC5
    for byte in data:
        value = ((value * 0x01000193) & MASK) ^ byte

    return value


def djb2(data: bytes) -> int:
    value = 5381
    for byte in data:
        value = (value * 33 + byte) & MASK

    return value


def sdbm(data: bytes) -> int:
    value = 0
    for byte in data:
        value = (byte + (value << 6) + (value << 16) - value) & MASK

    return value


FUNCTIONS = {
    "joaat": lambda data: joaat_seeded(data, 0),
    "joaat-partial": lambda data: joaat_partial(data, 0),
    "fnv1a": fnv1a,
    "fnv1": fnv1,
    "djb2": djb2,
    "sdbm": sdbm,
    "crc32": zlib.crc32,
}


def variants(text: str) -> dict[str, bytes]:
    return {"as-is": text.encode("ascii"), "lower": text.lower().encode("ascii"),
            "upper": text.upper().encode("ascii")}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pairs", nargs="+", help="text=hexhash")
    args = parser.parse_args()

    for pair in args.pairs:
        text, expected_text = pair.split("=")
        expected = int(expected_text, 16)
        matches = [f"{name}/{case}" for name, function in FUNCTIONS.items()
                   for case, data in variants(text).items() if function(data) == expected]
        shown = ", ".join(matches) if matches else "no match"
        print(f"{text} -> {expected:08x}: {shown} (joaat lower={joaat_seeded(text.lower().encode(), 0):08x})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
