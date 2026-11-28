"""Curated script facts about mission variants, gates and enables, each re-verified against the decompiled source.

A fact is kept only if every hash it relies on is found inside its cited line range; the exact lines are recorded.
"""

import argparse
import itertools
import json
import re
import sys
from pathlib import Path

from decomp_common import iter_hash_constants, joaat

CONTROLLER = "0xD2601E252151E04B.ysc.cs"
STORY = "story000.ysc.cs"
RAW_HASH = re.compile(r"^0x[0-9A-Fa-f]{8}$")

FACTS = [
    {"kind": "enables_trigger", "file": "0x2CC10383B818622E.ysc.cs", "lines": [45993, 46010],
     "ids": ["MTL_MUD"], "calls": ["_0xABB2FEE2751F2952", "_0x480014E54CD33903"],
     "statement": "If the MTL_MUD record is not enabled, this script enables it "
                  "(_0x480014E54CD33903(MTL_MUD, 1)). The same script references HO_PAR_FRINT.",
     "related_ids": ["HO_PAR_FRINT"]},
    {"kind": "time_of_day_variant", "file": STORY, "lines": [116302, 116328],
     "ids": ["BIL_PICK_NIGHT_TIME_START", "BIL_PICK_DAY_TIME_START"], "calls": ["_0x480014E54CD33903"],
     "statement": "A value compared with '< 17' selects the variant: the DAY record is enabled when the test is "
                  "true and the NIGHT record when it is false."},
    {"kind": "disables_triggers", "file": STORY, "lines": [110725, 110773],
     "ids": ["BIL_PRECI", "BIL_FINAL_B", "BIL_FINALE_M", "BIL_PENT_B_BRIAN", "BIL_PENT_M_MENDEZ"],
     "calls": ["_0x480014E54CD33903", "_0xC663AE0D5D968A80"],
     "statement": "One function disables all five records together (_0x480014E54CD33903(id, 0)) after moving "
                  "the player."},
    {"kind": "character_variant", "file": "0x35A38A0C3CB6F988.ysc.cs", "lines": [2133, 2213],
     "ids": ["ROB_BOAT_L_LUCIA", "ROB_BOAT_J_JASON"], "calls": ["_0x65F45909812A5248", "GET_CLOCK_HOURS"],
     "statement": "Two branches on an unnamed argument bind either ROB_BOAT_L_LUCIA or ROB_BOAT_J_JASON to a "
                  "ped; the LUCIA branch also reads the clock hour."},
    {"kind": "outcome_variant", "file": "0x5FCB40D75929A57C.ysc.cs", "lines": [9517, 9545],
     "ids": ["AIR_FINAL_DATA_HACK_PASSED", "AIR_FINAL_DATA_HACK_FAILED"], "calls": [],
     "statement": "A stored value compared with 0x88977441 selects AIR_FINAL_DATA_HACK_PASSED or "
                  "AIR_FINAL_DATA_HACK_FAILED."},
    {"kind": "choice_variant", "file": "0x514A96DB9A2F0242.ysc.cs", "lines": [5803, 5818],
     "ids": ["BIL_MOTEL_VIOLENT", "BIL_MOTEL_NON_VIOLENT"], "calls": [],
     "statement": "The script references both BIL_MOTEL_VIOLENT and BIL_MOTEL_NON_VIOLENT in adjacent branches. "
                  "The condition that picks one was not decoded."},
    {"kind": "finish_test", "file": CONTROLLER, "lines": [573098, 573136],
     "ids": ["BIL_FINALE_M", "BIL_FINAL_B"], "calls": ["Virtual.type_37658EE3464E5234.Method_1"],
     "statement": "func_10AD05 returns true when the flag store contains BIL_FINALE_M or BIL_FINAL_B."},
    {"kind": "required_player_check", "file": CONTROLLER, "lines": [635272, 635323],
     "ids": ["0xDB880157", "0x4E21D02A", "0x56D7FE7A", "0xD058819F", "0x072B3FF4"],
     "calls": ["_0xD4D69ABE605E6C2A", "GET_PLAYER_INDEX"],
     "statement": "Record property 0xDB880157 is read; value 0x4E21D02A is tested against the current player "
                  "being player_lucia (0xD058819F) and value 0x56D7FE7A against player_jason (0x072B3FF4). "
                  "A mismatch sets an output flag."},
    {"kind": "hour_properties_read", "file": "0x947D998BD81F7AC1.ysc.cs", "lines": [89983, 89999],
     "ids": ["0x1FD5BB99", "0xB376AD2B"], "calls": ["Virtual.type_B25CBCA46B3B2D61.Method_0"],
     "statement": "Record properties 0x1FD5BB99 and 0xB376AD2B are read into adjacent fields of one structure."},
]


class VerificationError(ValueError):
    pass


def hash_of(identifier: str) -> int:
    return int(identifier, 16) if RAW_HASH.match(identifier) else joaat(identifier.lower())


def read_range(path: Path, first: int, last: int) -> list[tuple[int, str]]:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return list(enumerate(itertools.islice(handle, first - 1, last), start=first))


def verify(fact: dict, source_dir: Path) -> dict:
    path = source_dir / fact["file"]
    if not path.is_file():
        raise VerificationError(f"Missing script {fact['file']}")

    first, last = fact["lines"]
    lines = read_range(path, first, last)
    found = {}
    for identifier in fact["ids"]:
        wanted = hash_of(identifier)
        hits = [number for number, line in lines if wanted in set(iter_hash_constants(line))]
        if not hits:
            raise VerificationError(f"{fact['file']}:{first}-{last} has no constant for {identifier}")

        found[identifier] = hits

    for call in fact["calls"]:
        if not any(call in line for _, line in lines):
            raise VerificationError(f"{fact['file']}:{first}-{last} has no call to {call}")

    evidence = [f"{fact['file']}:{number} ({identifier} = 0x{hash_of(identifier):08X})"
                for identifier, numbers in found.items() for number in numbers]
    return {"kind": fact["kind"], "ids": [i for i in fact["ids"] if not RAW_HASH.match(i)],
            "related_ids": fact.get("related_ids", []), "statement": fact["statement"],
            "file": fact["file"], "line_range": fact["lines"], "evidence": evidence}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    try:
        verified = [verify(fact, args.source_dir) for fact in FACTS]
    except VerificationError as error:
        print(f"Verification failed: {error}", file=sys.stderr)
        return 1

    args.out.write_text(json.dumps(verified, indent=1), encoding="utf-8")
    print(f"{args.out.name}: facts verified={len(verified)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
