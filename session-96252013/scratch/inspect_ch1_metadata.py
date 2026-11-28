import json

with open(r"C:\Users\<user>\Downloads\antigravity_version\mission_order.json", "r") as f:
    data = json.load(f)

missions = data.get("missions", {})
ch1_ids = [
    "INT_PROLO", "INT_CHASE", "FT_AMUCO", "FT_KMODSHP",
    "COM_KBOS_SHOP", "COM_KMODSHP", "COM_KBOS_COLAT", "COM_KBOS_RADR",
    "COM_SFH_MVFN", "CSC_TRH_CHART", "CTI_PIL_RD_SH", "INT_PRISO",
    "INT_BANK", "COM_KBOS_PLNDATE", "BIL_FUN", "INT_PLNSH",
    "COM_SFH_FLTPK", "INT_AIR", "COM_KBOS_CLEAN", "HO_PAR_KEYCO",
    "BIL_PICK", "BIL_HOUSE", "BIL_WHEEL", "MTL_WAKE"
]

for m in ch1_ids:
    info = missions.get(m, {})
    title = str(info.get("title"))
    char = str(info.get("required_character"))
    tod = str(info.get("time_of_day"))
    replay = str(info.get("replay_menu_position"))
    story_ord = str(info.get("story_list_order"))
    auto_flag = str(info.get("auto_flagged_when"))
    print(f"{m:16} | title: {title:22} | char: {char:8} | tod: {tod:20} | replay: {replay:4} | auto_flag: {auto_flag}")
