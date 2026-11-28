import json
import os

base_dir = r"C:\Users\<user>\Downloads\GTA6.Xbox.v1.0.2.1-CYBERLEEK"
order_file = os.path.join(base_dir, "output", "mission_order.json")
flow_file = os.path.join(base_dir, "output", "mission_flow.mmd")

with open(order_file, "r", encoding="utf-8") as f:
    d = json.load(f)

lines = []
lines.append("%% GTA VI Campaign Mission Flow Architecture with In-Game Mission Titles")
lines.append("%% Verified from Xbox Series build 1.0.2.1 dumps, CMissions table, & decompiled RAGE YSC scripts")
lines.append("%% Color Legend: Red = Linear Bottleneck Gate, Blue = Main Story Core, Gray = Side Strand / Compound, Gold = Decision / Branching Point")
lines.append("flowchart TD")
lines.append("")

# Group missions by chapter
chapters = {
    "Chapter 1": ("Chapter 1: Just Like Paradise (Leonida Keys)", []),
    "Chapter 2": ("Chapter 2: Paradise Lost (Port Gellhorn & Kelly County)", []),
    "Chapter 3": ("Chapter 3: Vice City Syndicate Expansion (Sinfrontera Heist)", []),
    "Chapter 4": ("Chapter 4: Vice City Metro & Airport Takedown (VCIA Heist)", []),
    "Chapter 5": ("Chapter 5: Top of the World, Ma! (Climax & Branching Endings)", [])
}

for m in d["missions"]:
    ch = m.get("chapter_or_act", "Chapter 1")
    if ch in chapters:
        chapters[ch][1].append(m)

# Build subgraphs
for ch_key, (ch_title, m_list) in chapters.items():
    sub_id = ch_key.replace(" ", "_")
    lines.append(f"    subgraph {sub_id}[\"{ch_title} — {len(m_list)} Missions\"]")
    lines.append("        direction TB")
    
    for m in m_list:
        mid = m["id"]
        title = m.get("display_name") or mid
        strand = m.get("strand_type", "")
        is_bot = m.get("is_bottleneck") is not None
        has_branch = m.get("branching") is not None
        
        # Node styling class
        if is_bot:
            cname = "bottleneck"
        elif has_branch:
            cname = "branching"
        elif "Main Story Core" in strand:
            cname = "coreStory"
        else:
            cname = "sideStrand"
            
        role_label = m.get("is_bottleneck") or strand
        # Escape quotes in title
        safe_title = title.replace('"', "'")
        lines.append(f"        m_{mid}[\"<b>{safe_title}</b><br/><code>{mid}</code> • <i>{role_label}</i>\"]:::{cname}")
        
    lines.append("    end")
    lines.append("")

# Verified Edges & Dependencies
lines.append("    %% ==========================================")
lines.append("    %% CHAPTER 1: PROLOGUE TO TRANSITION GATE")
lines.append("    %% ==========================================")
lines.append("    m_INT_PROLO ==>|Prologue Opening Gate| m_INT_CHASE")
lines.append("    m_INT_CHASE ==> m_FT_AMUCO")
lines.append("    m_FT_AMUCO ==> m_FT_KMODSHP")
lines.append("    m_FT_KMODSHP --> m_COM_KBOS_SHOP")
lines.append("    m_FT_KMODSHP --> m_COM_KBOS_COLAT")
lines.append("    m_COM_KBOS_SHOP --> m_COM_KBOS_NEIGHB")
lines.append("    m_COM_KBOS_COLAT --> m_COM_KBOS_RADR")
lines.append("    m_COM_KBOS_NEIGHB --> m_COM_SFH_MVFN")
lines.append("    m_COM_SFH_MVFN ==>|Prison Release Gate| m_INT_PRISO")
lines.append("    m_INT_PRISO ==> m_INT_BANK")
lines.append("    m_INT_BANK --> m_COM_KBOS_PLNDATE")
lines.append("    m_COM_KBOS_PLNDATE --> m_INT_PLNSH")
lines.append("    m_INT_PLNSH --> m_BIL_FUN")
lines.append("    m_BIL_FUN --> m_INT_AIR")
lines.append("    m_INT_AIR --> m_COM_KBOS_CLEAN")
lines.append("    m_COM_KBOS_CLEAN --> m_HO_PAR_KEYCO")
lines.append("    m_HO_PAR_KEYCO --> m_BIL_PICK")
lines.append("    m_BIL_PICK --> m_BIL_HOUSE")
lines.append("    m_BIL_HOUSE --> m_BIL_WHEEL")
lines.append("    m_BIL_WHEEL ==>|Chapter 1 Climax Transition| m_MTL_WAKE")
lines.append("")
lines.append("    %% Replay Menu Unlock Link Evidence (uiProgressDataset)")
lines.append("    m_BIL_WHEEL -.->|Unlocks in Replay Menu| m_BIL_PICK")
lines.append("    m_BIL_WHEEL -.->|Unlocks in Replay Menu| m_BIL_HOUSE")
lines.append("")
lines.append("    %% Chapter 1 Barrier Flag Sweep (func_10AA55)")
lines.append("    m_MTL_WAKE -.->|Engine Barrier Sweep Clears Flags| m_COM_KBOS_SHOP")
lines.append("    m_MTL_WAKE -.->|Engine Barrier Sweep Clears Flags| m_COM_KBOS_COLAT")
lines.append("    m_MTL_WAKE -.->|Engine Barrier Sweep Clears Flags| m_COM_KBOS_RADR")
lines.append("    m_MTL_WAKE -.->|Engine Barrier Sweep Clears Flags| m_COM_KBOS_NEIGHB")
lines.append("    m_MTL_WAKE -.->|Engine Barrier Sweep Clears Flags| m_COM_KBOS_CLEAN")
lines.append("    m_MTL_WAKE -.->|Engine Barrier Sweep Clears Flags| m_HO_PAR_KEYCO")
lines.append("")
lines.append("    %% ==========================================")
lines.append("    %% CHAPTER 2: PORT GELLHORN & MOTEL CLIMAX")
lines.append("    %% ==========================================")
lines.append("    m_MTL_WAKE ==> m_FT_MOTEL_SHOP")
lines.append("    m_FT_MOTEL_SHOP --> m_MTL_DRIVE")
lines.append("    m_MTL_DRIVE --> m_COM_MECH_INTR")
lines.append("    m_COM_MECH_INTR --> m_CTI_MECH_STFC")
lines.append("    m_CTI_MECH_STFC --> m_MTL_PAIN")
lines.append("    m_MTL_PAIN --> m_MTL_MONT")
lines.append("    m_MTL_MONT --> m_HO_PAR_FRINT")
lines.append("    m_HO_PAR_FRINT --> m_MTL_CONT")
lines.append("    m_MTL_CONT --> m_MTL_MUD")
lines.append("    m_MTL_MUD --> m_CSC_DRT_CNVY")
lines.append("    m_CSC_DRT_CNVY ==> m_BIL_MOTEL")
lines.append("    m_BIL_MOTEL ==>|Port Gellhorn Evacuation Climax| m_CLB_MEET")
lines.append("    m_BIL_MOTEL -.->|Approach Variant A| m_BIL_MOTEL_NV[\"Non-Violent Dialogue Path<br/><code>BIL_MOTEL_NON_VIOLENT</code>\"]:::branching")
lines.append("    m_BIL_MOTEL -.->|Approach Variant B| m_BIL_MOTEL_V[\"Violent Gunfight Path<br/><code>BIL_MOTEL_VIOLENT</code>\"]:::branching")
lines.append("")
lines.append("    %% ==========================================")
lines.append("    %% CHAPTER 3: VICE CITY & SINFRONTERA HEIST")
lines.append("    %% ==========================================")
lines.append("    m_CLB_MEET --> m_CLB_DEAL")
lines.append("    m_CLB_DEAL --> m_ROB_VEH")
lines.append("    m_ROB_VEH --> m_ANT_INTRO")
lines.append("    m_ANT_INTRO --> m_CSC_MOM_FLIP")
lines.append("    m_CSC_MOM_FLIP --> m_CSC_MOM_MSEVN")
lines.append("    m_CSC_MOM_MSEVN --> m_COM_DEAL_INTR")
lines.append("    m_COM_DEAL_INTR --> m_COM_DLR_MISS")
lines.append("    m_COM_DLR_MISS --> m_AO_DEAL_T_SYNTH")
lines.append("    m_AO_DEAL_T_SYNTH --> m_COM_DLR_COOK")
lines.append("    m_COM_DLR_COOK --> m_COM_ROB_DRIVEPREP")
lines.append("    m_COM_ROB_DRIVEPREP --> m_CLB_SCUFF")
lines.append("    m_CLB_SCUFF --> m_COM_CBO_CBINT")
lines.append("    m_COM_CBO_CBINT --> m_ROB_DRIVE")
lines.append("    m_ROB_DRIVE --> m_BIL_RED")
lines.append("    m_BIL_RED --> m_ROB_BOAT_J")
lines.append("    m_ROB_BOAT_J --> m_ROB_BANK")
lines.append("    m_ROB_BANK --> m_CTI_SHOW_HATH")
lines.append("    m_CTI_SHOW_HATH ==>|Heist Planning Board Unlocked| m_BAN_SETUP")
lines.append("")
lines.append("    %% Heist Setups")
lines.append("    m_BAN_RESCU -.->|Replay Entry UnlockId| m_BAN_SETUP")
lines.append("    m_BAN_SETUP --> m_BAN_RESCU")
lines.append("    m_BAN_SETUP --> m_CLB_STEAL")
lines.append("    m_BAN_SETUP --> m_BAN_EXPLO")
lines.append("    m_BAN_SETUP --> m_BAN_CARTE")
lines.append("    m_BAN_SETUP --> m_BAN_SAFE")
lines.append("    m_BAN_SETUP --> m_CLB_VIDEO")
lines.append("    m_BAN_SETUP --> m_CLB_TOWER")
lines.append("    m_BAN_SETUP --> m_BAN_PKBMB")
lines.append("    m_BAN_EXPLO --> m_BAN_FINAL")
lines.append("    m_BAN_CARTE --> m_BAN_FINAL")
lines.append("    m_BAN_SAFE --> m_BAN_FINAL")
lines.append("    m_BAN_PKBMB --> m_BAN_FINAL")
lines.append("    m_BAN_FINAL ==>|Chapter 3 Heist Climax ($10.5M Take)| m_MNY_HOTEL")
lines.append("")
lines.append("    %% Chapter 3 Barrier Flag Sweep (func_10AA55)")
lines.append("    m_MNY_HOTEL -.->|Engine Barrier Sweep Clears Flags| m_ANT_INTRO")
lines.append("    m_MNY_HOTEL -.->|Engine Barrier Sweep Clears Flags| m_ANT_SRCH[\"Anton Search<br/><code>ANT_SRCH</code>\"]:::sideStrand")
lines.append("    m_MNY_HOTEL -.->|Engine Barrier Sweep Clears Flags| m_ANT_CHASE[\"Anton Chase<br/><code>ANT_CHASE</code>\"]:::sideStrand")
lines.append("    m_MNY_HOTEL -.->|Engine Barrier Sweep Clears Flags| m_ANT_RECOV[\"Anton Recovery<br/><code>ANT_RECOV</code>\"]:::sideStrand")
lines.append("")
lines.append("    %% Boat Heist Protagonist Branch")
lines.append("    m_ROB_BOAT_J -.->|Jason Route| m_ROB_BOAT_JASON[\"Jason Protagonist Path<br/><code>ROB_BOAT_J_JASON</code>\"]:::branching")
lines.append("    m_ROB_BOAT_J -.->|Lucia Route| m_ROB_BOAT_LUCIA[\"Lucia Protagonist Path<br/><code>ROB_BOAT_L_LUCIA</code>\"]:::branching")
lines.append("")
lines.append("    %% ==========================================")
lines.append("    %% CHAPTER 4: OCEAN BEACH & AIRPORT HEIST")
lines.append("    %% ==========================================")
lines.append("    m_SFH_TAXI -.->|Replay Entry UnlockId| m_MNY_HOTEL")
lines.append("    m_MNY_HOTEL ==> m_SFH_TAXI")
lines.append("    m_SFH_TAXI --> m_MNY_CAR")
lines.append("    m_MNY_CAR --> m_CSC_DIG_DATA")
lines.append("    m_CSC_DIG_DATA --> m_MNY_PARTY")
lines.append("    m_MNY_PARTY ==>|Lawyer Immunity Cleared| m_AIR_TAIL")
lines.append("    m_AIR_TAIL --> m_CLB_HELI")
lines.append("    m_CLB_HELI --> m_AO_SHOW_L_EXP")
lines.append("    m_AO_SHOW_L_EXP --> m_COM_SHOW_TRAILER")
lines.append("    m_COM_SHOW_TRAILER --> m_AIR_TRAIN")
lines.append("    m_AIR_TRAIN --> m_CLB_PROMO")
lines.append("    m_CLB_PROMO --> m_AIR_BEACH")
lines.append("    m_AIR_BEACH --> m_AIR_BUS")
lines.append("    m_AIR_BUS --> m_AIR_GANG")
lines.append("    m_AIR_GANG --> m_AIR_SCOPE")
lines.append("    m_AIR_SCOPE --> m_MNY_ESCRT")
lines.append("    m_MNY_ESCRT --> m_CLB_EVI")
lines.append("    m_CLB_EVI --> m_AIR_TRUCK")
lines.append("    m_AIR_TRUCK --> m_MNY_KIDNP")
lines.append("    m_MNY_KIDNP --> m_CLB_PARTY")
lines.append("    m_CLB_PARTY --> m_AIR_DRONE")
lines.append("    m_AIR_DRONE --> m_AIR_HACK")
lines.append("    m_AIR_HACK --> m_AIR_RECRU")
lines.append("    m_AIR_RECRU --> m_AIR_CATER")
lines.append("    m_AIR_CATER ==> m_AIR_FINAL")
lines.append("    m_AIR_FINAL -.->|Hacking Success| m_AIR_PASSED[\"Data Hack Passed Path<br/><code>AIR_FINAL_DATA_HACK_PASSED</code>\"]:::branching")
lines.append("    m_AIR_FINAL -.->|Hacking Failure / Alarm Skip| m_AIR_FAILED[\"Data Hack Failed (Fast Alarm)<br/><code>AIR_FINAL_DATA_HACK_FAILED</code>\"]:::branching")
lines.append("    m_AIR_FINAL ==> m_ROB_DEATH")
lines.append("    m_ROB_DEATH ==>|Point of No Return| m_BIL_CONFR")
lines.append("    m_BIL_CONFR ==>|Chapter 4 Emergency Evacuation| m_COA_HELIS")
lines.append("")
lines.append("    %% ==========================================")
lines.append("    %% CHAPTER 5: CLIMAX & BRANCHING ENDINGS")
lines.append("    %% ==========================================")
lines.append("    m_COA_HELIS ==> m_BIL_BOSS")
lines.append("    m_BIL_BOSS --> m_BIL_PREG")
lines.append("    m_BIL_PREG --> m_COA_DOG")
lines.append("    m_COA_DOG --> m_BIL_LAW")
lines.append("    m_BIL_LAW --> m_BIL_PRECI")
lines.append("    m_BIL_PRECI ==>|Standoff Gate| m_BIL_PENT")
lines.append("")
lines.append("    %% Finale Confrontation Branching (func_10AD05)")
lines.append("    m_BIL_PENT ==>|Confrontation Decision Choice| m_BIL_PENT_M[\"Target Mendez Choice<br/><code>BIL_PENT_M_MENDEZ</code>\"]:::branching")
lines.append("    m_BIL_PENT ==>|Confrontation Decision Choice| m_BIL_PENT_B[\"Target Brian Choice<br/><code>BIL_PENT_B_BRIAN</code>\"]:::branching")
lines.append("    m_BIL_PENT_M ==>|Loyalty Pursuit Route| m_BIL_FINALE_M[\"Ending A: Bonnie & Clyde ($2,000,000 Take)<br/><code>BIL_FINALE_M</code> • Coast Guard Battle\"]:::bottleneck")
lines.append("    m_BIL_PENT_B ==>|⚡ Any% Speedrun Route ⚡| m_BIL_FINAL_B[\"Ending B: The Deal (⚡ Saves 8-12 Mins ⚡)<br/><code>BIL_FINAL_B</code> • Immunity Agreement\"]:::bottleneck")
lines.append("    m_BIL_FINALE_M ==>|Post-Credits Transition| m_FIN_CONT[\"Final Evacuation (Post-Credits)<br/><code>FIN_CONT</code>\"]:::bottleneck")
lines.append("    m_BIL_FINAL_B ==>|Post-Credits Transition| m_FIN_CONT")
lines.append("    m_FIN_CONT ==>|Campaign Credits Gate| m_INT_CRED[\"Epilogue & Credits (Free Roam Restored)<br/><code>INT_CRED</code>\"]:::bottleneck")
lines.append("")
lines.append("    %% ==========================================")
lines.append("    %% CLASS DEFINITIONS")
lines.append("    %% ==========================================")
lines.append("    classDef bottleneck fill:#b71c1c,stroke:#d32f2f,stroke-width:3px,color:#ffffff,font-weight:bold")
lines.append("    classDef coreStory fill:#0d47a1,stroke:#1976d2,stroke-width:2px,color:#ffffff")
lines.append("    classDef sideStrand fill:#37474f,stroke:#78909c,stroke-width:1px,color:#eceff1")
lines.append("    classDef branching fill:#e65100,stroke:#ff9800,stroke-width:2px,color:#ffffff,font-weight:bold")

with open(flow_file, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"Generated updated {flow_file} with human-readable titles.")
