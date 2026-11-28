import os

base_dir = r"C:\Users\<user>\Downloads\GTA6.Xbox.v1.0.2.1-CYBERLEEK"
notes_file = os.path.join(base_dir, "output", "SPEEDRUN_ROUTING_NOTES.md")

content = """# Speedrun Routing Notes: GTA VI Build 1.0.2.1 (Xbox Series) & Decompiled YSC Scripts

## 1. Executive Summary & Provenance

This document synthesizes verified findings recovered directly from the game files of **Grand Theft Auto VI build 1.0.2.1** (Xbox Series dump) cross-referenced with the decompiled RAGE YSC C# scripts (`Americas.Decompiled` in `americas_scripts_23_11_2026`).

All information herein is derived strictly from binary structures, metadata manifests, and script decompilation. No external rumors, leaks, or unverified community assertions are used.

### Primary File Sources
1. **`common.rpf` @ `0x219000` (`CMissions.xml`)**:
   - Master mission registration table containing **145 entries** with `UniqueMissionIndex`, `MissionId`, `Description` (text key), and `TextureName`.
2. **`data.rpf` @ `0x12010000` (`uiProgressDataset` in RBF0)**:
   - Progress and replay menu configuration containing **97 mission entries** categorized into 5 sequential chapter filters:
     - Chapter 1: 22 missions
     - Chapter 2: 13 missions
     - Chapter 3: 28 missions
     - Chapter 4: 27 missions
     - Chapter 5: 7 missions
3. **`0xD2601E252151E04B.ysc.cs` (`Program_0E8E47D1`)**:
   - Master story narrative and mission state manager imported directly by `story000.ysc.cs`:
     - `func_109E09`: Mission registry lookup evaluating **131 mission hashes** via a compiled binary search dispatch tree.
     - `func_10AA55`: Chapter barrier state handler managing flag sweeps at chapter transitions.
     - `func_10AD05`: Campaign finale evaluation checking `BIL_FINALE_M` or `BIL_FINAL_B`.
4. **`story000.ysc.cs` (`Program_5B5EEFFE`)**:
   - Master story orchestrator script managing global mission threads, time-of-day checks, and cutscene triggers.

---

## 2. GXT2 Localization Scan Results (Verified Fact)

A comprehensive binary scan was performed across all extracted RPF archives and raw payload chunks (over 75 GB of data) for the RAGE localization table magic `GXT2` / `2TXG` (`0x32545847` / `0x47585432`):

- **Scan Results**:
  - Compressed zlib streams starting with GXT2: **0**
  - Valid raw GXT2 container headers: **0** (the only 4 occurrences in raw dumps are non-header random byte collisions in compressed data, verified by `header_plausible == False` in `work/gxt_scan.json`).
- **Conclusion**:
  - **In-game display titles are completely absent in unencrypted form in the dump.**
  - Game strings and mission titles are referenced exclusively by their 32-bit Jenkins/Joaat hashes (e.g., `INT_PROLO`, `PROG_INT_PROLO_DESC_REPLAY`, `GRID_SML_L_CH1_INT_PROLO`).
  - Text localization is either encrypted with platform-specific keys, stored in separate language packages not present in this build slice, or streamed on demand.

---

## 3. Mission Taxonomy: Main Story Core vs. Side-Strands

Analysis of mission prefixes and dedicated script references establishes a clear taxonomy distinguishing the **Main Story Core** from **Side-Strands**, **Faction Compounds**, and **Tutorial Vignettes**:

| Prefix | Category | Role in Campaign | Any% Speedrun Relevance |
|---|---|---|---|
| **`INT_`** | Main Story Core | Prologue & Early Campaign Progression (`INT_PROLO`, `INT_CHASE`, `INT_PRISO`, `INT_BANK`, `INT_AIR`) | **Mandatory Linear Bottlenecks** |
| **`BIL_`** | Main Story Core | Billy Narrative Arc spanning Chapters 1, 2, 3, and 5 (`BIL_FUN`, `BIL_PICK`, `BIL_MOTEL`, `BIL_RED`, `BIL_PENT`) | **Mandatory Narrative Backbone** |
| **`MTL_`** | Main Story Core | Kelly County / Motel Recovery Arc in Chapter 2 (`MTL_WAKE`, `MTL_DRIVE`, `MTL_MONT`, `MTL_MUD`) | **Mandatory Chapter 2 Core** |
| **`BAN_`** | Main Story Core | Sinfrontera Cartel Heist Arc in Chapter 3 (`BAN_SETUP`, `BAN_RESCU`, `BAN_EXPLO`, `BAN_CARTE`, `BAN_SAFE`, `BAN_FINAL`) | **Mandatory Heist Convergence** |
| **`AIR_`** | Main Story Core | Vice City Airport Operation Arc in Chapter 4 (`AIR_SCOPE`, `AIR_TAIL`, `AIR_TRAIN`, `AIR_HACK`, `AIR_FINAL`) | **Mandatory Heist Convergence** |
| **`ROB_`** | Main Story Core | Major Robberies & Getaways (`ROB_VEH`, `ROB_DRIVE`, `ROB_BOAT_J`, `ROB_BANK`, `ROB_DEATH`) | **Mandatory Heist Operations** |
| **`MNY_`** | Main Story Core | Money Laundering & Escort Arc in Chapter 4 (`MNY_HOTEL`, `MNY_CAR`, `MNY_PARTY`, `MNY_ESCRT`, `MNY_KIDNP`) | **Mandatory Chapter 4 Core** |
| **`COA_`** | Main Story Core | Coastal Climax Operations in Chapter 5 (`COA_HELIS`, `COA_DOG`, `COA_SHIP`) | **Mandatory Finale Lead-in** |
| **`CLB_`** | Narrative Strand | Nightclub Operations & Vice City Contacts (`CLB_MEET`, `CLB_DEAL`, `CLB_STEAL`, `CLB_VIDEO`, `CLB_TOWER`) | Narrative Strand / Heist Support |
| **`COM_`** | Faction / Compound Strand | Faction Territory Operations (Kingfishers, Kolt, Guardia Brothers, San4San, M7, PTTY) | **High Any% Skip Potential** |
| **`FT_`** | Tutorial / First-Time Strand | First-Time Interactions & System Introductions (`FT_AMUCO`, `FT_KMODSHP`, `FT_MOTEL_SHOP`) | Tutorial / Potential Quick Completion |
| **`CSC_`** | Cutscene Vignette | Narrative Vignette & Route Transition Checkpoints (`CSC_TRH_CHART`, `CSC_DRT_CNVY`, `CSC_MOM_FLIP`) | Cutscene Checkpoints |
| **`HO_`** | Hangout Vignette | Neighborhood & Social Vignettes (`HO_PAR_KEYCO`, `HO_PAR_FRINT`) | Social / High Skip Potential |
| **`AO_`** | Activity Strand | Specialized Operations (`AO_DEAL_T_SYNTH`, `AO_SHOW_L_EXP`) | Activity / Side Strand |
| **`UP_`** | World Encounter | Minor World Encounters (`UP_MLSPM`, `UP_MLSPM_CONFRONT`) | Minor Encounter |

---

## 4. Linear Bottlenecks vs. Parallel Tracks

Script analysis in `0xD2601E252151E04B.ysc.cs` confirms that GTA VI combines **strict linear bottleneck gates** between chapters with **parallel multi-track setup structures** inside chapters:

```
[Chapter 1: Prologue] ──> [MTL_WAKE] (Ch2 Gate) ──> [BIL_MOTEL] (Ch2 Climax)
                                                            │
    ┌───────────────────────────────────────────────────────┘
    ▼
[Chapter 3 Parallel Tracks]
    ├── CLB_* Track (Nightclub)
    ├── ROB_* Track (Robbery Preps)
    └── BAN_* Track (Cartel Setups) ──> [BAN_FINAL] (Ch3 Climax Gate)
                                                │
    ┌───────────────────────────────────────────┘
    ▼
[Chapter 4 Parallel Tracks]
    ├── MNY_* Track (Laundering)
    └── AIR_* Track (Airport Preps) ──> [AIR_FINAL] (Ch4 Climax Gate)
                                                │
    ┌───────────────────────────────────────────┘
    ▼
[Chapter 5 Climax] ───────────────> [BIL_PENT] (Decision Gate)
                                        ├──> Ending M: BIL_FINALE_M
                                        └──> Ending B: BIL_FINAL_B
                                                │
                                                ▼
                                            [FIN_CONT] ──> [INT_CRED]
```

### Confirmed Linear Bottlenecks:
1. **`INT_PROLO` -> `INT_CHASE` -> `INT_PRISO` -> `INT_BANK`**:
   - The opening prologue is strictly sequential.
2. **`MTL_WAKE` (Chapter 2 Gate)**:
   - Entering Chapter 2 executes a barrier sweep in `func_10AA55` lines 572964..573008, explicitly setting the state flags for:
     - `FT_KMODSHP_SECOND`
     - `COM_KBOS_SHOP`, `COM_KBOS_COLAT`, `COM_KBOS_RADR`, `COM_KBOS_NEIGHB`, `COM_KBOS_CLEAN`
     - `HO_PAR_KEYCO`
     - `RecoverDropTipShackDonnieAlive` / `RecoverDropTipShackDonnieDeadUnknown`
   - **Speedrun Implication**: Any Chapter 1 compound or hangout task not strictly required to trigger `MTL_WAKE` is swept by the engine, indicating potential Any% skips of Chapter 1 side content.
3. **`BAN_FINAL` (Chapter 3 Heist Climax)**:
   - The Cartel Heist acts as the convergence bottleneck for Chapter 3 setups (`BAN_EXPLO`, `BAN_CARTE`, `BAN_SAFE`, `BAN_PKBMB`).
4. **`MNY_HOTEL` (Chapter 4 Gate)**:
   - Entering Chapter 4 executes a barrier sweep in `func_10AA55` lines 572946..573082, resolving:
     - `ANT_SRCH`, `ANT_RECOV`
     - `ANT_CHASE` / `ANT_CHASE_AUTOLAUNCH`
     - `ANT_INTRO_APARTMENT` / `ANT_INTRO_STORAGE`
5. **`AIR_FINAL` (Chapter 4 Airport Climax)**:
   - Climax of the Vice City Airport operation converging all `AIR_*` preparation tracks.
6. **`BIL_PENT` (Chapter 5 Climax Gate)**:
   - The final confrontation gate that branches into mutually exclusive finale missions.

---

## 5. Speedrun-Critical Branching & Any% Routing Opportunities

Several missions feature distinct branching rows in `CMissions` and dedicated script logic:

### A. The Mutually Exclusive Finale Branch (Ending M vs. Ending B)
- **Target Gate**: `BIL_PENT` (UniqueMissionIndex 97)
- **Branch Options**:
  - `BIL_PENT_M_MENDEZ` (Index 102) -> Leads to `BIL_FINALE_M` (Index 144)
  - `BIL_PENT_B_BRIAN` (Index 103) -> Leads to `BIL_FINAL_B` (Index 145)
- **Engine Verification**:
  - In `0xD2601E252151E04B.ysc.cs` (`func_10AD05`), the story completion evaluator explicitly checks:
    ```csharp
    if (Method_1(store, 0xF8FB7ACC /* BIL_FINALE_M */) != 0) return 1;
    return Method_1(store, 0x96F9A142 /* BIL_FINAL_B */);
    ```
- **Speedrun Routing Recommendation**:
  - Time both `BIL_FINALE_M` and `BIL_FINAL_B` routes once runnable to determine which path has shorter cutscenes, faster combat encounters, and quicker vehicle transit to `FIN_CONT` (Index 134) and `INT_CRED` (Index 108).

### B. Airport Heist Data Hack Outcome
- **Mission**: `AIR_FINAL` (UniqueMissionIndex 88)
- **Variants in `CMissions`**:
  - `AIR_FINAL_DATA_HACK_PASSED` (Index 113)
  - `AIR_FINAL_DATA_HACK_FAILED` (Index 112)
- **Speedrun Routing Opportunity**:
  - In many RAGE engine heists, failing a secondary objective (like data hacking) triggers an immediate loud alarm / violent escape. If `AIR_FINAL_DATA_HACK_FAILED` does not cause mission failure but immediately bypasses stealth hacking minigames, it could represent a massive Any% time save.

### C. Motel Confrontation Approach
- **Mission**: `BIL_MOTEL` (UniqueMissionIndex 34)
- **Variants in `CMissions`**:
  - `BIL_MOTEL_NON_VIOLENT` (Index 115)
  - `BIL_MOTEL_VIOLENT` (Index 116)
- **Script Evidence**:
  - Script `0x514A96DB9A2F0242.ysc.cs` cross-references both options.
- **Speedrun Routing Opportunity**:
  - Compare dialogue skip duration in `NON_VIOLENT` vs. immediate weapon takedown in `VIOLENT`.

### D. Boat Heist Protagonist Routing
- **Mission**: `ROB_BOAT_J` (UniqueMissionIndex 51)
- **Variants in `CMissions`**:
  - `ROB_BOAT_J_JASON` (Index 143)
  - `ROB_BOAT_L_LUCIA` (Index 131)
- **Script Evidence**:
  - Script `0x35A38A0C3CB6F988.ysc.cs` cross-references both protagonist paths.
- **Speedrun Routing Opportunity**:
  - Determine whether Jason or Lucia has the faster objective split (e.g., driver vs. shooter role).

### E. Catering Disguise Options
- **Mission**: `AIR_CATER` (UniqueMissionIndex 87)
- **Variants in `CMissions`**:
  - `AIR_CATER_DHF` (Index 109)
  - `AIR_CATER_DHP` (Index 110)
  - `AIR_CATER_DHS` (Index 111)
- **Speedrun Routing Opportunity**:
  - Three distinct catering setup methods exist. Route runners should test travel distance and setup requirements for each.

---

## 6. Replay Menu Cross-Mission Links (Observed Facts)

In `data.rpf` (`uiProgressDataset`), 4 replay entries specify an `UnlockId` that points to a different mission:

| Replay Entry (`item_id`) | Unlock Trigger (`unlock_id`) | Chapter Filter | Evaluator |
|---|---|---|---|
| `BIL_PICK` | `BIL_WHEEL` | Chapter 1 | `uiUnlockEvaluatorMission` |
| `BIL_HOUSE` | `BIL_WHEEL` | Chapter 1 | `uiUnlockEvaluatorMission` |
| `BAN_SETUP` | `BAN_RESCU` | Chapter 3 | `uiUnlockEvaluatorMission` |
| `MNY_HOTEL` | `SFH_TAXI` | Chapter 4 | `uiUnlockEvaluatorMission` |

*Note: These indicate replay-menu reveal relationships in the UI, corroborating narrative dependencies between these mission pairs.*

---

## 7. Speedrun Route Verification Checklist

When routing Any% or 100% categories, runners should verify:
1. **Can Chapter 1 compound tasks (`COM_KBOS_*`) be completely bypassed?**
   - Check if `MTL_WAKE` can be triggered immediately after `INT_BANK` without completing the full Kingfishers compound chain.
2. **Which Chapter 3 Heist preps are strictly mandatory?**
   - Verify whether all 4 setups (`BAN_EXPLO`, `BAN_CARTE`, `BAN_SAFE`, `BAN_PKBMB`) must be completed or if specific setup combinations unlock `BAN_FINAL`.
3. **Data Hack Fail Routing in `AIR_FINAL`**:
   - Test whether triggering `AIR_FINAL_DATA_HACK_FAILED` shortens mission completion time compared to completing the hack minigame.
4. **Mendez vs. Brian Finale Delta**:
   - Accurately time `BIL_FINALE_M` vs. `BIL_FINAL_B` from penthouses trigger to final credits roll.
"""

with open(notes_file, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Updated {notes_file} successfully.")
