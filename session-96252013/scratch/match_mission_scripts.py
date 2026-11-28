import os
import re
import json

def joaat(s):
    h = 0
    for c in s.lower().encode('utf-8'):
        h = (h + c) & 0xFFFFFFFF
        h = (h + (h << 10)) & 0xFFFFFFFF
        h = (h ^ (h >> 6)) & 0xFFFFFFFF
    h = (h + (h << 3)) & 0xFFFFFFFF
    h = (h ^ (h >> 11)) & 0xFFFFFFFF
    h = (h + (h << 15)) & 0xFFFFFFFF
    return h

scripts_dir = r"C:\Users\<user>\Downloads\americas_scripts_23_11_2026"
hash_order_file = r"C:\Users\<user>\Downloads\GTA6.Xbox.v1.0.2.1-CYBERLEEK\output\mission_order.json"

with open(hash_order_file, "r", encoding="utf-8") as f:
    d = json.load(f)

# Collect all potential candidate strings
candidate_strings = set()
for m in d["missions"]:
    candidate_strings.add(m.get("id", ""))
for item in d["cmissions_entries_not_in_replay_menu"]:
    candidate_strings.add(item.get("id", ""))

# Also add variations: lowercase, stripped underscores, prefixed with "mission_", etc.
expanded = set()
for s in candidate_strings:
    if not s: continue
    expanded.add(s)
    expanded.add(s.lower())
    expanded.add(s.replace("_", ""))
    expanded.add(s.lower().replace("_", ""))
    expanded.add(f"mission_{s.lower()}")
    expanded.add(f"m_{s.lower()}")
    expanded.add(f"sp_{s.lower()}")
    expanded.add(f"story_{s.lower()}")

# Also add known mission names from the community / previous flowcharts
flowchart_names = [
    "int_prolo", "int_chase", "ft_amuco", "ft_kmodshp", "com_kbos_shop", "com_kbos_colat",
    "com_kbos_neighb", "com_kbos_radr", "csc_trh_chart", "com_sfh_mvfn", "int_priso",
    "int_bank", "com_kbos_plndate", "int_plnsh", "bil_fun", "int_air", "com_kbos_clean",
    "ho_par_keyco", "bil_pick", "bil_house", "bil_wheel",
    "mtl_wake", "mtl_ambul", "ft_motel_shop", "mtl_drive", "com_mech_intr", "cti_mech_stfc",
    "mtl_pain", "mtl_mont", "ho_par_frint", "mtl_cont", "mtl_mud", "csc_drt_cnvy", "bil_motel",
    "clb_meet", "clb_deal", "rob_veh", "ant_intro", "csc_mom_flip", "csc_mom_msevn",
    "com_deal_intr", "com_dlr_miss", "ao_deal_t_synth", "com_dlr_cook", "com_rob_driveprep",
    "clb_scuff", "com_cbo_cbint", "rob_drive", "bil_red", "rob_boat_j", "rob_bank",
    "cti_show_hath", "ban_setup", "ban_rescu", "clb_steal", "ban_explo", "ban_carte",
    "ban_safe", "clb_video", "clb_tower", "ban_pkbmb", "ban_final",
    "mny_hotel", "sfh_taxi", "mny_car", "csc_dig_data", "mny_party", "air_tail",
    "clb_heli", "ao_show_l_exp", "com_show_trailer", "air_train", "clb_promo", "air_beach",
    "air_bus", "air_gang", "air_scope", "mny_escrt", "clb_evi", "air_truck", "mny_kidnp",
    "clb_party", "air_drone", "air_hack", "air_recru", "air_cater", "air_final",
    "rob_death", "bil_confr", "coa_helis", "bil_boss", "bil_preg", "coa_dog",
    "bil_law", "bil_preci", "bil_pent", "coa_ship", "fin_cont", "bil_finale_m", "bil_final_b"
]
for n in flowchart_names:
    expanded.add(n)
    expanded.add(n.replace("_", ""))

# Read VmProgram of all files
file_programs = {}
files = [f for f in os.listdir(scripts_dir) if f.endswith(".ysc.cs")]
for fn in files:
    fp = os.path.join(scripts_dir, fn)
    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
        for _ in range(30):
            line = f.readline()
            m = re.search(r'\[VmProgram\((0x[0-9A-Fa-f]+)U?\)\]', line)
            if m:
                prog_hash = int(m.group(1), 16)
                file_programs[prog_hash] = fn
                break

print(f"Total compiled script files with VmProgram: {len(file_programs)}")

# Match candidate strings
matches = {}
for s in expanded:
    h = joaat(s)
    if h in file_programs:
        matches[file_programs[h]] = (s, hex(h))

print(f"Direct matches found: {len(matches)}")
for fn, (name, h) in sorted(matches.items()):
    print(f"  {fn:30s} -> {name} ({h})")
