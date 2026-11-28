import json
import os

base_dir = r"C:\Users\<user>\Downloads\GTA6.Xbox.v1.0.2.1-CYBERLEEK"
output_dir = os.path.join(base_dir, "output")

# Load existing mission_order.json
order_file = os.path.join(output_dir, "mission_order.json")
with open(order_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Update metadata
data["metadata"]["status"] = "verified_inventory_with_decompiled_script_state_machine"
data["metadata"]["gxt2_localization_scan"] = {
    "magic_searched": ["GXT2", "2TXG", "0x32545847"],
    "total_chunks_scanned_bytes": "75+ GB across raw and zlib payload streams",
    "result": "completely_absent_in_unencrypted_form",
    "details": "0 valid GXT2 text headers found. Text strings are referenced by 32-bit Jenkins/Joaat hashes. In-game display titles are not present in unencrypted plaintext in the dump."
}
data["metadata"]["script_flow_facts_recovered"] = 28
data["metadata"]["dispatcher_evidence"] = {
    "script": "0xD2601E252151E04B.ysc.cs (Program_0E8E47D1)",
    "func_109E09": "Master mission lookup dispatching 131 mission hashes via binary search tree.",
    "func_10AA55": "Chapter barrier handler: MTL_WAKE sweeps Ch1 compound flags; MNY_HOTEL sweeps ANT_* flags.",
    "func_10AD05": "Campaign finale win condition evaluating BIL_FINALE_M (hash 0xF8FB7ACC) or BIL_FINAL_B (hash 0x96F9A142)."
}

# Prefix taxonomy mapping
# INT_ = Introduction/Prologue Core
# BIL_ = Billy Narrative Core
# MTL_ = Motel / Kelly County Core
# BAN_ = Band / Cartel Heist Arc
# ROB_ = Robbery / Heist Ops
# CLB_ = Nightclub Narrative Strand
# AIR_ = Airport Operation Arc
# MNY_ = Money Laundering Arc
# COA_ = Coastal / Climax Arc
# FT_ = First-Time Tutorial / Interaction
# COM_ = Compound / Faction Territory Strand
# CSC_ = Cutscene / Narrative Vignette
# HO_ = Hangout / Social Vignette
# AO_ = Activity Operation Strand
# UP_ = Universal / Encounter Minor Strand
# CTI_ = Contract / Tip / Target Strand

strand_mapping = {
    "INT": "Main Story Core (Prologue)",
    "BIL": "Main Story Core (Billy Narrative Arc)",
    "MTL": "Main Story Core (Kelly County Arc)",
    "BAN": "Main Story Core (Cartel Heist Arc)",
    "ROB": "Main Story Core (Heist / Robbery Ops)",
    "AIR": "Main Story Core (Airport Operation Arc)",
    "MNY": "Main Story Core (Money Laundering Arc)",
    "COA": "Main Story Core (Coastal / Finale Arc)",
    "CLB": "Narrative Strand (Nightclub Arc)",
    "FT": "Tutorial / First-Time Introduction Strand",
    "COM": "Faction / Compound Territory Strand",
    "CSC": "Cutscene / Narrative Vignette Checkpoint",
    "HO": "Hangout / Social Vignette",
    "AO": "Activity / Operations Strand",
    "UP": "World / Encounter Minor Strand",
    "CTI": "Contract / Tip / Target Strand",
    "SFH": "Safehouse / Hub Taxi Strand"
}

bottleneck_ids = {
    "INT_PROLO": "Campaign Opening Prologue Gate",
    "INT_BANK": "Prologue Heist Climax / Transition Gate",
    "MTL_WAKE": "Chapter 2 Opening Gate (Barrier sweep of Ch1 compound flags in func_10AA55)",
    "BAN_FINAL": "Chapter 3 Cartel Heist Climax",
    "MNY_HOTEL": "Chapter 4 Opening Gate (Barrier sweep of ANT_* flags in func_10AA55)",
    "AIR_FINAL": "Chapter 4 Airport Operation Climax",
    "BIL_PENT": "Chapter 5 Penthouse Confrontation (Mutually exclusive branching gate)",
    "FIN_CONT": "Campaign Epilogue / Post-Credits Transition",
    "INT_CRED": "Campaign Credits Gate"
}

branching_info = {
    "BIL_PENT": {
        "type": "mutually_exclusive_finale_choice",
        "variants": ["BIL_PENT_M_MENDEZ", "BIL_PENT_B_BRIAN"],
        "target_missions": ["BIL_FINALE_M", "BIL_FINAL_B"],
        "script_evidence": "0xD2601E252151E04B.ysc.cs func_10AD05 checks BIL_FINALE_M || BIL_FINAL_B"
    },
    "AIR_FINAL": {
        "type": "heist_outcome_branch",
        "variants": ["AIR_FINAL_DATA_HACK_PASSED", "AIR_FINAL_DATA_HACK_FAILED"],
        "script_evidence": "CMissions UniqueMissionIndex 112 & 113"
    },
    "BIL_MOTEL": {
        "type": "approach_choice",
        "variants": ["BIL_MOTEL_NON_VIOLENT", "BIL_MOTEL_VIOLENT"],
        "script_evidence": "0x514A96DB9A2F0242.ysc.cs cross-references both variants"
    },
    "ROB_BOAT_J": {
        "type": "character_selection",
        "variants": ["ROB_BOAT_J_JASON", "ROB_BOAT_L_LUCIA"],
        "script_evidence": "0x35A38A0C3CB6F988.ysc.cs cross-references both Jason and Lucia rows"
    },
    "AIR_CATER": {
        "type": "setup_disguise_variant",
        "variants": ["AIR_CATER_DHF", "AIR_CATER_DHP", "AIR_CATER_DHS"],
        "script_evidence": "CMissions UniqueMissionIndex 109, 110, 111"
    },
    "BIL_PICK": {
        "type": "time_of_day_variant",
        "variants": ["BIL_PICK_DAY_TIME_START", "BIL_PICK_NIGHT_TIME_START"],
        "script_evidence": "story000.ysc.cs lines 116320..116328 boolean check"
    },
    "INT_PRISO": {
        "type": "trigger_timing_variant",
        "variants": ["INT_PRISO_TRIGGER_EARLY", "INT_PRISO_TRIGGER_LATE"],
        "script_evidence": "CMissions UniqueMissionIndex 123, 124"
    },
    "FT_AMUCO": {
        "type": "tutorial_interaction_stage",
        "variants": ["FT_AMUCO_FIRST_INTERACTION", "FT_AMUCO_SECOND_INTERACTION"],
        "script_evidence": "CMissions UniqueMissionIndex 119, 120"
    },
    "FT_KMODSHP": {
        "type": "tutorial_interaction_stage",
        "variants": ["FT_KMODSHP_FIRST", "FT_KMODSHP_SECOND"],
        "script_evidence": "0x3D9897741AACE500.ysc.cs"
    },
    "ANT_INTRO": {
        "type": "asset_recovery_choice",
        "variants": ["ANT_INTRO_APARTMENT", "ANT_INTRO_STORAGE"],
        "script_evidence": "0x2B87210672A3FA58.ysc.cs and func_10AA55 lines 573049..573076"
    }
}

# Update individual mission entries in data["missions"]
for m in data["missions"]:
    mid = m["id"]
    prefix = mid.split("_")[0]
    m["strand_type"] = strand_mapping.get(prefix, "Other Strand")
    m["is_bottleneck"] = bottleneck_ids.get(mid, None)
    if mid in branching_info:
        m["branching"] = branching_info[mid]
    else:
        m["branching"] = None

# Save updated mission_order.json
with open(order_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("Updated mission_order.json successfully.")
