"""
Deep analysis of func_109E09 in 0xD2601E252151E04B.ysc.cs to extract
the actual prerequisite checking pattern.

The dispatcher function appears to be a large switch-case on mission IDs.
For each mission, it checks whether certain prerequisite missions are complete
(via Method_1 = check state) and sets flags (via Method_0 = set state).
"""

import os
import re
import json
from collections import defaultdict, OrderedDict

SCRIPTS_DIR = r"C:\Users\<user>\Downloads\americas_scripts_23_11_2026"
OUTPUT_DIR = r"C:\Users\<user>\Downloads\GTA6.Xbox.v1.0.2.1-CYBERLEEK\output"
SCRATCH_DIR = r"C:\Users\<user>\.gemini\antigravity-cli\brain\96252013-4633-45e8-b6a2-59b18be9e68c\scratch"


def joaat(s):
    h = 0
    for c in s.lower().encode("utf-8"):
        h = (h + c) & 0xFFFFFFFF
        h = (h + (h << 10)) & 0xFFFFFFFF
        h = (h ^ (h >> 6)) & 0xFFFFFFFF
    h = (h + (h << 3)) & 0xFFFFFFFF
    h = (h ^ (h >> 11)) & 0xFFFFFFFF
    h = (h + (h << 15)) & 0xFFFFFFFF
    return h


def build_hash_table():
    with open(os.path.join(OUTPUT_DIR, "mission_order.json"), "r", encoding="utf-8") as f:
        order_doc = json.load(f)
    hash_to_name = {}
    name_to_meta = {}
    for m in order_doc["missions"]:
        mid = m["id"]
        hash_to_name[joaat(mid)] = mid
        name_to_meta[mid] = m.get("chapter_or_act", "?")
    for item in order_doc["cmissions_entries_not_in_replay_menu"]:
        mid = item["id"]
        hash_to_name[joaat(mid)] = mid
        if mid not in name_to_meta:
            name_to_meta[mid] = "Ch{} (table)".format(item.get("texture_chapter_tag", 0))
    return hash_to_name, name_to_meta


def analyze_dispatcher_blocks():
    """
    Read func_109E09 and parse the control flow to find:
    - Switch cases on mission IDs (compare local_0 to hash)
    - Within each case: Method_1 calls (checks) and Method_0 calls (sets)
    """
    hash_to_name, name_to_meta = build_hash_table()
    dispatcher = os.path.join(SCRIPTS_DIR, "0xD2601E252151E04B.ysc.cs")

    # Read the entire func_109E09 region
    # From decomp_mission_refs: func_109E09 covers lines ~548000..573000+
    # Let's find the exact range

    in_func = False
    func_lines = []
    start_line = 0

    with open(dispatcher, "r", encoding="utf-8", errors="ignore") as f:
        for idx, line in enumerate(f, 1):
            if "[VmFunction(0x109E09)]" in line:
                in_func = True
                start_line = idx
                continue
            if in_func:
                if line.strip().startswith("[VmFunction(") and "0x109E09" not in line:
                    break
                func_lines.append((idx, line.rstrip()))

    print("func_109E09: {} lines (starting at L{})".format(len(func_lines), start_line))

    # Parse the control flow:
    # Pattern 1: Switch dispatch - as_i32(local_0) == as_i32(0xHASH) -> goto label
    # Pattern 2: Method_0(ptr, hash, 1) = set mission state flag
    # Pattern 3: Method_1(ptr, hash, 1) = check mission state flag (returns bool)

    hash_re = re.compile(r"0x([0-9A-Fa-f]{8})")
    switch_re = re.compile(r"as_i32\(local_0\)\s*==\s*as_i32\((0x[0-9A-Fa-f]+)\)")
    switch_gt_re = re.compile(r"as_i32\(local_0\)\s*>\s*as_i32\((0x[0-9A-Fa-f]+)\)")
    method0_re = re.compile(r"Method_0\(.*?,\s*(.*?)\[0\],\s*1\)")
    method1_re = re.compile(r"Method_1\(.*?,\s*(.*?)\[0\],\s*1\)")
    store_i32_re = re.compile(r"store_i32\(.*?,\s*0x0,\s*(0x[0-9A-Fa-f]+)\)")
    label_re = re.compile(r"^(\s*label_[0-9A-Fa-f]+)\s*;")

    # Track: which hash is being switched on, and within that block, what's checked/set
    current_switch_hash = None
    current_switch_name = None
    current_block_checks = []  # Method_1 calls (prerequisite checks)
    current_block_sets = []  # Method_0 calls (state sets)
    last_stored_hash = None

    blocks = []  # (switch_name, checks, sets)

    for line_num, line in func_lines:
        # Detect switch comparison
        sw = switch_re.search(line)
        if sw:
            # Save previous block
            if current_switch_name:
                blocks.append((current_switch_name, current_switch_hash,
                               list(current_block_checks), list(current_block_sets)))
                current_block_checks = []
                current_block_sets = []

            raw_hash = int(sw.group(1), 16)
            current_switch_hash = raw_hash
            current_switch_name = hash_to_name.get(raw_hash, "UNKNOWN_0x{:08X}".format(raw_hash))
            continue

        # Detect store_i32 for hash constants
        st = store_i32_re.search(line)
        if st:
            last_stored_hash = int(st.group(1), 16)
            continue

        # Detect Method_0 (set state)
        if "Method_0(" in line and last_stored_hash:
            name = hash_to_name.get(last_stored_hash, "0x{:08X}".format(last_stored_hash))
            current_block_sets.append(name)
            last_stored_hash = None
            continue

        # Detect Method_1 (check state)
        if "Method_1(" in line and last_stored_hash:
            name = hash_to_name.get(last_stored_hash, "0x{:08X}".format(last_stored_hash))
            current_block_checks.append(name)
            last_stored_hash = None
            continue

    # Save last block
    if current_switch_name:
        blocks.append((current_switch_name, current_switch_hash,
                       list(current_block_checks), list(current_block_sets)))

    # Print analysis
    print("\n=== DISPATCHER BLOCKS (switch cases) ===")
    print("Each block: when mission X completes, it checks/sets other mission flags\n")

    dependency_edges = []

    for switch_name, switch_hash, checks, sets in blocks:
        ch = name_to_meta.get(switch_name, "?")
        if not checks and not sets:
            continue
        print("{} [{}]:".format(switch_name, ch))
        if checks:
            print("  CHECKS (prerequisites): {}".format(", ".join(checks)))
            for c in checks:
                dependency_edges.append({"from": c, "to": switch_name, "type": "check"})
        if sets:
            print("  SETS (unlocks): {}".format(", ".join(sets)))
            for s in sets:
                dependency_edges.append({"from": switch_name, "to": s, "type": "set"})
        print()

    # Save edges
    out_path = os.path.join(SCRATCH_DIR, "dispatcher_dependency_edges.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(dependency_edges, f, indent=2)
    print("Saved {} dependency edges to {}".format(len(dependency_edges), out_path))

    return blocks, dependency_edges


def analyze_func_10AA55():
    """Analyze the chapter transition handler."""
    hash_to_name, name_to_meta = build_hash_table()
    dispatcher = os.path.join(SCRIPTS_DIR, "0xD2601E252151E04B.ysc.cs")

    in_func = False
    func_lines = []

    with open(dispatcher, "r", encoding="utf-8", errors="ignore") as f:
        for idx, line in enumerate(f, 1):
            if "[VmFunction(0x10AA55)]" in line:
                in_func = True
                continue
            if in_func:
                if line.strip().startswith("[VmFunction(") and "0x10AA55" not in line:
                    break
                func_lines.append((idx, line.rstrip()))

    print("\n\n=== func_10AA55 (Chapter Transition Handler) ===")
    print("Lines: {}".format(len(func_lines)))

    store_i32_re = re.compile(r"store_i32\(.*?,\s*0x0,\s*(0x[0-9A-Fa-f]+)\)")
    switch_re = re.compile(r"as_i32\(.*?\)\s*==\s*as_i32\((0x[0-9A-Fa-f]+)\)")

    last_stored_hash = None
    for line_num, line in func_lines:
        st = store_i32_re.search(line)
        if st:
            h = int(st.group(1), 16)
            name = hash_to_name.get(h, "0x{:08X}".format(h))
            print("  L{}: store hash -> {}".format(line_num, name))

        sw = switch_re.search(line)
        if sw:
            h = int(sw.group(1), 16)
            name = hash_to_name.get(h, "0x{:08X}".format(h))
            print("  L{}: compare == {}".format(line_num, name))

        if "Method_0(" in line:
            print("  L{}: SET STATE".format(line_num))
        if "Method_1(" in line:
            print("  L{}: CHECK STATE".format(line_num))
        if "goto " in line:
            label = line.strip()
            if "goto label_" in label:
                print("  L{}: {}".format(line_num, label))


def analyze_func_24BCE4():
    """Analyze the third dispatcher function."""
    hash_to_name, name_to_meta = build_hash_table()
    dispatcher = os.path.join(SCRIPTS_DIR, "0xD2601E252151E04B.ysc.cs")

    in_func = False
    func_lines = []

    with open(dispatcher, "r", encoding="utf-8", errors="ignore") as f:
        for idx, line in enumerate(f, 1):
            if "[VmFunction(0x24BCE4)]" in line:
                in_func = True
                continue
            if in_func:
                if line.strip().startswith("[VmFunction(") and "0x24BCE4" not in line:
                    break
                func_lines.append((idx, line.rstrip()))

    print("\n\n=== func_24BCE4 (Tertiary Dispatcher) ===")
    print("Lines: {}".format(len(func_lines)))

    store_i32_re = re.compile(r"store_i32\(.*?,\s*0x0,\s*(0x[0-9A-Fa-f]+)\)")
    switch_re = re.compile(r"as_i32\(.*?\)\s*==\s*as_i32\((0x[0-9A-Fa-f]+)\)")

    for line_num, line in func_lines:
        st = store_i32_re.search(line)
        if st:
            h = int(st.group(1), 16)
            name = hash_to_name.get(h, "0x{:08X}".format(h))
            if name != "0x{:08X}".format(h):
                print("  L{}: store -> {}".format(line_num, name))

        sw = switch_re.search(line)
        if sw:
            h = int(sw.group(1), 16)
            name = hash_to_name.get(h, "0x{:08X}".format(h))
            if name != "0x{:08X}".format(h):
                print("  L{}: == {}".format(line_num, name))

        if "Method_0(" in line:
            print("  L{}: SET".format(line_num))
        if "Method_1(" in line:
            print("  L{}: CHECK".format(line_num))


if __name__ == "__main__":
    blocks, edges = analyze_dispatcher_blocks()
    analyze_func_10AA55()
    analyze_func_24BCE4()
