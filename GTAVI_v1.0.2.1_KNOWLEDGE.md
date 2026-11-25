Grand Theft Auto VI (Xbox Build v1.0.2.1) — Reverse-Engineered Knowledge Dossier
This dossier consolidates everything recovered and verified from the Xbox Series X|S developer/retail dump (GTA6.Xbox.v1.0.2.1-CYBERLEEK), the decompiled script archive (americas_scripts_23_11_2026), the 0DRP English localization text table, and the Chapter 1 reference flow diagram.
1. Build Architecture, Encryption & File Map
| Artifact / Path | Format & Offset | Contents & Reverse-Engineering Findings |
|---|---|---|
| MicrosoftGame.Config / appxmanifest.xml | XML Manifest | Identifies Title ID 7952987A, package identity RockstarGamesInc.28872443D20A7 v1.0.2.1, target console family Scarlett (Xbox Series X|S), and primary executable game_scarlett_master.exe. |
| Catalog000.bin | PE32+ (x86_64) | Disguised 64-bit Windows/Xbox PE binary (Machine: 0x8664, raw section mapped at RVA 0x1000). |
| common.rpf | RPF9 (0x52504639) @ 0x219000 | Contains the zlib-compressed <CMissions> XML table (145 total entries indexed 1 through 146). |
| data.rpf | RPF9 @ 0x19be000 & 0x12010000 | 0x19be000 holds the 0DRP English localization table (181 recovered mission titles, replay summaries, and objective strings keyed by 32-bit JOAAT hash). 0x12010000 holds the RBF0 <uiProgressDataset> replay menu (97 entries split across Chapters 1–5). |
| pack/story000/story000.rpf | RPF9 (20.02 GB) @ 0x3e30b5000 & 0x3e2372000 | 0x3e30b5000 (PSO, 262,496 bytes inflated) contains the internal story_list_order array (0xB95219D4) and the mission variant map. 0x3e2372000 (PSO, 2,166,996 bytes inflated) stores map trigger coordinates, required player hashes, contact hashes, and time-of-day windows. |
| levels.rpf | RPF9 @ 0x11bb116000 | Secondary PSO trigger table (1,498,864 bytes inflated) mirroring world trigger positions and hour windows. |
| script.rpf & story000_script.rpf | RPF9 (4.35 MB & 78.02 MB) | Compiled RAGE VM script containers (746 scripts in the decompiled americas_scripts_23_11_2026 dump). |
Hashing & Naming Schemes Used by Rockstar
 * Decompiled Script Filenames (0x<16-hex>.ysc.cs): Computed as the top/first 64 bits of 128-bit MurmurHash3 (seed = 0) of the lowercase, expanded script name without .ysc (e.g., mmh3_128("introprologue", seed=0) = fe2c49933556469c78780b969480653f \rightarrow 0xFE2C49933556469C.ysc.cs).
 * In-Script Mission & Entity Identifiers (0x<8-hex>): Computed using standard 32-bit JOAAT (Jenkins One-At-A-Time) on lowercase strings (e.g., joaat("int_prolo") = 0x62131F35, joaat("player_jason") = 0x56D7FE7A, joaat("player_lucia") = 0x4E21D02A).
 * Internal Prefix Expansion Dictionary:
   * INT_ \rightarrow intro (Prologue & Leonida Keys opening arc)
   * BIL_ \rightarrow billionaire (Early archetype name for Mattia and his boss, Bilgeco shipping heir Giorgio Gallo)
   * MTL_ \rightarrow motel (Port Gellhorn / Starlet Motel arc)
   * CLB_ \rightarrow club (Boobie Ike & Dre'Quan / Jack of Hearts & VYB nightclub arc)
   * ROB_ \rightarrow robber (Raul Bautista's crew & smaller bank/convoy jobs)
   * BAN_ \rightarrow bank (Sinfrontera National Bank / La Polilla Negra cartel heist)
   * MNY_ \rightarrow money (Valentina's Y Hotel money laundering & Andrés de León bodyguard arc)
   * AIR_ \rightarrow airport (Kordell Grant's bodybuilder crew & Vice City International Airport heist)
   * COA_ \rightarrow coastguard (Giorgio Gallo's National Coast Guard & cocaine recovery arc)
   * ANT_ \rightarrow antique (Benedict Halifax & Evelyn's Capri antique store / statue arc)
   * COM_ / FT_ / CSC_ / CTI_ / HO_ / UP_ / AO_ \rightarrow Mission archetypes (Community/Contact job, First-Time/Tutorial-style intro, Character Side Content, Contact Intro, Hangout, Unplanned/Ambient, Additional Objective) that are woven directly into the main story campaign.
2. Core Characters, Factions & Story Synopsis
 * Protagonists: Jason (0x56D7FE7A) and Lucia (0x4E21D02A).
 * Chapter 1 — Leonida Keys: Lucia starts in prison (Prologue). Jason works smuggling runs in the Keys for Brian alongside Donnie and Cal, battling a rival gang called the Kingfishers. After Lucia's early release (Coming Home), she reunites with her former cellmate Kat and Kat's wealthy boyfriend Mattia. Mattia hires Jason and Lucia to retrieve a bag from a locker at the Grassrivers Visitor Center (Tourist Trap). The pickup is ambushed by dirty cops led by Captain Méndez; Jason is shot, masked men burn down Jason's house (Home Sweet Home), and Lucia rescues Jason from Vice City Hospital (Discharge Time), escaping west to Port Gellhorn with a mysterious old statue and an encrypted hard drive from the bag.
 * Chapter 2 — Port Gellhorn & Kelly County: Hiding out at the Starlet Motel (What's in the Bag?), Lucia teams up with local dancer Vicki and dealer Dunk to get painkillers for Jason (Girls' Trip, Slam Dunk), meets mechanic Moses Watkins (Moses), and robs Delights Cabaret (Afternoon Delight) and armored vans with dirt biker Billy (Thrillbillies, Twist Wrist, Smash, Grab) before masked men raid the motel and force them to flee to Vice City (Checking Out).
 * Chapter 3 — Vice City & The Sinfrontera Cartel Heist: In Vice City, Jason and Lucia link up with Jason's high school friend Dre'Quan and strip-club boss Boobie Ike at the Jack of Hearts (Welcome to Vice City), deal with local street dealer Tyrone (Tyrone, Here, Kitty Kitty, Spin on This), get scammed by British antiquer Benedict Halifax over the statue (Dubious Provenance), and join master thief Raul Bautista's crew (Andrea, Karim, Felipe). After recruiting safecracker Nicole Park (Security Expert) and hitting Colombian cartel La Polilla Negra, they rob Sinfrontera National Bank (The Cartel Heist).
 * Chapter 4 — Ocean Beach & The VCIA Airport Heist: Moving into the Y Hotel under money launderer Valentina (Ocean Beach), Jason and Lucia hire lawyer Abraham "Abe" Gonzalez (Lawyer Up), protect telenovela star Andrés de León and rescue his son Rafa from the revolutionary group FAP (Party Hard, Adventures in Babysitting, Child's Play), help Dre'Quan's duo The Real Dimez (Roxy & Bae-Luxe) launch at VYB nightclub (Watch It, Fresh Evidence, Headliners), and infiltrate bodybuilder Kordell Grant's crew to hijack their Vice City International Airport (VCIA) vault score (VCIA Takedown). Meanwhile, Karim decrypts the hard drive, revealing blackmail footage of Leonida Senator Camila Fuentes, and discovers the bag belonged to Bilgeco shipping heir Giorgio Gallo. Valentina betrays Raul to Captain Méndez (Sunset), and Giorgio confronts Jason and Lucia (Starting From Zero).
 * Chapter 5 — Coast Guard Raid & Finale: In exchange for a Presidential pardon via Senator Fuentes, Giorgio forces Jason and Lucia to help his Navy ORCA mercenaries (Vinny, Kevin, Liz) steal back his seized cocaine from the National Coast Guard and destroy a rival Albanian mob shipment (Bird in the Hand, Taking Liberties, Doggie Bag, Operation Savage Glory). Giorgio double-crosses them to prosecutor Danica Howard (Protective Custody), leading to the final penthouse assault (The End of the Road) with branching paths involving Brian (BIL_PENT_B_BRIAN / BIL_FINAL_B) and Méndez (BIL_PENT_M_MENDEZ / BIL_FINALE_M).
3. Complete Chapter-by-Chapter Mission Master Table
(Ordered by internal story_list_order from story000.rpf @ 0x3e30b5000, grouped by <uiProgressDataset> chapter filters.)
Chapter 1: Leonida Keys (story_list_position 0–22)
| Pos | Internal ID | In-Game Title | Player | Trigger Coords / Hours | Notes & Variants |
|---|---|---|---|---|---|
| 0 | INT_PROLO | Prologue | Lucia | — | Prison counselor interview (introprologue.ysc). |
| 1 | INT_CHASE | Gone Fishing | Jason | (-1739.3, -4256.4, 2.5) | Rescue Donnie from Kingfishers; Lucia calls about early release. |
| 2 | FT_AMUCO | Gear Up | Jason | (-2145.4, -5531.0, 4.9) | Variants: _FIRST_INTERACTION, _SECOND_INTERACTION. |
| 3 | FT_KMODSHP | Just a Scratch | Jason | (-3089.7, -6606.5, 2.4) | Mandatory gate before Buck Me & Swamped. _SECOND auto-flagged at Ch.2. |
| 4 | COM_KBOS_SHOP | Lab Fees | Jason | (-2950.0, -6374.4, 3.6) | Auto-flagged by func_10AA55 when MTL_WAKE starts. |
| 5 | COM_KMODSHP | (Unnamed Variant) | — | — | Listed in story_list_order (0x17F3BB95); no 0DRP title. |
| 6 | COM_KBOS_COLAT | Unwanted Attention | Jason | (-1486.6, -4755.7, 3.6) | Impound car recovery with Cal; auto-flagged at MTL_WAKE. |
| 7 | COM_KBOS_RADR | Hey Arnold! | Jason | (-2741.2, -6418.5, 5.3) (08:00–16:00) | Track down broker Arnold; auto-flagged at MTL_WAKE. |
| 8 | COM_SFH_MVFN | Feng Shui | Jason | (-2351.5, -5526.7, 7.6) | Rearrange furniture with Cal; triggers 24h wait before Lucia's release. |
| 9 | CSC_TRH_CHART | Island Dreams | Jason | (-2012.2, -5711.2, 2.7) | Scuba dive with Kenton; dead-end side branch off Hey Arnold!. |
| 10 | CTI_PIL_RD_SH | Find Donnie's Package | Jason | — | Replay title: Clean Up After Donnie (CTI_PIL_RD_BC_PARENT). |
| 11 | INT_PRISO | Coming Home | Jason | (-2692.4, -2952.0, 12.4) | Variants: _TRIGGER_EARLY and _TRIGGER_LATE. |
| 12 | INT_BANK | Buck Me | Jason | (-2689.2, -6149.8, 4.8) | Gated behind Just a Scratch completion. |
| 13 | COM_KBOS_PLNDATE | Down to Earth | Jason | (-2547.6, -5863.2, 5.7) (07:00–18:00) | Variant: _PLANE_N_DINNER_DATE. |
| 14 | BIL_FUN | Day Release | Jason | (-2246.8, -5273.6, 4.0) (07:00–17:00) | Ankle tag removed; yacht & Club NINE1NINE with Mattia & Kat. |
| 15 | INT_PLNSH | Clear Skies | Jason | (-6346.6, -6678.3, 3.5) (07:00–23:00) | Seaplane escort with Donnie. |
| 16 | COM_SFH_FLTPK | Building a Life | Jason | (-2350.1, -5535.9, 6.0) | Optional furniture assembly with Lucia. |
| 17 | INT_AIR | Swamped | Jason | (-2542.4, -5829.3, 5.4) | Gated on Day Release + Just a Scratch; Donnie killed by Kingfishers. |
| 18 | COM_KBOS_CLEAN | Don Gone | Jason | (-2683.7, -6050.1, 4.4) | Clean up Donnie's trailer; auto-flagged at MTL_WAKE. |
| — | HO_PAR_KEYCO | Recalibration | Jason | — | Take Cal fishing; replay pos 18; auto-flagged at MTL_WAKE. |
| 20 | BIL_PICK | Tourist Trap | Jason | Day (-3405.6, -6843.2) / Night (-2352.3, -5528.4) | Script checks < 17 clock hour to pick _DAY_TIME_START vs _NIGHT_TIME_START. |
| 21 | BIL_HOUSE | Home Sweet Home | Lucia | (-2351.3, -5523.4, 6.0) | Lucia solo; house burned down by masked men. |
| 22 | BIL_WHEEL | Discharge Time | — | — | Escape Vice City Hospital into Chapter 2. |
(Note: COM_KBOS_NEIGHB — Pipework — is in <CMissions> [Index 8] and Replay Menu Ch.1 [Pos 6], and is auto-flagged at MTL_WAKE, though omitted from the main story_list_order array.)
Chapter 2: Port Gellhorn (story_list_position 23–37)
| Pos | Internal ID | In-Game Title | Player | Coords | Notes & Variants |
|---|---|---|---|---|---|
| 23 | MTL_WAKE | What's in the Bag? | — | — | Chapter 2 start; runs func_10AA55 cleanup flags. |
| 24 | UP_MLSPM | Overnight Charges | Lucia | — | Variant: UP_MLSPM_CONFRONT. |
| 25 | MTL_DRIVE | Girls' Trip | Lucia | (-5350.2, 3460.2, 67.2) | Meet Vicki & Dunk. |
| 26 | MTL_AMBUL | Ambulance Chaser | Lucia | (-5058.8, 3654.2, 36.0) | Destroy the stolen hospital ambulance. |
| 27 | FT_MOTEL_SHOP | Just Moved In | Lucia | — | Alpha convenience store run. |
| 28 | COM_MECH_INTR | Moses | Lucia | — | Unlocks vehicle fencing with Moses Watkins. |
| 29 | MTL_CHECK | Play Nurse | Lucia | (-5362.9, 3483.1, 67.2) | Variants: _LOW_REL, _HIGH_REL, 0x0F9ED9C2. |
| 30 | FT_UP_MMRENT | Behind on Payments | Lucia | — | Variants: _MANAGER_INITIAL, _CONFRONTED, _LATE_NO_COPS, _LATE_COPS. |
| 31 | CTI_MECH_STFC | Daily Driver | Lucia | — | Steal '82 Canis Crawler for Moses. |
| 32 | MTL_PAIN | Slam Dunk | Lucia | (-6438.4, 3691.7, 8.8) | Kidnap Dr. Bill for painkillers. |
| 33 | MTL_MONT | Breakfast Run | Lucia | (-5366.9, 3480.4, 66.8) | Variants: MTL_MONT_AUTOLAUNCH, 0x4CB4EB61. |
| 34 | HO_PAR_FRINT | Coffee Break | — | — | Jason & Lucia plan bigger scores in Kelly County. |
| 35 | MTL_CONT | Afternoon Delight | — | (-6361.1, 3588.8, 7.7) | Rob Delights Cabaret on ladies' night. |
| 36 | MTL_MUD | Thrillbillies | — | (-4820.3, 4348.9, 22.3) | Thrillbilly Mud Club with Billy; unlocks CSC_DRT_CNVY (Twist Wrist, Smash, Grab). |
| 37 | BIL_MOTEL | Checking Out | — | (-5369.5, 3481.8, 66.8) | Variants: _NON_VIOLENT, _VIOLENT, _AUTOLAUNCH. |
Chapter 3: Vice City & Sinfrontera Heist (story_list_position 38–72)
| Pos | Internal ID | In-Game Title | Player | Coords | Notes & Variants |
|---|---|---|---|---|---|
| 38 | CLB_MEET | Welcome to Vice City | Jason | (-1324.7, -1300.1, 15.1) | Meet Dre'Quan & Boobie Ike at Jack of Hearts. |
| 39 | CLB_DEAL | Dealer's Choice | Jason | (-689.9, 1205.9, 7.0) | Drug run with Dre'Quan; Cal fails to crack the hard drive. |
| 40–43 | ANT_INTRO / SRCH / CHASE | Dubious Provenance | — | (-470.7, 1234.3) / (-6845.9, 175.9) | Includes _APARTMENT, _STORAGE, ANT_GIVE, ANT_RECOV, _AUTOLAUNCH. Entire strand is auto-flagged at MNY_HOTEL (Ch.4). |
| 44 | ROB_VEH | Meet the Heders | — | (-475.1, 1236.5, 7.4) | Brian & Lori introduce Raul; steal car with head in trunk. |
| 45 | CSC_MOM_FLIP | Mami Knows Best | Lucia | — | Help Lucia's mom Mia; leads to CSC_MOM_MSEVN (South Leonida Real Estate). |
| 46–48 | COM_DEAL_INTR / DLR_MISS / AO_DEAL_T_SYNTH | Tyrone / Here, Kitty Kitty / Kitty Litter Labs | Jason | — | Tyrone synthetic drug strand (culminates in COM_DLR_COOK / Spin on This). |
| 50–51 | COM_ROB_DRIVEPREP / ROB_DRIVE | Car Service / First Impressions | — | (435.6, 204.2, 3.0) | Decoy getaway for Raul's Fleeca robbery. |
| 52 | BIL_RED | Caught Slipping | — | (-475.7, 1231.3, 8.0) | Apartment burglary; move bag to storage. |
| 53 | CLB_SCUFF | Top Billing | — | (-679.5, 1241.8, 2.7) | Real Dimez vs. DWNPLY at Jack of Hearts. |
| 55 | COM_CBO_CBINT | Boobie Time | Jason | — | Drive Boobie Ike around Little Cuba. |
| 56 | ROB_BOAT_J | Crosstown Traffic | Jason / Lucia | Jason (-1042.2, 1633.3) / Lucia (-366.3, 1723.0) | Dual-character split (ROB_BOAT_J_JASON & ROB_BOAT_L_LUCIA). |
| 57 | CLB_STEAL | Ride or Die | Jason | (-686.3, 1237.9, 3.7) | Steal DWNPLY's car with Dre'Quan. |
| 58 | ROB_BANK | Credit Check | — | (-359.3, 1693.6, 3.3) | Small bank robberies for Raul. |
| 59 | CLB_SETUP | (Unnamed Setup) | — | — | Listed in story_list_order (0xA9331381). |
| 60 | BAN_SETUP | Sinfrontera National Bank | — | (-939.2, -1250.3, 4.9) | Case the bank; unlocks heist prep missions. |
| 61–62 | CTI_SHOW_HATH / AO_SHOW_L_EXP | Steal the Zorrusso for Randy / Randy's Wish List | — | — | Randy Kozlov exotic car export strand (ends with COM_SHOW_TRAILER / Delivery Day). |
| 63 | BAN_RESCU | Security Expert | — | (-54.7, 3620.9, 3.3) | Kidnap safecracker Nicole Park. |
| 64 | BAN_EXPLO | Company Property | — | (-2595.5, -3884.2, 3.3) | Collect weapons from Pilot Pete with Brian. |
| 65 | BAN_CARTE | The Missing Link | Lucia | (-5282.1, -2947.3, 3.5) | Capture & interrogate Monty. |
| 66 | BAN_SAFE | Safe Word | — | (-350.9, 1677.0, 3.6) | Steal practice safe from porn mogul's mansion. |
| 67 | CLB_VIDEO | Cooties | — | (-625.3, 954.7, 3.0) | Variants: _JASON, _LUCIA. |
| 69–70 | BAN_PKBMB / FT_BAN_DISTR | Hidden Charges | — | (-341.1, 1674.9, 6.2) | Plant explosives on cell towers with Karim. |
| 71 | CLB_TOWER | Bricked Up | — | (-473.0, 1237.2, 7.1) | San4San coke pickup interrupted by Méndez raid. |
| 72 | BAN_FINAL | The Cartel Heist | — | (-330.1, 1669.7, 3.2) | Sinfrontera National Bank heist climax. |
Chapter 4: Ocean Beach & VCIA Takedown (story_list_position 73–100)
| Pos | Internal ID | In-Game Title | Player | Coords | Notes & Variants |
|---|---|---|---|---|---|
| 73 | MNY_HOTEL | Ocean Beach | — | (-472.6, 1238.4, 8.1) | Check into Y Hotel; has _AUTOLAUNCH; auto-flags ANT_* strand. |
| 74 | SFH_TAXI | Another Life | — | — | Lucia's arrest flashback. |
| 76 | MNY_CAR | Company Cars | — | (1953.4, 1573.6, 4.5) | Pick up Valentina's high-end cars. |
| 78 | CSC_DIG_DATA | Lawyer Up | — | — | Meet Abe Gonzalez. |
| 79 | MNY_PARTY | Party Hard | — | (-2697.9, -79.0, 5.2) | Megamundo HQ hostage rescue. |
| 80 | CLB_HELI | Photo/Shoot | — | (-850.0, -1538.2, 8.4) | Skyscraper photoshoot & KD rescue. |
| 81 | AIR_TAIL | Heavy Lifting | — | (-610.6, 739.5, 3.8) | Tail Kordell's crew; Karim IDs Giorgio Gallo's hard drive. |
| 82 | AIR_TRAIN | Making Gainz | Lucia | (-331.2, 1668.1, 3.7) | Work out with Nate at Ajax Gym (COM_UP_BBWOR = Blood Sweat and Gear). |
| 83 | AIR_SCOPE | Too Much Baggage | Jason | (-1900.8, -551.9, 2.8) | Plant bugs at VCIA under Omar. |
| 85 | CLB_PROMO | Watch It | Jason | (1538.4, 2087.5, 6.6) | Meet VYB promoter Royce Jones. |
| 86 | MNY_ESCRT | Adventures in Babysitting | Jason | (658.5, 359.7, 4.7) | Bodyguard Andrés de León at The Vault. |
| 87 | AIR_BUS | Amateur Hour | Lucia | (1455.6, 1746.8, 7.4) | Help Cisco collect debt. |
| 88 | AIR_BEACH | Cash Injections | Lucia | (2020.0, 394.6, 3.3) | Synthol deal with Nate. |
| 89 | CLB_EVI | Fresh Evidence | Jason | (-693.7, 1223.6, 6.4) | Steal Dante Fresh's blackmail tapes. |
| 90 | AIR_TRUCK | Power Play | Lucia | (-1257.6, -408.7, 4.3) | Getaway driver while Jason steals Kordell's airport plans. |
| 91 | AIR_GANG | Dirty Work | — | (-336.4, 1680.6, 6.1) | Frame Raina to get her kicked off Kordell's crew. |
| 92 | MNY_KIDNP | Child's Play | — | (-476.2, -294.4, 4.0) | Rescue Rafa from FAP; has _AUTO-LAUNCH variant. |
| 93 | AIR_DRONE | Close Surveillance | Jason | (1853.4, 772.8, 26.2) | Drone surveillance with Karim; decrypt Camila Fuentes footage. |
| 94 | AIR_HACK | Delivery Method | Jason | (-351.0, 1677.1, 3.3) | Plant Lucia's fingerprints in TSS database. |
| 95 | AIR_RECRU | Team Building | Lucia | (1435.3, 1740.0, 6.0) | Underground fight club with Kordell. |
| 96 | AIR_CATER | Fully Catered | — | (-3289.9, 53.8, 14.6) | Steal airport catering truck; variants _DHF, _DHP, _DHS. |
| 97 | CLB_PARTY | Headliners | — | (1965.1, 1165.9, 6.4) | VYB reopening party; defeat DWNPLY. |
| 98 | AIR_FINAL | VCIA Takedown | — | (-351.0, 1677.0, 3.3) | Airport heist double-cross; variants _DATA_HACK_PASSED vs _FAILED. |
| 99 | ROB_DEATH | Sunset | — | (1959.5, 1587.9, 4.5) | Find Raul tortured on his houseboat; escape police. |
| 100 | BIL_CONFR | Starting From Zero | — | (-2173.7, -1875.1, 0.8) | Recover hard drive & statue; first encounter with Giorgio Gallo. |
Chapter 5: Coast Guard & Finale (story_list_position 101–110)
| Pos | Internal ID | In-Game Title | Player | Coords | Notes & Variants |
|---|---|---|---|---|---|
| 101 | COA_HELIS | Bird in the Hand | Lucia | (4.3, -949.5, 188.3) | Scope Coast Guard HQ & steal Mile Zero helicopter. |
| 102 | BIL_PREG | VC Baby | — | (-14.8, -929.2, 184.8) | Kat goes into labor in Giorgio's penthouse. |
| 103 | BIL_BOSS | Taking Liberties | Jason | (-7.6, -918.3, 183.4) | Albanian mob hitman confronts Giorgio at his spa. |
| 104 | COA_DOG | Doggie Bag | — | (0.7, -903.1, 183.5) | Steal Coast Guard sniffer dog Rocco from cruise ship. |
| 105–106 | COA_SHIP / COA_RAID | Operation Savage Glory | — | (-9.6, -940.9, 193.4) | Coast Guard raid; Vinny & Liz killed; Camila Fuentes calls off cops. |
| 107 | BIL_LAW | Honest Abe | — | (-549.4, 188.9, 2.6) | Meet Abe Gonzalez to arrange pardon. |
| 108 | BIL_PENT | The End of the Road | — | Mendez (-1575.8, 635.2) / Brian (-2545.0, -5814.9) | Penthouse assault; splits into BIL_PENT_M_MENDEZ (_M) and BIL_PENT_B_BRIAN (_B). |
| 109 | BIL_PRECI | Protective Custody | — | (-549.4, 188.9, 2.6) | Giorgio betrays Jason & Lucia; Danica Howard interrogation; Méndez ambush. |
| 110 | BIL_FINAL | The End of the Road | Jason | (-150.2, -916.4, 152.9) | Variants BIL_FINAL_B & BIL_FINALE_M checked by func_10AD05 to trigger FIN_CONT (post-game). |
4. Confirmed Speedrun Mechanics & Any% Routing Intelligence
 * Verified func_10AA55 Auto-Flagged Any% Skips (0xD2601E252151E04B.ysc.cs):
   * Triggering Chapter 2 (MTL_WAKE / What's in the Bag?) automatically sets the state flags for FT_KMODSHP_SECOND, COM_KBOS_SHOP (Lab Fees), COM_KBOS_COLAT (Unwanted Attention), COM_KBOS_RADR (Hey Arnold!), COM_KBOS_NEIGHB (Pipework), COM_KBO
