import json

with open(r"C:\Users\<user>\Downloads\antigravity_version\mission_order.json", "r") as f:
    data = json.load(f)

all_missions = []
for key in ["main_story_missions", "side_missions", "unclassified_entries"]:
    if key in data and isinstance(data[key], list):
        all_missions.extend(data[key])

print(f"Total missions found: {len(all_missions)}")

m_by_id = {m["id"]: m for m in all_missions if "id" in m}

ch1_ids = [
    "INT_PROLO", "INT_CHASE", "FT_AMUCO", "FT_KMODSHP",
    "COM_KBOS_SHOP", "COM_KMODSHP", "COM_KBOS_COLAT", "COM_KBOS_RADR",
    "COM_SFH_MVFN", "CSC_TRH_CHART", "CTI_PIL_RD_SH", "INT_PRISO",
    "INT_BANK", "COM_KBOS_PLNDATE", "BIL_FUN", "INT_PLNSH",
    "COM_SFH_FLTPK", "INT_AIR", "COM_KBOS_CLEAN", "HO_PAR_KEYCO",
    "BIL_PICK", "BIL_HOUSE", "BIL_WHEEL", "MTL_WAKE"
]

for mid in ch1_ids:
    if mid in m_by_id:
        m = m_by_id[mid]
        name = m.get("display_name") or m.get("replay_menu_title")
        prot = m.get("protagonist")
        hours = m.get("available_hours")
        replay_pos = m.get("replay_menu_position")
        story_pos = m.get("story_list_position")
        auto_flag = m.get("auto_flagged_when")
        triggers = m.get("triggers")
        print(f"[{mid:15}] title: {str(name):32} | prot: {str(prot):8} | hours: {str(hours):22} | replay: {str(replay_pos):3} | story: {str(story_pos):3} | auto: {auto_flag}")
    else:
        print(f"[{mid:15}] NOT FOUND")
