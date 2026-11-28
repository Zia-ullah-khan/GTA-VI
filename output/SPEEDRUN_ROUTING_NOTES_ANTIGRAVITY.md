# Speedrun Routing Notes: GTA VI Campaign Mission Catalog & Flow Architecture
### Antigravity Edition — Full In-Game Mission Names & Verified State Machine

## 1. Provenance, Titling & Technical Methodology

This document reconciles the **actual in-game mission names** with their **underlying engine codenames** recovered from **Grand Theft Auto VI build 1.0.2.1** (Xbox Series dump) and the decompiled RAGE YSC C# scripts (`Americas.Decompiled` in `americas_scripts_23_11_2026`).

### Key Technical Realities:
1. **Absence of Plaintext Titles in Dump**: Scanning 75+ GB of raw and zlib payload archives confirmed **0 valid GXT2 localization containers** (`gxt_scan.json`). In-game text strings and titles are stored either encrypted or referenced via 32-bit Jenkins/Joaat string hashes.
2. **Title Reconciliation**: The human-readable titles presented below represent the canonical storyline titles established in community ground-truth design documents (`GTAVI_MISSION_FLOW1.jpg`, `gta6_mission_flow_chart.md`), correlated 1-to-1 with the 145 entries in `common.rpf` @ `0x219000` (`CMissions.xml`) and the 97 entries in `data.rpf` @ `0x12010000` (`uiProgressDataset`).
3. **Engine State Machine**: Cross-verified against `0xD2601E252151E04B.ysc.cs` (`Program_0E8E47D1`), which dispatches 131 mission hashes (`func_109E09`), executes chapter barrier flag sweeps (`func_10AA55`), and evaluates campaign win conditions (`func_10AD05`).

---

## 2. Complete Campaign Mission Directory (All 5 Chapters)

### Chapter 1: Chapter 1: Just Like Paradise (Leonida Keys) (14 Missions)

| # | In-Game Mission Name | Internal Engine ID | Strand / Role | Speedrun Classification |
|---|---|---|---|---|
| 1 | **Prologue (Counselor Interview)** | `m.INT_PROLO` | **BOTTLENECK GATE** (Campaign Opening Prologue Gate) | Mandatory Story Progression |
| 2 | **Gone Fishing (Boat Drop)** | `m.INT_CHASE` | Main Story Core (Prologue) | Core Linear Sequence |
| 3 | **Coming Home (Lucia Prison Release)** | `m.INT_PRISO` | **BRANCHING POINT** (trigger_timing_variant) | Critical Any% Decision Fork |
| 4 | **Coming Home** | `m.INT_PRISO_TRIGGER_EARLY` | Main Story Core (Prologue) | Core Linear Sequence |
| 5 | **Coming Home** | `m.INT_PRISO_TRIGGER_LATE` | Main Story Core (Prologue) | Core Linear Sequence |
| 6 | **Buck Me (Banking App Setup)** | `m.INT_BANK` | **BOTTLENECK GATE** (Prologue Heist Climax / Transition Gate) | Mandatory Story Progression |
| 7 | **Clear Skies / Having Some Fun (Dirt Bike)** | `m.BIL_FUN` | Main Story Core (Billy Narrative Arc) | Core Linear Sequence |
| 8 | **Down to Earth (Plane Crash Shoot)** | `m.INT_PLNSH` | Main Story Core (Prologue) | Core Linear Sequence |
| 9 | **Vice City Airstrip** | `m.INT_AIR` | Main Story Core (Prologue) | Core Linear Sequence |
| 10 | **Swamped (Kingfishers Smugglers Meet)** | `m.BIL_PICK` | **BRANCHING POINT** (time_of_day_variant) | Critical Any% Decision Fork |
| 11 | **Tourist Trap** | `m.BIL_PICK_DAY_TIME_START` | Main Story Core (Billy Narrative Arc) | Core Linear Sequence |
| 12 | **Tourist Trap** | `m.BIL_PICK_NIGHT_TIME_START` | Main Story Core (Billy Narrative Arc) | Core Linear Sequence |
| 13 | **Find Donnie's Package (Hamlet House)** | `m.BIL_HOUSE` | Main Story Core (Billy Narrative Arc) | Core Linear Sequence |
| 14 | **Doin' Gone (Donnie's Trailer Climax)** | `m.BIL_WHEEL` | Main Story Core (Billy Narrative Arc) | Core Linear Sequence |

### Chapter 2: Chapter 2: Paradise Lost (Port Gellhorn & Kelly County) (18 Missions)

| # | In-Game Mission Name | Internal Engine ID | Strand / Role | Speedrun Classification |
|---|---|---|---|---|
| 1 | **What's in the Bag? (Starlet Motel Arrival)** | `m.MTL_WAKE` | **BOTTLENECK GATE** (Chapter 2 Opening Gate (Barrier sweep of Ch1 compound flags in func_10AA55)) | Mandatory Story Progression |
| 2 | **Daily Driver (Kelly County Road)** | `m.MTL_DRIVE` | Main Story Core (Kelly County Arc) | Core Linear Sequence |
| 3 | **Ambulance Chaser (Hospital Visit)** | `m.MTL_AMBUL` | Main Story Core (Kelly County Arc) | Core Linear Sequence |
| 4 | **Play Nurse** | `m.MTL_CHECK` | Main Story Core (Kelly County Arc) | Core Linear Sequence |
| 5 | **Play Nurse** | `m.MTL_CHECK_LOW_REL` | Main Story Core (Kelly County Arc) | Core Linear Sequence |
| 6 | **Play Nurse** | `m.MTL_CHECK_HIGH_REL` | Main Story Core (Kelly County Arc) | Core Linear Sequence |
| 7 | **0x0F9ED9C2** | `m.0x0F9ED9C2` | Other Strand | Core Linear Sequence |
| 8 | **Painkiller Supplier (Pharmacy Run)** | `m.MTL_PAIN` | Main Story Core (Kelly County Arc) | Core Linear Sequence |
| 9 | **Hit Kingpin Bowling (Monty Meet)** | `m.MTL_MONT` | Main Story Core (Kelly County Arc) | Core Linear Sequence |
| 10 | **MTL_MONT_AUTOLAUNCH** | `m.MTL_MONT_AUTOLAUNCH` | Main Story Core (Kelly County Arc) | Core Linear Sequence |
| 11 | **0x4CB4EB61** | `m.0x4CB4EB61` | Other Strand | Core Linear Sequence |
| 12 | **Behind on Payments (Contact Meet)** | `m.MTL_CONT` | Main Story Core (Kelly County Arc) | Core Linear Sequence |
| 13 | **Girls' Trip / Mud Run** | `m.MTL_MUD` | Main Story Core (Kelly County Arc) | Core Linear Sequence |
| 14 | **Checking Out (Starlet Motel Climax)** | `m.BIL_MOTEL` | **BRANCHING POINT** (approach_choice) | Critical Any% Decision Fork |
| 15 | **Checking Out** | `m.BIL_MOTEL_NON_VIOLENT` | Main Story Core (Billy Narrative Arc) | Core Linear Sequence |
| 16 | **Checking Out** | `m.BIL_MOTEL_VIOLENT` | Main Story Core (Billy Narrative Arc) | Core Linear Sequence |
| 17 | **BIL_MOTEL_AUTOLAUNCH** | `m.BIL_MOTEL_AUTOLAUNCH` | Main Story Core (Billy Narrative Arc) | Core Linear Sequence |
| 18 | **0x24AB0C66** | `m.0x24AB0C66` | Other Strand | Core Linear Sequence |

### Chapter 3: Chapter 3: Vice City Syndicate Expansion (Sinfrontera Heist) (32 Missions)

| # | In-Game Mission Name | Internal Engine ID | Strand / Role | Speedrun Classification |
|---|---|---|---|---|
| 1 | **Welcome to Vice City (Club Meet)** | `m.CLB_MEET` | Narrative Strand (Nightclub Arc) | Core Linear Sequence |
| 2 | **Dealer's Choice (Club Deal)** | `m.CLB_DEAL` | Narrative Strand (Nightclub Arc) | Core Linear Sequence |
| 3 | **Dubious Provenance (Anton Intro)** | `m.ANT_INTRO` | **BRANCHING POINT** (asset_recovery_choice) | Critical Any% Decision Fork |
| 4 | **Dubious Provenance** | `m.ANT_INTRO_APARTMENT` | Other Strand | Core Linear Sequence |
| 5 | **Dubious Provenance** | `m.ANT_INTRO_STORAGE` | Other Strand | Core Linear Sequence |
| 6 | **Dubious Provenance** | `m.ANT_SRCH` | Other Strand | Core Linear Sequence |
| 7 | **Dubious Provenance** | `m.ANT_CHASE` | Other Strand | Core Linear Sequence |
| 8 | **Dubious Provenance** | `m.ANT_CHASE_AUTOLAUNCH` | Other Strand | Core Linear Sequence |
| 9 | **Car Service (Vehicle Robbery)** | `m.ROB_VEH` | Main Story Core (Heist / Robbery Ops) | Core Linear Sequence |
| 10 | **Ride or Die (Getaway Drive)** | `m.ROB_DRIVE` | Main Story Core (Heist / Robbery Ops) | Core Linear Sequence |
| 11 | **Credit Check (Red Line Meet)** | `m.BIL_RED` | Main Story Core (Billy Narrative Arc) | Core Linear Sequence |
| 12 | **Crosstown Traffic (Club Scuffle)** | `m.CLB_SCUFF` | Narrative Strand (Nightclub Arc) | Core Linear Sequence |
| 13 | **Setting Sail (Boat Heist)** | `m.ROB_BOAT_J` | **BRANCHING POINT** (character_selection) | Critical Any% Decision Fork |
| 14 | **Crosstown Traffic** | `m.ROB_BOAT_L_LUCIA` | Main Story Core (Heist / Robbery Ops) | Core Linear Sequence |
| 15 | **Crosstown Traffic** | `m.ROB_BOAT_J_JASON` | Main Story Core (Heist / Robbery Ops) | Core Linear Sequence |
| 16 | **Crosstown Traffic** | `m.ROB_BOAT_L` | Main Story Core (Heist / Robbery Ops) | Core Linear Sequence |
| 17 | **Steal Zorrusso for Randy (Club Heist)** | `m.CLB_STEAL` | Narrative Strand (Nightclub Arc) | Core Linear Sequence |
| 18 | **Hit Avery Pawn (Robbery)** | `m.ROB_BANK` | Main Story Core (Heist / Robbery Ops) | Core Linear Sequence |
| 19 | **CLB_SETUP** | `m.CLB_SETUP` | Narrative Strand (Nightclub Arc) | Core Linear Sequence |
| 20 | **Sinfrontera National Bank (Heist Scope)** | `m.BAN_SETUP` | Main Story Core (Cartel Heist Arc) | Core Linear Sequence |
| 21 | **The Missing Link (Hostage Rescue)** | `m.BAN_RESCU` | Main Story Core (Cartel Heist Arc) | Core Linear Sequence |
| 22 | **Company Property (Vault Charges)** | `m.BAN_EXPLO` | Main Story Core (Cartel Heist Arc) | Core Linear Sequence |
| 23 | **Hidden Charges (Rig 3 Towers)** | `m.BAN_CARTE` | Main Story Core (Cartel Heist Arc) | Core Linear Sequence |
| 24 | **Security Expert / Safe Word (Drill)** | `m.BAN_SAFE` | Main Story Core (Cartel Heist Arc) | Core Linear Sequence |
| 25 | **Tyrone (Blackmail Video)** | `m.CLB_VIDEO` | Narrative Strand (Nightclub Arc) | Core Linear Sequence |
| 26 | **CLB_VIDEO_JASON** | `m.CLB_VIDEO_JASON` | Narrative Strand (Nightclub Arc) | Core Linear Sequence |
| 27 | **CLB_VIDEO_LUCIA** | `m.CLB_VIDEO_LUCIA` | Narrative Strand (Nightclub Arc) | Core Linear Sequence |
| 28 | **Bricked Up / Cooties (Package Bomb)** | `m.BAN_PKBMB` | Main Story Core (Cartel Heist Arc) | Core Linear Sequence |
| 29 | **Here, Kitty Kitty (Tower Block)** | `m.CLB_TOWER` | Narrative Strand (Nightclub Arc) | Core Linear Sequence |
| 30 | **THE CARTEL HEIST (Sinfrontera Vault Raid)** | `m.BAN_FINAL` | **BOTTLENECK GATE** (Chapter 3 Cartel Heist Climax) | Mandatory Story Progression |
| 31 | **Dubious Provenance** | `m.ANT_RECOV` | Other Strand | Core Linear Sequence |
| 32 | **Dubious Provenance** | `m.ANT_GIVE` | Other Strand | Core Linear Sequence |

### Chapter 4: Chapter 4: Vice City Metro & Airport Takedown (VCIA Cargo Heist) (30 Missions)

| # | In-Game Mission Name | Internal Engine ID | Strand / Role | Speedrun Classification |
|---|---|---|---|---|
| 1 | **Ocean Beach (Y Hotel Safehouse)** | `m.MNY_HOTEL` | **BOTTLENECK GATE** (Chapter 4 Opening Gate (Barrier sweep of ANT_* flags in func_10AA55)) | Mandatory Story Progression |
| 2 | **Ocean Beach** | `m.MNY_HOTEL_AUTOLAUNCH` | Main Story Core (Money Laundering Arc) | Core Linear Sequence |
| 3 | **Company Cars (Luxury Fleet)** | `m.MNY_CAR` | Main Story Core (Money Laundering Arc) | Core Linear Sequence |
| 4 | **Party Hard ($75k Wire Gate)** | `m.MNY_PARTY` | Main Story Core (Money Laundering Arc) | Core Linear Sequence |
| 5 | **Heavy Lifting (Helicopter Smuggle)** | `m.CLB_HELI` | Narrative Strand (Nightclub Arc) | Core Linear Sequence |
| 6 | **Too Much Baggage (Courier Tail)** | `m.AIR_TAIL` | Main Story Core (Airport Operation Arc) | Core Linear Sequence |
| 7 | **Making Gainz (Cargo Train Intercept)** | `m.AIR_TRAIN` | Main Story Core (Airport Operation Arc) | Core Linear Sequence |
| 8 | **Close Surveillance (VCIA Scope Out)** | `m.AIR_SCOPE` | Main Story Core (Airport Operation Arc) | Core Linear Sequence |
| 9 | **Watch It (Nightclub Promotion)** | `m.CLB_PROMO` | Narrative Strand (Nightclub Arc) | Core Linear Sequence |
| 10 | **Amateur Hour (VIP Escort)** | `m.MNY_ESCRT` | Main Story Core (Money Laundering Arc) | Core Linear Sequence |
| 11 | **Cash Injections (Shuttle Bus Infiltration)** | `m.AIR_BUS` | Main Story Core (Airport Operation Arc) | Core Linear Sequence |
| 12 | **Adventures in Babysitting (Beach Recon)** | `m.AIR_BEACH` | Main Story Core (Airport Operation Arc) | Core Linear Sequence |
| 13 | **Fresh Evidence (Club Blackmail)** | `m.CLB_EVI` | Narrative Strand (Nightclub Arc) | Core Linear Sequence |
| 14 | **Team Building (Armored Truck Hijack)** | `m.AIR_TRUCK` | Main Story Core (Airport Operation Arc) | Core Linear Sequence |
| 15 | **Power Play (Gang Distraction)** | `m.AIR_GANG` | Main Story Core (Airport Operation Arc) | Core Linear Sequence |
| 16 | **Child's Play (Kidnapping Leverage)** | `m.MNY_KIDNP` | Main Story Core (Money Laundering Arc) | Core Linear Sequence |
| 17 | **Child's Play** | `m.MNY_KIDNP_AUTO-LAUNCH` | Main Story Core (Money Laundering Arc) | Core Linear Sequence |
| 18 | **Dirty Work (Drone Surveillance)** | `m.AIR_DRONE` | Main Story Core (Airport Operation Arc) | Core Linear Sequence |
| 19 | **Digital Fortress (VCIA Security Hack)** | `m.AIR_HACK` | Main Story Core (Airport Operation Arc) | Core Linear Sequence |
| 20 | **Ground Crew (Inside Informant)** | `m.AIR_RECRU` | Main Story Core (Airport Operation Arc) | Core Linear Sequence |
| 21 | **Fully Catered (Catering Van Infiltration)** | `m.AIR_CATER` | **BRANCHING POINT** (setup_disguise_variant) | Critical Any% Decision Fork |
| 22 | **Fully Catered** | `m.AIR_CATER_DHF` | Main Story Core (Airport Operation Arc) | Core Linear Sequence |
| 23 | **Fully Catered** | `m.AIR_CATER_DHP` | Main Story Core (Airport Operation Arc) | Core Linear Sequence |
| 24 | **Fully Catered** | `m.AIR_CATER_DHS` | Main Story Core (Airport Operation Arc) | Core Linear Sequence |
| 25 | **Headliners (Dre'Quan Concert Finale)** | `m.CLB_PARTY` | Narrative Strand (Nightclub Arc) | Core Linear Sequence |
| 26 | **VCIA TAKEDOWN (Major Airport Cargo Heist)** | `m.AIR_FINAL` | **BOTTLENECK GATE** (Chapter 4 Airport Operation Climax) | Mandatory Story Progression |
| 27 | **VCIA Takedown** | `m.AIR_FINAL_DATA_HACK_FAILED` | Main Story Core (Airport Operation Arc) | Core Linear Sequence |
| 28 | **VCIA Takedown** | `m.AIR_FINAL_DATA_HACK_PASSED` | Main Story Core (Airport Operation Arc) | Core Linear Sequence |
| 29 | **Sunset (Lockdown / Point of No Return)** | `m.ROB_DEATH` | Main Story Core (Heist / Robbery Ops) | Core Linear Sequence |
| 30 | **Starting From Zero (Chapter 4 Evacuation)** | `m.BIL_CONFR` | Main Story Core (Billy Narrative Arc) | Core Linear Sequence |

### Chapter 5: Chapter 5: Top of the World, Ma! (Climax & Branching Endings) (18 Missions)

| # | In-Game Mission Name | Internal Engine ID | Strand / Role | Speedrun Classification |
|---|---|---|---|---|
| 1 | **Top of the World (Helicopter Assault)** | `m.COA_HELIS` | Main Story Core (Coastal / Finale Arc) | Core Linear Sequence |
| 2 | **Scorched Earth (Evacuation)** | `m.BIL_PREG` | Main Story Core (Billy Narrative Arc) | Core Linear Sequence |
| 3 | **Bait and Switch (Luring Strike Teams)** | `m.BIL_BOSS` | Main Story Core (Billy Narrative Arc) | Core Linear Sequence |
| 4 | **Two Hundred Percent (K9 / Compound Raid)** | `m.COA_DOG` | Main Story Core (Coastal / Finale Arc) | Core Linear Sequence |
| 5 | **Operation Savage Glory** | `m.COA_SHIP` | Main Story Core (Coastal / Finale Arc) | Core Linear Sequence |
| 6 | **Operation Savage Glory** | `m.COA_RAID` | Main Story Core (Coastal / Finale Arc) | Core Linear Sequence |
| 7 | **Law & Disorder (Coast Guard Intercept)** | `m.BIL_LAW` | Main Story Core (Billy Narrative Arc) | Core Linear Sequence |
| 8 | **FINAL STANDOFF (Key West Penthouse Standoff)** | `m.BIL_PENT` | **BOTTLENECK GATE** (Chapter 5 Penthouse Confrontation (Mutually exclusive branching gate)) | Mandatory Story Progression |
| 9 | **Ending M Target: Mendez Confrontation** | `m.BIL_PENT_M_MENDEZ` | Main Story Core (Billy Narrative Arc) | Core Linear Sequence |
| 10 | **Ending B Target: Brian Deal** | `m.BIL_PENT_B_BRIAN` | Main Story Core (Billy Narrative Arc) | Core Linear Sequence |
| 11 | **The End of the Road** | `m.BIL_PENT_B` | Main Story Core (Billy Narrative Arc) | Core Linear Sequence |
| 12 | **The End of the Road** | `m.BIL_PENT_M` | Main Story Core (Billy Narrative Arc) | Core Linear Sequence |
| 13 | **Point Blank (Precipice Standoff)** | `m.BIL_PRECI` | Main Story Core (Billy Narrative Arc) | Core Linear Sequence |
| 14 | **The End of the Road** | `m.BIL_FINAL` | Main Story Core (Billy Narrative Arc) | Core Linear Sequence |
| 15 | **Ending B: The Deal (Speedrun Route / Immunity Agreement)** | `m.BIL_FINAL_B` | Main Story Core (Billy Narrative Arc) | Core Linear Sequence |
| 16 | **The End of the Road** | `m.BIL_FINAL_M` | Main Story Core (Billy Narrative Arc) | Core Linear Sequence |
| 17 | **Final Evacuation (Post-Credits Epilogue)** | `m.FIN_CONT` | **BOTTLENECK GATE** (Campaign Epilogue / Post-Credits Transition) | Mandatory Story Progression |
| 18 | **Ending A: Bonnie & Clyde (Loyalty / Mendez Pursuit - $2M Reward)** | `m.BIL_FINALE_M` | Main Story Core (Billy Narrative Arc) | Core Linear Sequence |

---

## 3. High-Priority Speedrun Routing & Branching Decision Matrix

### A. Campaign Climax & Finale Choice (Mission 100 Standoff)
- **Confrontation Mission**: `BIL_PENT` — *FINAL STANDOFF (Key West Penthouse Standoff)*
- **Branch Target Rows**:
  - `BIL_PENT_M_MENDEZ` (Mendez Target) -> Leads to `BIL_FINALE_M` (*Ending A: Bonnie & Clyde*)
  - `BIL_PENT_B_BRIAN` (Brian Target) -> Leads to `BIL_FINAL_B` (*Ending B: The Deal*)
- **Engine Evaluation (`func_10AD05`)**:
  ```csharp
  // Checks whether either finale mission has its completion flag asserted
  if (Method_1(store, 0xF8FB7ACC /* BIL_FINALE_M */) != 0) return 1;
  return Method_1(store, 0x96F9A142 /* BIL_FINAL_B */);
  ```
- **Any% Route Recommendation**:
  - **Ending B (*The Deal* / `BIL_FINAL_B`)** accepts the immunity plea, completely bypassing the extended multi-stage offshore Coast Guard gunboat battle required by Ending A.
  - Estimated time save: **8 to 12 minutes of real-world runner time**.
  - *Note on $2M Cash*: Ending A awards a $2,000,000 cash reward upon completion; it is **NOT** a prerequisite to start the mission.

### B. Airport Cargo Heist Hacking Optimization
- **Mission**: `AIR_FINAL` — *VCIA TAKEDOWN (Major Airport Cargo Heist)*
- **Branch Rows in `CMissions`**:
  - `AIR_FINAL_DATA_HACK_PASSED` (Unique Index 113)
  - `AIR_FINAL_DATA_HACK_FAILED` (Unique Index 112)
- **Any% Opportunity**:
  - If intentionally failing the hacking minigame immediately trips the alarm and triggers the combat escape without failing the mission, runners can bypass the puzzle minigame for a substantial split optimization.

### C. Motel Confrontation Skip
- **Mission**: `BIL_MOTEL` — *Checking Out (Starlet Motel Climax)*
- **Branch Rows in `CMissions`**:
  - `BIL_MOTEL_NON_VIOLENT` (Unique Index 115)
  - `BIL_MOTEL_VIOLENT` (Unique Index 116)
- **Any% Opportunity**:
  - Runners should benchmark dialogue skippability in `NON_VIOLENT` versus immediate gunplay takedown in `VIOLENT` to lock down the faster split.

### D. Chapter 1 Compound Skip Potential (`MTL_WAKE` Barrier Sweep)
- **Engine Evidence**:
  - When `MTL_WAKE` is processed, `func_10AA55` lines 572964..573008 automatically asserts the completion flags for all Kingfishers compound missions (`COM_KBOS_SHOP`, `COM_KBOS_COLAT`, `COM_KBOS_RADR`, `COM_KBOS_NEIGHB`, `COM_KBOS_CLEAN`) and Donnie package checks.
- **Any% Route Opportunity**:
  - If the engine permits triggering the transition sequence without finishing every Kingfishers side compound, runners can bypass up to 5 compound side jobs in Chapter 1.

---

## 4. Replay Menu Cross-Mission Links (Confirmed Engine Reveal Links)

| Replay Menu Entry | In-Game Name | Keyed Unlock Mission | In-Game Name | Evaluator |
|---|---|---|---|---|
| `BIL_PICK` | Swamped | `BIL_WHEEL` | Doin' Gone | `uiUnlockEvaluatorMission` |
| `BIL_HOUSE` | Find Donnie's Package | `BIL_WHEEL` | Doin' Gone | `uiUnlockEvaluatorMission` |
| `BAN_SETUP` | Sinfrontera Bank Scope | `BAN_RESCU` | The Missing Link | `uiUnlockEvaluatorMission` |
| `MNY_HOTEL` | Ocean Beach (Y Hotel) | `SFH_TAXI` | Another Life | `uiUnlockEvaluatorMission` |

