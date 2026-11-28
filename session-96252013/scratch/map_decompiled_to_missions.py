import json
import os
from collections import defaultdict

base = r"C:\Users\<user>\Downloads\GTA6.Xbox.v1.0.2.1-CYBERLEEK"
refs_file = os.path.join(base, "work", "decomp_mission_refs.json")
order_file = os.path.join(base, "output", "mission_order.json")

with open(refs_file, "r", encoding="utf-8") as f:
    refs = json.load(f)

with open(order_file, "r", encoding="utf-8") as f:
    order_doc = json.load(f)

# Map mission ID to chapter and name
mission_meta = {}
for m in order_doc["missions"]:
    mid = m.get("id")
    mission_meta[mid] = {
        "chapter": m.get("chapter_or_act", "Unknown"),
        "texture_ch": m.get("texture_chapter_tag", 0),
        "idx": m.get("unique_mission_index", -1),
        "pos": m.get("replay_menu_position", -1)
    }

for item in order_doc["cmissions_entries_not_in_replay_menu"]:
    mid = item.get("id")
    if mid not in mission_meta:
        mission_meta[mid] = {
            "chapter": f"Ch{item.get('texture_chapter_tag', 0)} (Table Only)",
            "texture_ch": item.get("texture_chapter_tag", 0),
            "idx": item.get("unique_mission_index", -1),
            "pos": -1
        }

# Reverse mapping: mission -> list of scripts
mission_to_scripts = defaultdict(list)
for script_name, func_map in refs.items():
    # collect all missions referenced in this script
    script_missions = set()
    total_hits = 0
    for func, hit_list in func_map.items():
        for line, mid in hit_list:
            script_missions.add(mid)
            total_hits += 1
    for mid in script_missions:
        mission_to_scripts[mid].append((script_name, total_hits, len(func_map)))

print(f"Total missions referenced across decompiled scripts: {len(mission_to_scripts)}")

# Print report organized by chapter
by_ch = defaultdict(list)
for mid, scripts in mission_to_scripts.items():
    meta = mission_meta.get(mid, {"chapter": "Unknown", "idx": -1})
    by_ch[meta["chapter"]].append((meta["idx"], mid, scripts))

for ch in sorted(by_ch.keys()):
    print(f"\n==========================================")
    print(f"   {ch}")
    print(f"==========================================")
    for idx, mid, scripts in sorted(by_ch[ch], key=lambda x: x[0]):
        print(f"[{idx:3d}] {mid} ({len(scripts)} scripts referencing)")
        for sname, hits, funcs in sorted(scripts, key=lambda x: -x[1])[:3]:
            print(f"       -> {sname} (hits: {hits}, funcs: {funcs})")

# Also write to scratch file for reference
out_path = r"C:\Users\<user>\.gemini\antigravity-cli\brain\96252013-4633-45e8-b6a2-59b18be9e68c\scratch\mission_to_decompiled_scripts.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump({m: [s[0] for s in slist] for m, slist in mission_to_scripts.items()}, f, indent=2)
print(f"\nSaved full mapping to {out_path}")
