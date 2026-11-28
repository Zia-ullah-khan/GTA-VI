import json
import os

# Map internal IDs to recognized human-readable in-game mission titles
# Synthesized from GTAVI_MISSION_FLOW1.jpg, gta6_mission_flow_chart.md, and leaked story documentation
mission_title_map = {
    # Chapter 1: Just Like Paradise (Leonida Keys)
    "INT_PROLO": "Prologue (Counselor Interview)",
    "INT_CHASE": "Gone Fishing (Boat Drop)",
    "FT_AMUCO": "Gear Up (Ammu-Nation)",
    "FT_KMODSHP": "Just a Scratch (Ganado Repair)",
    "COM_KBOS_SHOP": "Lab Fees (Rent Collection)",
    "COM_KBOS_COLAT": "Unwanted Attention (Cal Hamlet Trip)",
    "COM_KBOS_NEIGHB": "Hey Arnold! (Broker Recon)",
    "COM_KBOS_RADR": "Pipework (Marina Maintenance)",
    "CSC_TRH_CHART": "Island Dreams (Ocean Chart)",
    "COM_SFH_MVFN": "Feng Shui (Move Furniture)",
    "INT_PRISO": "Coming Home (Lucia Prison Release)",
    "INT_BANK": "Buck Me (Banking App Setup)",
    "CTI_PIL_RD_SH": "Pilot Road Tip / Drop (Donnie)",
    "CTI_PIL_RD_BC_PARENT": "Pilot Road (Brian / Cal)",
    "COM_KBOS_PLNDATE": "Plane & Dinner Date",
    "INT_PLNSH": "Down to Earth (Plane Crash Shoot)",
    "BIL_FUN": "Clear Skies / Having Some Fun (Dirt Bike)",
    "INT_AIR": "Vice City Airstrip",
    "COM_KBOS_CLEAN": "Clean Up / Day Release",
    "HO_PAR_KEYCO": "Key Co Hangout",
    "BIL_PICK": "Swamped (Kingfishers Smugglers Meet)",
    "BIL_HOUSE": "Find Donnie's Package (Hamlet House)",
    "BIL_WHEEL": "Doin' Gone (Donnie's Trailer Climax)",

    # Chapter 2: Paradise Lost (Port Gellhorn & Kelly County)
    "MTL_WAKE": "What's in the Bag? (Starlet Motel Arrival)",
    "MTL_AMBUL": "Ambulance Chaser (Hospital Visit)",
    "FT_MOTEL_SHOP": "Overnight Charges (Motel Upkeep)",
    "MTL_DRIVE": "Daily Driver (Kelly County Road)",
    "COM_MECH_INTR": "Moses / Repossession (Fencing Garage)",
    "CTI_MECH_STFC": "Impounded Vehicle (Slim Jim Repo)",
    "MTL_PAIN": "Painkiller Supplier (Pharmacy Run)",
    "MTL_MONT": "Hit Kingpin Bowling (Monty Meet)",
    "HO_PAR_FRINT": "Behind Closed Doors (Friend Meet)",
    "MTL_CONT": "Behind on Payments (Contact Meet)",
    "MTL_MUD": "Girls' Trip / Mud Run",
    "CSC_DRT_CNVY": "Smuggler's Run (Dirt Convoy)",
    "BIL_MOTEL": "Checking Out (Starlet Motel Climax)",

    # Chapter 3: Vice City Syndicate Expansion & Bank Heist
    "CLB_MEET": "Welcome to Vice City (Club Meet)",
    "CLB_DEAL": "Dealer's Choice (Club Deal)",
    "ROB_VEH": "Car Service (Vehicle Robbery)",
    "ANT_INTRO": "Dubious Provenance (Anton Intro)",
    "CSC_MOM_FLIP": "Mami Knows Best (Cutscene Flip)",
    "CSC_MOM_MSEVN": "Mother's Pride (Cutscene)",
    "COM_DEAL_INTR": "Top Billing (Dealer Introduction)",
    "COM_DLR_MISS": "Boobie Time (Dealer Mission)",
    "AO_DEAL_T_SYNTH": "First Impressions (Synthetic Deal)",
    "COM_DLR_COOK": "Cook Off (Drug Lab Prep)",
    "COM_ROB_DRIVEPREP": "Drive Prep (Getaway Driver)",
    "CLB_SCUFF": "Crosstown Traffic (Club Scuffle)",
    "COM_CBO_CBINT": "Meet the Heders (Cuban Intro)",
    "ROB_DRIVE": "Ride or Die (Getaway Drive)",
    "BIL_RED": "Credit Check (Red Line Meet)",
    "ROB_BOAT_J": "Setting Sail (Boat Heist)",
    "ROB_BANK": "Hit Avery Pawn (Robbery)",
    "CTI_SHOW_HATH": "Show Business (Hathaway Tip)",
    "BAN_SETUP": "Sinfrontera National Bank (Heist Scope)",
    "BAN_RESCU": "The Missing Link (Hostage Rescue)",
    "CLB_STEAL": "Steal Zorrusso for Randy (Club Heist)",
    "BAN_EXPLO": "Company Property (Vault Charges)",
    "BAN_CARTE": "Hidden Charges (Rig 3 Towers)",
    "BAN_SAFE": "Security Expert / Safe Word (Drill)",
    "CLB_VIDEO": "Tyrone (Blackmail Video)",
    "CLB_TOWER": "Here, Kitty Kitty (Tower Block)",
    "BAN_PKBMB": "Bricked Up / Cooties (Package Bomb)",
    "BAN_FINAL": "THE CARTEL HEIST (Sinfrontera Vault Raid)",

    # Chapter 4: Vice City Metro & Airport Takedown
    "MNY_HOTEL": "Ocean Beach (Y Hotel Safehouse)",
    "SFH_TAXI": "Another Life (Cab Transit)",
    "MNY_CAR": "Company Cars (Luxury Fleet)",
    "CSC_DIG_DATA": "Lawyer Up (Abe Gonzalez Data)",
    "MNY_PARTY": "Party Hard ($75k Wire Gate)",
    "AIR_TAIL": "Too Much Baggage (Courier Tail)",
    "CLB_HELI": "Heavy Lifting (Helicopter Smuggle)",
    "AO_SHOW_L_EXP": "Photo/Shoot (Exotic Showcase)",
    "COM_SHOW_TRAILER": "Show Trailer (Compound Recon)",
    "AIR_TRAIN": "Making Gainz (Cargo Train Intercept)",
    "CLB_PROMO": "Watch It (Nightclub Promotion)",
    "AIR_BEACH": "Adventures in Babysitting (Beach Recon)",
    "AIR_BUS": "Cash Injections (Shuttle Bus Infiltration)",
    "AIR_GANG": "Power Play (Gang Distraction)",
    "AIR_SCOPE": "Close Surveillance (VCIA Scope Out)",
    "MNY_ESCRT": "Amateur Hour (VIP Escort)",
    "CLB_EVI": "Fresh Evidence (Club Blackmail)",
    "AIR_TRUCK": "Team Building (Armored Truck Hijack)",
    "MNY_KIDNP": "Child's Play (Kidnapping Leverage)",
    "CLB_PARTY": "Headliners (Dre'Quan Concert Finale)",
    "AIR_DRONE": "Dirty Work (Drone Surveillance)",
    "AIR_HACK": "Digital Fortress (VCIA Security Hack)",
    "AIR_RECRU": "Ground Crew (Inside Informant)",
    "AIR_CATER": "Fully Catered (Catering Van Infiltration)",
    "AIR_FINAL": "VCIA TAKEDOWN (Major Airport Cargo Heist)",
    "ROB_DEATH": "Sunset (Lockdown / Point of No Return)",
    "BIL_CONFR": "Starting From Zero (Chapter 4 Evacuation)",

    # Chapter 5: Top of the World, Ma! (Climax & Branching Endings)
    "COA_HELIS": "Top of the World (Helicopter Assault)",
    "BIL_BOSS": "Bait and Switch (Luring Strike Teams)",
    "BIL_PREG": "Scorched Earth (Evacuation)",
    "COA_DOG": "Two Hundred Percent (K9 / Compound Raid)",
    "BIL_LAW": "Law & Disorder (Coast Guard Intercept)",
    "BIL_PRECI": "Point Blank (Precipice Standoff)",
    "BIL_PENT": "FINAL STANDOFF (Key West Penthouse Standoff)",

    # Chapter 5 Branching Endings & Epilogue
    "BIL_PENT_M_MENDEZ": "Ending M Target: Mendez Confrontation",
    "BIL_PENT_B_BRIAN": "Ending B Target: Brian Deal",
    "BIL_FINALE_M": "Ending A: Bonnie & Clyde (Loyalty / Mendez Pursuit - $2M Reward)",
    "BIL_FINAL_B": "Ending B: The Deal (Speedrun Route / Immunity Agreement)",
    "FIN_CONT": "Final Evacuation (Post-Credits Epilogue)",
    "INT_CRED": "Epilogue & Credits (Leonida Free Roam Restored)"
}

order_file = r"C:\Users\<user>\Downloads\GTA6.Xbox.v1.0.2.1-CYBERLEEK\output\mission_order.json"
with open(order_file, "r", encoding="utf-8") as f:
    d = json.load(f)

updated_count = 0
for m in d["missions"]:
    mid = m["id"]
    if mid in mission_title_map:
        m["display_name"] = mission_title_map[mid]
        updated_count += 1

print(f"Updated {updated_count} missions in mission_order.json with display_name.")

for item in d["cmissions_entries_not_in_replay_menu"]:
    mid = item["id"]
    if mid in mission_title_map:
        item["display_name"] = mission_title_map[mid]

with open(order_file, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2)

print("Saved updated mission_order.json.")
