"""
Extract the mission dependency graph from the decompiled scripts and game data files.

Sources used (all from the game files, nothing external):
1. cmissions.xml - CMissions table with UniqueMissionIndex and MissionId
2. progress_missions.json - Replay menu layout with chapter filters and unlock_id links
3. mission_order.json - Merged mission registry with chapter assignments
4. decomp_mission_refs.json - Which decompiled scripts reference which missions
5. 0xD2601E252151E04B.ysc.cs - Master dispatcher script (func_109E09, func_12EB6F, func_24BCE4)
6. story000.ysc.cs - Story state machine
"""

import json
import os
import re
from collections import defaultdict

SCRIPTS_DIR = r"C:\Users\<user>\Downloads\americas_scripts_23_11_2026"
WORK_DIR = r"C:\Users\<user>\Downloads\GTA6.Xbox.v1.0.2.1-CYBERLEEK\work"
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
    """Build complete hash -> mission name table from all known mission IDs."""
    with open(os.path.join(OUTPUT_DIR, "mission_order.json"), "r", encoding="utf-8") as f:
        order_doc = json.load(f)

    hash_to_name = {}
    name_to_meta = {}

    for m in order_doc["missions"]:
        mid = m["id"]
        h = joaat(mid)
        hash_to_name[h] = mid
        name_to_meta[mid] = {
            "chapter": m.get("chapter_or_act", "Unknown"),
            "idx": m.get("unique_mission_index", -1),
            "pos": m.get("replay_menu_position", -1),
        }

    for item in order_doc["cmissions_entries_not_in_replay_menu"]:
        mid = item["id"]
        h = joaat(mid)
        hash_to_name[h] = mid
        if mid not in name_to_meta:
            name_to_meta[mid] = {
                "chapter": "Ch{} (Table Only)".format(item.get("texture_chapter_tag", 0)),
                "idx": item.get("unique_mission_index", -1),
                "pos": -1,
            }

    return hash_to_name, name_to_meta


def extract_dispatcher_hashes():
    """Extract all 32-bit constant hashes from the master dispatcher script."""
    dispatcher = os.path.join(SCRIPTS_DIR, "0xD2601E252151E04B.ysc.cs")

    # Pattern to find store_i32(..., 0x<HASH>) and comparisons like as_i32(0x<HASH>)
    hash_pattern = re.compile(r"0x([0-9A-Fa-f]{8})")

    # Read the file and extract hashes from the dispatcher functions
    # func_109E09 starts around line 548000+, func_12EB6F, func_24BCE4
    hashes_by_function = defaultdict(list)
    current_func = None

    line_count = 0
    with open(dispatcher, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line_count += 1
            # Track function boundaries
            func_match = re.search(r"\[VmFunction\((0x[0-9A-Fa-f]+)\)\]", line)
            if func_match:
                current_func = "func_" + func_match.group(1)[2:]  # Strip 0x prefix

            if current_func and "store_i32" in line:
                for m in hash_pattern.finditer(line):
                    val = int(m.group(1), 16)
                    # Filter out small values and obvious non-mission hashes
                    if val > 0x1000 and val != 0xFFFFFFFF:
                        hashes_by_function[current_func].append((line_count, val))

            if current_func and "as_i32" in line:
                for m in hash_pattern.finditer(line):
                    val = int(m.group(1), 16)
                    if val > 0x1000 and val != 0xFFFFFFFF:
                        hashes_by_function[current_func].append((line_count, val))

    return hashes_by_function


def extract_story000_state_checks():
    """Extract mission hash checks from story000.ysc.cs to find state transitions."""
    story_file = os.path.join(SCRIPTS_DIR, "story000.ysc.cs")

    hash_pattern = re.compile(r"0x([0-9A-Fa-f]{8})")
    checks_by_function = defaultdict(list)
    current_func = None
    line_count = 0

    with open(story_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line_count += 1
            func_match = re.search(r"\[VmFunction\((0x[0-9A-Fa-f]+)\)\]", line)
            if func_match:
                current_func = "func_" + func_match.group(1)[2:]

            if current_func and ("store_i32" in line or "as_i32" in line):
                for m in hash_pattern.finditer(line):
                    val = int(m.group(1), 16)
                    if val > 0x1000 and val != 0xFFFFFFFF:
                        checks_by_function[current_func].append((line_count, val))

    return checks_by_function


def extract_per_mission_script_dependencies():
    """
    For each mission's dedicated script, check which other mission IDs it references.
    This reveals direct dependencies (e.g., a mission script checking if another mission is complete).
    """
    with open(os.path.join(WORK_DIR, "decomp_mission_refs.json"), "r", encoding="utf-8") as f:
        refs = json.load(f)

    # Build reverse: for each script, what missions does it reference?
    # Then for each mission, what other missions does its dedicated script check?
    # We know mission X's dedicated script from the mapping (the script with most hits for that mission)

    hash_to_name, name_to_meta = build_hash_table()

    # Find the "primary" script for each mission (excludes the shared dispatcher 0xD260...)
    mission_primary_script = {}
    for script_name, func_map in refs.items():
        if script_name == "0xD2601E252151E04B.ysc.cs":
            continue
        if script_name == "shared.ysc.cs":
            continue

        missions_in_script = set()
        total_hits = 0
        for func, hit_list in func_map.items():
            for _, mid in hit_list:
                missions_in_script.add(mid)
                total_hits += 1

        # If a script predominantly references one mission, it's that mission's script
        if len(missions_in_script) == 1:
            mission = list(missions_in_script)[0]
            if mission not in mission_primary_script or total_hits > mission_primary_script[mission][1]:
                mission_primary_script[mission] = (script_name, total_hits)

    # For multi-mission scripts, assign to the one with most hits
    for script_name, func_map in refs.items():
        if script_name in ("0xD2601E252151E04B.ysc.cs", "shared.ysc.cs", "story000.ysc.cs"):
            continue

        mission_hit_count = defaultdict(int)
        for func, hit_list in func_map.items():
            for _, mid in hit_list:
                mission_hit_count[mid] += 1

        if mission_hit_count:
            top_mission = max(mission_hit_count, key=lambda m: mission_hit_count[m])
            if top_mission not in mission_primary_script:
                mission_primary_script[top_mission] = (script_name, mission_hit_count[top_mission])

    # Now, for each mission's primary script, what OTHER missions does it reference?
    dependencies = {}
    for mission, (script_name, _) in mission_primary_script.items():
        func_map = refs.get(script_name, {})
        other_missions = set()
        for func, hit_list in func_map.items():
            for _, mid in hit_list:
                if mid != mission:
                    other_missions.add(mid)
        if other_missions:
            dependencies[mission] = {
                "script": script_name,
                "references": sorted(other_missions),
            }

    return mission_primary_script, dependencies


def extract_progress_menu_dependencies():
    """
    Extract dependencies from the progress/replay menu data.
    When unlock_id != item_id, it means the mission reveals in menu only after unlock_id completes.
    """
    with open(os.path.join(WORK_DIR, "progress_missions.json"), "r", encoding="utf-8") as f:
        pm = json.load(f)

    unlock_links = []
    menu_order = {}

    for chapter_filter in pm:
        filter_id = chapter_filter.get("filter_id", "")
        items = chapter_filter.get("items", [])
        for item in items:
            label = item.get("label", "")
            item_id = item.get("item_id", "")
            unlock_id = item.get("unlock_id", "")
            pos = item.get("position", -1)

            menu_order[(filter_id, pos)] = label

            # When unlock_id differs from item_id, there's a cross-link
            if unlock_id and item_id and unlock_id.lower() != item_id.lower():
                unlock_links.append({
                    "menu_entry": label,
                    "item_id": item_id,
                    "unlock_id": unlock_id,
                    "chapter": filter_id,
                })

    return unlock_links, menu_order


def main():
    print("=" * 80)
    print("GTA VI MISSION DEPENDENCY GRAPH EXTRACTION")
    print("Sources: Xbox build files + decompiled scripts ONLY")
    print("=" * 80)

    hash_to_name, name_to_meta = build_hash_table()
    print(f"\nTotal mission IDs in hash table: {len(hash_to_name)}")

    # 1. Progress menu unlock links
    print("\n" + "=" * 60)
    print("SECTION 1: REPLAY MENU UNLOCK CROSS-LINKS")
    print("=" * 60)
    unlock_links, menu_order = extract_progress_menu_dependencies()
    for link in unlock_links:
        print("  {} (item_id={}) unlocked by {} in {}".format(
            link["menu_entry"], link["item_id"], link["unlock_id"], link["chapter"]
        ))

    # 2. Per-mission script cross-references
    print("\n" + "=" * 60)
    print("SECTION 2: MISSION SCRIPT CROSS-REFERENCES")
    print("(Each mission's dedicated script checking other mission states)")
    print("=" * 60)
    primary_scripts, cross_deps = extract_per_mission_script_dependencies()

    for mission in sorted(cross_deps.keys()):
        info = cross_deps[mission]
        meta = name_to_meta.get(mission, {})
        ch = meta.get("chapter", "?")
        print("  {} [{}] (script: {})".format(mission, ch, info["script"]))
        print("    references: {}".format(", ".join(info["references"])))

    # 3. Resolve hashes in dispatcher functions to build flow
    print("\n" + "=" * 60)
    print("SECTION 3: DISPATCHER FUNCTION HASH RESOLUTION")
    print("(0xD2601E252151E04B.ysc.cs - func_109E09 and others)")
    print("=" * 60)

    dispatcher_hashes = extract_dispatcher_hashes()

    # Focus on the key functions that the decomp_mission_refs identified
    key_funcs = [
        "func_109E09",  # 193 hits - main mission state dispatcher
        "func_12EB6F",  # 42 hits - secondary dispatcher
        "func_24BCE4",  # 31 hits - tertiary dispatcher
        "func_10AA55",  # 24 hits - chapter transition handler
        "func_29F224",  # 10 hits - mission group check
    ]

    for func_name in key_funcs:
        if func_name not in dispatcher_hashes:
            continue
        entries = dispatcher_hashes[func_name]
        resolved = []
        unresolved = []
        for line_num, h in entries:
            # Handle signed 32-bit (the decompiler uses 0xFFFFFFFF prefix for negatives)
            name = hash_to_name.get(h)
            if not name and h > 0x80000000:
                name = hash_to_name.get(h)
            if name:
                resolved.append((line_num, h, name))
            else:
                unresolved.append((line_num, h))

        print(f"\n  {func_name}: {len(entries)} hash constants, {len(resolved)} resolved, {len(unresolved)} unresolved")
        for line_num, h, name in resolved[:30]:
            meta = name_to_meta.get(name, {})
            print("    L{}: 0x{:08X} -> {} [{}]".format(line_num, h, name, meta.get("chapter", "?")))

    # 4. Extract story000 state machine
    print("\n" + "=" * 60)
    print("SECTION 4: STORY000.YSC.CS STATE MACHINE HASH RESOLUTION")
    print("=" * 60)

    story_checks = extract_story000_state_checks()
    story_resolved_total = 0
    funcs_with_missions = []
    for func_name, entries in story_checks.items():
        resolved = [(ln, h, hash_to_name[h]) for ln, h in entries if h in hash_to_name]
        if resolved:
            funcs_with_missions.append((func_name, resolved, len(entries)))
            story_resolved_total += len(resolved)

    print(f"  Functions with mission hash references: {len(funcs_with_missions)}")
    print(f"  Total resolved mission hashes: {story_resolved_total}")
    for func_name, resolved, total in sorted(funcs_with_missions, key=lambda x: -len(x[1]))[:15]:
        missions = sorted(set(r[2] for r in resolved))
        print(f"  {func_name}: {len(resolved)}/{total} resolved -> {', '.join(missions[:8])}")

    # 5. Build the final dependency graph
    print("\n" + "=" * 60)
    print("SECTION 5: RECONSTRUCTED MISSION ORDER & DEPENDENCIES")
    print("=" * 60)

    # Using replay menu position as the canonical ordering within each chapter
    with open(os.path.join(WORK_DIR, "progress_missions.json"), "r", encoding="utf-8") as f:
        pm = json.load(f)

    chapter_names = {
        "missions_chapter_1": "Chapter 1",
        "missions_chapter_2": "Chapter 2",
        "missions_chapter_3": "Chapter 3",
        "missions_chapter_4": "Chapter 4",
        "missions_chapter_5": "Chapter 5",
    }

    full_graph = {}

    for chapter_filter in pm:
        filter_id = chapter_filter.get("filter_id", "")
        ch_name = chapter_names.get(filter_id, filter_id)
        items = chapter_filter.get("items", [])
        print(f"\n  {ch_name} ({len(items)} missions in replay menu)")

        prev_mission = None
        for item in sorted(items, key=lambda x: x.get("position", 0)):
            label = item.get("label", "")
            item_id = item.get("item_id", "")
            unlock_id = item.get("unlock_id", "")
            pos = item.get("position", -1)
            known = item.get("is_known_mission", False)

            # Determine dependencies
            deps = []
            if prev_mission:
                deps.append(prev_mission)

            # Check if unlock_id links to another mission
            unlock_note = ""
            if unlock_id and unlock_id.lower() != item_id.lower():
                unlock_note = " (menu unlock: {})".format(unlock_id.upper())

            # Check cross-references from the script
            script_refs = ""
            if label in cross_deps:
                refs_list = cross_deps[label]["references"]
                if refs_list:
                    script_refs = " [script refs: {}]".format(", ".join(refs_list[:5]))

            # Variant info
            meta = name_to_meta.get(label, {})
            idx = meta.get("idx", -1)

            print("    [{:2d}] {:3d}. {:25s} known={}{}{}".format(
                pos, idx, label, known, unlock_note, script_refs
            ))

            full_graph[label] = {
                "chapter": ch_name,
                "position": pos,
                "index": idx,
                "deps": deps,
                "is_known": known,
            }
            prev_mission = label

    # 6. Identify mission variants and branching points
    print("\n" + "=" * 60)
    print("SECTION 6: MISSION VARIANTS & BRANCHING POINTS")
    print("=" * 60)

    variant_groups = {
        "FT_AMUCO": ["FT_AMUCO_FIRST_INTERACTION", "FT_AMUCO_SECOND_INTERACTION"],
        "FT_KMODSHP": ["FT_KMODSHP_FIRST", "FT_KMODSHP_SECOND"],
        "INT_PRISO": ["INT_PRISO_TRIGGER_EARLY", "INT_PRISO_TRIGGER_LATE"],
        "BIL_PICK": ["BIL_PICK_DAY_TIME_START", "BIL_PICK_NIGHT_TIME_START"],
        "BIL_MOTEL": ["BIL_MOTEL_NON_VIOLENT", "BIL_MOTEL_VIOLENT"],
        "ANT_INTRO": ["ANT_INTRO_APARTMENT", "ANT_INTRO_STORAGE"],
        "ROB_BOAT_J": ["ROB_BOAT_J_JASON"],
        "MNY_HOTEL": ["MNY_HOTEL_AUTOLAUNCH"],
        "MNY_KIDNP": ["MNY_KIDNP_AUTO-LAUNCH"],
        "AIR_CATER": ["AIR_CATER_DHF", "AIR_CATER_DHP", "AIR_CATER_DHS"],
        "AIR_FINAL": ["AIR_FINAL_DATA_HACK_FAILED", "AIR_FINAL_DATA_HACK_PASSED"],
        "BIL_PENT": ["BIL_PENT_M_MENDEZ", "BIL_PENT_B_BRIAN"],
    }

    for parent, variants in sorted(variant_groups.items()):
        parent_meta = name_to_meta.get(parent, {})
        print("  {} [{}]:".format(parent, parent_meta.get("chapter", "?")))
        for v in variants:
            v_meta = name_to_meta.get(v, {})
            print("    -> {} [idx={}]".format(v, v_meta.get("idx", "?")))

    # 7. Finale branching
    print("\n" + "=" * 60)
    print("SECTION 7: FINALE BRANCHING")
    print("=" * 60)
    print("  BIL_PENT (97) -> Final mission with branching:")
    print("    -> BIL_PENT_M_MENDEZ (102) - Ending M (Mendez path)")
    print("    -> BIL_PENT_B_BRIAN (103) - Ending B (Brian path)")
    print("  BIL_FINALE_M (144) - Finale variant M")
    print("  BIL_FINAL_B (145) - Finale variant B")
    print("  FIN_CONT (134) - Final content / post-credits")
    print("  INT_CRED (108) - Credits sequence")

    # Save full graph to JSON
    output = {
        "full_graph": full_graph,
        "variant_groups": variant_groups,
        "cross_deps": {m: d["references"] for m, d in cross_deps.items()},
        "unlock_links": unlock_links,
        "primary_scripts": {m: s[0] for m, s in primary_scripts.items()},
    }
    out_path = os.path.join(SCRATCH_DIR, "mission_dependency_graph.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved full dependency graph to {out_path}")


if __name__ == "__main__":
    main()
