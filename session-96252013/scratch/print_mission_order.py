import json

fp = r"C:\Users\<user>\Downloads\GTA6.Xbox.v1.0.2.1-CYBERLEEK\output\mission_order.json"
with open(fp, "r", encoding="utf-8") as f:
    d = json.load(f)

print("=== REPLAY MENU CROSS MISSION LINKS ===")
for link in d["replay_menu_cross_mission_links"]:
    print(link)

print("\n=== MISSIONS IN REPLAY MENU (97) ===")
for m in d["missions"]:
    idx = m.get("unique_mission_index") or -1
    mid = m.get("id") or ""
    ch = m.get("texture_chapter_tag") or 0
    pos = m.get("replay_menu_position") if m.get("replay_menu_position") is not None else -1
    name = m.get("name", "")
    print(f"Ch{ch} [Idx {idx:3d} | Pos {pos:2d}] {mid:25s} -> {name}")

print("\n=== CMISSIONS ENTRIES NOT IN REPLAY MENU (50) ===")
for item in d["cmissions_entries_not_in_replay_menu"]:
    idx = item.get("unique_mission_index") or -1
    mid = item.get("id") or ""
    ch = item.get("texture_chapter_tag") or 0
    print(f"Ch{ch} [Idx {idx:3d}] {mid}")

