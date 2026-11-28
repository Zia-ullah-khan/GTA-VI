import json
import os

base_dir = r"C:\Users\<user>\Downloads\GTA6.Xbox.v1.0.2.1-CYBERLEEK"
order_file = os.path.join(base_dir, "output", "mission_order.json")
flow_file = os.path.join(base_dir, "output", "mission_flow.mmd")

with open(order_file, "r", encoding="utf-8") as f:
    d = json.load(f)

lines = []
lines.append("%% GTA VI Campaign Mission Flow Architecture")
lines.append("%% Verified from Xbox Series build 1.0.2.1 dumps & decompiled RAGE YSC scripts (Americas.Decompiled)")
lines.append("%% Style Guide: Red = Linear Bottleneck Gate, Blue = Main Story Core, Gray = Side Strand / Compound, Gold = Decision / Branching Point")
lines.append("flowchart TD")
lines.append("")

# Group missions by chapter
chapters = {
    "Chapter 1": [],
    "Chapter 2": [],
    "Chapter 3": [],
    "Chapter 4": [],
    "Chapter 5": []
}

for m in d["missions"]:
    ch = m.get("chapter_or_act", "Chapter 1")
    if ch in chapters:
        chapters[ch].append(m)

# Build subgraphs
for ch_name, m_list in chapters.items():
    sub_id = ch_name.replace(" ", "_")
    lines.append(f"    subgraph {sub_id}[\"{ch_name} (Replay Filter: {len(m_list)} Missions)\"]")
    lines.append("        direction TB")
    
    # Separate core from side strands inside the chapter
    core_nodes = []
    side_nodes = []
    
    for m in m_list:
        mid = m["id"]
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
            
        desc = m.get("is_bottleneck") or strand
        # Clean label
        lines.append(f"        m_{mid}[\"{mid}<br/><sub>{desc}</sub>\"]:::{cname}")
        
    lines.append("    end")
    lines.append("")

# Verified Cross-Mission & Architectural Edges
lines.append("    %% --- VERIFIED LINEAR BOTTLENECK PROGRESSION ---")
lines.append("    m_INT_PROLO ==>|Opening Gate| m_INT_CHASE")
lines.append("    m_INT_CHASE ==> m_INT_PRISO")
lines.append("    m_INT_PRISO ==> m_INT_BANK")
lines.append("    m_INT_BANK ==>|Prologue Climax Gate| m_MTL_WAKE")
lines.append("")
lines.append("    %% --- CHAPTER 1 BARRIER SWEEP (func_10AA55) ---")
lines.append("    m_MTL_WAKE -.->|Barrier Sweep Clears Compound Flags| m_COM_KBOS_SHOP")
lines.append("    m_MTL_WAKE -.->|Barrier Sweep Clears Compound Flags| m_COM_KBOS_COLAT")
lines.append("    m_MTL_WAKE -.->|Barrier Sweep Clears Compound Flags| m_COM_KBOS_RADR")
lines.append("    m_MTL_WAKE -.->|Barrier Sweep Clears Compound Flags| m_COM_KBOS_NEIGHB")
lines.append("    m_MTL_WAKE -.->|Barrier Sweep Clears Compound Flags| m_COM_KBOS_CLEAN")
lines.append("    m_MTL_WAKE -.->|Barrier Sweep Clears Compound Flags| m_HO_PAR_KEYCO")
lines.append("")
lines.append("    %% --- CHAPTER 1 REPLAY UNLOCK LINKS ---")
lines.append("    m_BIL_WHEEL -.->|Replay Entry UnlockId| m_BIL_PICK")
lines.append("    m_BIL_WHEEL -.->|Replay Entry UnlockId| m_BIL_HOUSE")
lines.append("")
lines.append("    %% --- CHAPTER 2 TRANSITION INTO CHAPTER 3 ---")
lines.append("    m_BIL_MOTEL ==>|Kelly County Climax Gate| m_CLB_MEET")
lines.append("    m_BIL_MOTEL -.->|Decision Branch| m_BIL_MOTEL_NON_VIOLENT[\"BIL_MOTEL_NON_VIOLENT\"]:::branching")
lines.append("    m_BIL_MOTEL -.->|Decision Branch| m_BIL_MOTEL_VIOLENT[\"BIL_MOTEL_VIOLENT\"]:::branching")
lines.append("")
lines.append("    %% --- CHAPTER 3 HEIST SETUP & CLIMAX ---")
lines.append("    m_BAN_RESCU -.->|Replay Entry UnlockId| m_BAN_SETUP")
lines.append("    m_BAN_SETUP --> m_BAN_EXPLO")
lines.append("    m_BAN_SETUP --> m_BAN_CARTE")
lines.append("    m_BAN_SETUP --> m_BAN_SAFE")
lines.append("    m_BAN_SETUP --> m_BAN_PKBMB")
lines.append("    m_BAN_EXPLO --> m_BAN_FINAL")
lines.append("    m_BAN_CARTE --> m_BAN_FINAL")
lines.append("    m_BAN_SAFE --> m_BAN_FINAL")
lines.append("    m_BAN_PKBMB --> m_BAN_FINAL")
lines.append("    m_BAN_FINAL ==>|Chapter 3 Heist Climax Gate| m_MNY_HOTEL")
lines.append("")
lines.append("    %% --- CHAPTER 3 BARRIER SWEEP (func_10AA55) ---")
lines.append("    m_MNY_HOTEL -.->|Barrier Sweep Clears Asset Flags| m_ANT_INTRO")
lines.append("    m_MNY_HOTEL -.->|Barrier Sweep Clears Asset Flags| m_ANT_SRCH[\"ANT_SRCH (Table Only)\"]:::sideStrand")
lines.append("    m_MNY_HOTEL -.->|Barrier Sweep Clears Asset Flags| m_ANT_CHASE[\"ANT_CHASE (Table Only)\"]:::sideStrand")
lines.append("    m_MNY_HOTEL -.->|Barrier Sweep Clears Asset Flags| m_ANT_RECOV[\"ANT_RECOV (Table Only)\"]:::sideStrand")
lines.append("")
lines.append("    %% --- CHAPTER 3 BOAT HEIST PROTAGONIST SELECTION ---")
lines.append("    m_ROB_BOAT_J -.->|Jason Protagonist Path| m_ROB_BOAT_J_JASON[\"ROB_BOAT_J_JASON\"]:::branching")
lines.append("    m_ROB_BOAT_J -.->|Lucia Protagonist Path| m_ROB_BOAT_L_LUCIA[\"ROB_BOAT_L_LUCIA (Table Only)\"]:::branching")
lines.append("")
lines.append("    %% --- CHAPTER 4 AIRPORT HEIST CONVERGENCE ---")
lines.append("    m_SFH_TAXI -.->|Replay Entry UnlockId| m_MNY_HOTEL")
lines.append("    m_AIR_SCOPE --> m_AIR_TAIL")
lines.append("    m_AIR_SCOPE --> m_AIR_TRAIN")
lines.append("    m_AIR_SCOPE --> m_AIR_BEACH")
lines.append("    m_AIR_SCOPE --> m_AIR_BUS")
lines.append("    m_AIR_SCOPE --> m_AIR_GANG")
lines.append("    m_AIR_SCOPE --> m_AIR_TRUCK")
lines.append("    m_AIR_SCOPE --> m_AIR_DRONE")
lines.append("    m_AIR_SCOPE --> m_AIR_HACK")
lines.append("    m_AIR_SCOPE --> m_AIR_RECRU")
lines.append("    m_AIR_SCOPE --> m_AIR_CATER")
lines.append("    m_AIR_HACK --> m_AIR_FINAL")
lines.append("    m_AIR_CATER --> m_AIR_FINAL")
lines.append("    m_AIR_FINAL -.->|Data Hack Passed Path| m_AIR_FINAL_PASSED[\"AIR_FINAL_DATA_HACK_PASSED\"]:::branching")
lines.append("    m_AIR_FINAL -.->|Data Hack Failed Path| m_AIR_FINAL_FAILED[\"AIR_FINAL_DATA_HACK_FAILED\"]:::branching")
lines.append("    m_AIR_FINAL ==>|Chapter 4 Airport Climax Gate| m_COA_HELIS")
lines.append("")
lines.append("    %% --- CHAPTER 5 FINALE BRANCHING (func_10AD05) ---")
lines.append("    m_BIL_PENT ==>|Confrontation Decision Gate| m_BIL_PENT_M_MENDEZ[\"BIL_PENT_M_MENDEZ (Ending M Target)\"]:::branching")
lines.append("    m_BIL_PENT ==>|Confrontation Decision Gate| m_BIL_PENT_B_BRIAN[\"BIL_PENT_B_BRIAN (Ending B Target)\"]:::branching")
lines.append("    m_BIL_PENT_M_MENDEZ ==>|Mendez Finale Path| m_BIL_FINALE_M[\"BIL_FINALE_M (Ending M Finale)\"]:::bottleneck")
lines.append("    m_BIL_PENT_B_BRIAN ==>|Brian Finale Path| m_BIL_FINAL_B[\"BIL_FINAL_B (Ending B Finale)\"]:::bottleneck")
lines.append("    m_BIL_FINALE_M ==>|Post-Credits Transition| m_FIN_CONT[\"FIN_CONT (Post-Credits Epilogue)\"]:::bottleneck")
lines.append("    m_BIL_FINAL_B ==>|Post-Credits Transition| m_FIN_CONT")
lines.append("    m_FIN_CONT ==>|Campaign Credits Gate| m_INT_CRED[\"INT_CRED (Finale Credits)\"]:::bottleneck")
lines.append("")
lines.append("    %% --- CLASS DEFINITIONS ---")
lines.append("    classDef bottleneck fill:#b71c1c,stroke:#d32f2f,stroke-width:3px,color:#ffffff,font-weight:bold")
lines.append("    classDef coreStory fill:#0d47a1,stroke:#1976d2,stroke-width:2px,color:#ffffff")
lines.append("    classDef sideStrand fill:#37474f,stroke:#78909c,stroke-width:1px,color:#eceff1")
lines.append("    classDef branching fill:#e65100,stroke:#ff9800,stroke-width:2px,color:#ffffff,font-weight:bold")

with open(flow_file, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"Updated {flow_file} successfully.")
