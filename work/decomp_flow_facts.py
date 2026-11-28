"""Verify hand-read flow facts against the decompiled sources and write them as machine-checked evidence.

Every fact cites a file, function and line. A fact is only emitted if that line really contains the joaat hash of
the mission ID it names, so the citations cannot drift from the source.
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from decomp_common import iter_hash_constants, load_mission_hashes
from decomp_switch_set import EQUALITY
from decomp_annotate import find_function

CONTROLLER = "0xD2601E252151E04B.ysc.cs"
STORY = "story000.ysc.cs"
CENTRAL_SCRIPTS = {CONTROLLER, STORY, "shared.ysc.cs", "native.ysc.cs"}
FLAG_STORE = "Virtual.type_37658EE3464E5234"

HANDLER_FACTS = [
    ("MTL_WAKE", 572964, "set", "FT_KMODSHP_SECOND", 572975, None),
    ("MTL_WAKE", 572964, "set", "COM_KBOS_SHOP", 572979, None),
    ("MTL_WAKE", 572964, "set", "COM_KBOS_COLAT", 572983, None),
    ("MTL_WAKE", 572964, "set", "COM_KBOS_RADR", 572987, None),
    ("MTL_WAKE", 572964, "set", "COM_KBOS_NEIGHB", 572991, None),
    ("MTL_WAKE", 572964, "set", "COM_KBOS_CLEAN", 572995, None),
    ("MTL_WAKE", 572964, "set", "HO_PAR_KEYCO", 572999, None),
    ("MTL_WAKE", 572964, "set", "RecoverDropTipShackDonnieAlive", 573003, None),
    ("MTL_WAKE", 572964, "set", "RecoverDropTipShackDonnieDeadUnknown", 573007, None),
    ("MNY_HOTEL", 572946, "set", "ANT_SRCH", 573013, None),
    ("MNY_HOTEL", 572946, "set", "ANT_CHASE", 573043,
     [("ANT_CHASE_AUTOLAUNCH", 573017), ("ANT_CHASE", 573030)]),
    ("MNY_HOTEL", 572946, "set", "ANT_INTRO_APARTMENT", 573075,
     [("ANT_INTRO_APARTMENT", 573049), ("ANT_INTRO_STORAGE", 573062)]),
    ("MNY_HOTEL", 572946, "set", "ANT_RECOV", 573081, None),
]
SAME_BRANCH = [("MNY_HOTEL_AUTOLAUNCH", 572955, "MNY_HOTEL")]
FINISH_TESTS = [("BIL_FINALE_M", 573115), ("BIL_FINAL_B", 573127)]
TIME_VARIANTS = [("BIL_PICK_NIGHT_TIME_START", 116320), ("BIL_PICK_DAY_TIME_START", 116325)]


class LineChecker:
    def __init__(self, source_dir: Path, hashes: dict[str, int]):
        self._source_dir = source_dir
        self._hashes = hashes
        self._wanted = defaultdict(set)
        self._lines = {}

    def want(self, script: str, line: int) -> None:
        self._wanted[script].add(line)

    def load(self) -> None:
        for script, wanted in self._wanted.items():
            with (self._source_dir / script).open("r", encoding="utf-8", errors="replace") as handle:
                for number, text in enumerate(handle, start=1):
                    if number in wanted:
                        self._lines[(script, number)] = text

    def require(self, script: str, line: int, mission_id: str) -> str:
        text = self._lines.get((script, line), "")
        if self._hashes[mission_id] not in set(iter_hash_constants(text)):
            raise ValueError(f"{script}:{line} does not contain the hash of {mission_id}")

        return f"{script}:{line} (0x{self._hashes[mission_id]:08X} = joaat('{mission_id.lower()}'))"


def build_handler_facts(checker: LineChecker) -> list[dict]:
    facts = []
    for trigger, trigger_line, action, target, target_line, unless in HANDLER_FACTS:
        fact = {
            "kind": "handler_sets_flag",
            "function": "func_10AA55",
            "when_argument_equals": trigger,
            "also_when_argument_equals": [alias for alias, _, base in SAME_BRANCH if base == trigger],
            "action": f"{FLAG_STORE}.Method_0(store, id, 1)",
            "target": target,
            "only_if_neither_flag_set": [name for name, _ in unless] if unless else None,
            "evidence": [checker.require(CONTROLLER, trigger_line, trigger),
                         checker.require(CONTROLLER, target_line, target)],
        }
        for alias, alias_line, base in SAME_BRANCH:
            if base == trigger:
                fact["evidence"].append(checker.require(CONTROLLER, alias_line, alias))

        for name, line in unless or []:
            fact["evidence"].append(checker.require(CONTROLLER, line, name) + f" tested with {FLAG_STORE}.Method_1")

        facts.append(fact)

    return facts


def build_membership_fact(source_dir: Path, names: dict[int, str]) -> dict:
    tested = set()
    for _, line in find_function(source_dir / CONTROLLER, "func_109E09"):
        if EQUALITY.search(line):
            tested.update(iter_hash_constants(line))

    members = sorted(names[value] for value in tested if value in names)
    return {
        "kind": "id_membership_switch",
        "function": "func_109E09",
        "returns_1_for_mission_ids": members,
        "mission_ids_not_in_switch": sorted(set(names.values()) - set(members)),
        "other_values_in_switch": sorted(f"0x{value:08X}" for value in tested if value not in names),
        "evidence": [f"{CONTROLLER} func_109E09 (lines 570880..572796), equality tests ending in 'return 1'"],
    }


def build_script_references(refs_index: dict) -> dict[str, list[str]]:
    scripts = defaultdict(set)
    for script, functions in refs_index.items():
        if script in CENTRAL_SCRIPTS:
            continue

        for entries in functions.values():
            for _, mission_id in entries:
                scripts[mission_id].add(script.replace(".ysc.cs", ""))

    return {mission_id: sorted(names) for mission_id, names in sorted(scripts.items())}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("missions_json", type=Path)
    parser.add_argument("refs_json", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    names = load_mission_hashes(args.missions_json)
    hashes = {mission_id: value for value, mission_id in names.items()}
    checker = LineChecker(args.source_dir, hashes)
    for trigger, trigger_line, _, _, target_line, unless in HANDLER_FACTS:
        checker.want(CONTROLLER, trigger_line)
        checker.want(CONTROLLER, target_line)
        for _, line in unless or []:
            checker.want(CONTROLLER, line)

    for _, line, _ in SAME_BRANCH:
        checker.want(CONTROLLER, line)

    for _, line in FINISH_TESTS:
        checker.want(CONTROLLER, line)

    for _, line in TIME_VARIANTS:
        checker.want(STORY, line)

    checker.load()
    try:
        facts = build_handler_facts(checker)
        facts.append({
            "kind": "either_flag_test",
            "function": "func_10AD05",
            "returns_true_if_any_flag_set": [name for name, _ in FINISH_TESTS],
            "action": f"{FLAG_STORE}.Method_1(store, id, flag)",
            "evidence": [checker.require(CONTROLLER, line, name) for name, line in FINISH_TESTS],
        })
        facts.append({
            "kind": "complementary_enable",
            "function": "func_055F3F",
            "ids": [name for name, _ in TIME_VARIANTS],
            "action": "Native._0x480014E54CD33903(id, bool) called with a boolean and its negation; "
                      "the boolean includes an integer comparison '< 17'",
            "evidence": [checker.require(STORY, line, name) for name, line in TIME_VARIANTS],
        })
    except ValueError as error:
        print(f"Citation check failed: {error}", file=sys.stderr)
        return 1

    facts.append(build_membership_fact(args.source_dir, names))
    references = build_script_references(json.loads(args.refs_json.read_text(encoding="utf-8")))
    document = {"source_dir": str(args.source_dir), "facts": facts, "scripts_referencing_mission_id": references}
    args.out.write_text(json.dumps(document, indent=1), encoding="utf-8")

    script_count = len({script for scripts in references.values() for script in scripts})
    print(f"facts verified={len(facts)} missions with a referencing mission script={len(references)} "
          f"scripts={script_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
