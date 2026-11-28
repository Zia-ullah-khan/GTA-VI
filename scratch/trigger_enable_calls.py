"""List every call to the trigger enable/disable native (_0x480014E54CD33903) whose record ID is a known mission.

Read-only. For each call, the record ID is the nearest 32-bit constant in the lines just above the call.
Only IDs that hash-match a CMissions row or a previously recovered ID name are reported; the rest are counted.
"""

import collections
import json
import os
import re
import sys

from joaat_candidates import joaat

SCRIPTS_DIR = r"C:\Users\<user>\Downloads\americas_scripts_23_11_2026"
WORK_DIR = r"C:\Users\<user>\Downloads\GTA6.Xbox.v1.0.2.1-CYBERLEEK\work"
CALL_PATTERN = re.compile(r"Native\._0x480014E54CD33903\((.*)\);")
CONSTANT_PATTERN = re.compile(r"= (0x[0-9A-Fa-f]{5,16});")
LOOKBACK_LINES = 12


def load_mission_names():
    with open(os.path.join(WORK_DIR, "cmissions.json"), encoding="utf-8") as table_file:
        names = [row["id"] for row in json.load(table_file)]

    with open(os.path.join(WORK_DIR, "flow", "id_names.json"), encoding="utf-8") as names_file:
        for recovered in json.load(names_file).values():
            names.extend(recovered)

    return {joaat(name): name for name in names}


def find_record_id(lines, call_index):
    for index in range(call_index - 1, max(call_index - LOOKBACK_LINES, -1), -1):
        match = CONSTANT_PATTERN.search(lines[index])
        if match:
            return int(match.group(1), 16) & 0xFFFFFFFF

    return None


def scan_script(path, mission_names):
    with open(path, encoding="utf-8", errors="replace") as script_file:
        lines = script_file.readlines()

    calls = []
    unnamed = 0
    for index, line in enumerate(lines):
        match = CALL_PATTERN.search(line)
        if not match or "public static" in line:
            continue

        record_id = find_record_id(lines, index)
        name = mission_names.get(record_id)
        if name is None:
            unnamed += 1
            continue

        enable_argument = match.group(1).rsplit(",", 1)[-1].strip()
        calls.append((index + 1, name, enable_argument))

    return calls, unnamed


def main():
    mission_names = load_mission_names()
    file_names = sorted(name for name in os.listdir(SCRIPTS_DIR) if name.endswith(".ysc.cs"))
    totals = collections.Counter()

    for file_name in file_names:
        path = os.path.join(SCRIPTS_DIR, file_name)
        with open(path, "rb") as script_file:
            if b"_0x480014E54CD33903(" not in script_file.read():
                continue

        calls, unnamed = scan_script(path, mission_names)
        totals["named"] += len(calls)
        totals["unnamed"] += unnamed
        if not calls:
            continue

        print(f"== {file_name} ({len(calls)} mission calls, {unnamed} other)")
        for line_number, name, enable_argument in calls:
            print(f"   line {line_number}: {name} <- {enable_argument}")

    print(f"Calls with a mission ID: {totals['named']}; calls with another or unresolved ID: {totals['unnamed']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
