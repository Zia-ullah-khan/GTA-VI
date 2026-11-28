"""Shared helpers for reading hash constants and function boundaries in the decompiled script sources."""

import json
import re
from pathlib import Path
from typing import Iterator

from hash_probe import joaat

HEX_CONSTANT = re.compile(r"\b0x([0-9A-Fa-f]{1,16})U?\b")
FUNCTION_HEADER = re.compile(r"^\s*public static \S+ (func_[0-9A-F]{6})\(")
SIGN_EXTENSION = 0xFFFFFFFF
MIN_HASH = 0x10000


def iter_hash_constants(line: str) -> Iterator[int]:
    """Yield 32-bit values; the decompiler prints negative hashes sign-extended to 64 bits and drops leading zeros."""
    code = line.split("//", 1)[0]
    for digits in HEX_CONSTANT.findall(code):
        value = int(digits, 16)
        if len(digits) == 16 and value >> 32 == SIGN_EXTENSION:
            value &= 0xFFFFFFFF

        if MIN_HASH <= value <= 0xFFFFFFFF:
            yield value


def load_mission_hashes(missions_json: Path) -> dict[int, str]:
    missions = json.loads(missions_json.read_text(encoding="utf-8"))
    return {joaat(mission["id"].lower()): mission["id"] for mission in missions}


def control_hashes(count: int) -> dict[int, str]:
    return {joaat(f"control_probe_{index}"): f"control_{index}" for index in range(count)}
