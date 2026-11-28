# Crate loot odds: GTA VI (Xbox build v1.0.2.1)

Per-crate chances for the pickups and weapons inside container crates, worked out from the game's crate loot file
(`container_crates.ymt`) and verified against `game_scarlett_master.exe`. Covers molotovs, the explosives pickup,
heals, ammo boxes, weapons, cash and other items.

## Contents

| Path | What it is |
|---|---|
| `README.md` | This file: method, confirmed rules, results, caveats |
| `scripts/build_crate_odds.py` | Builds all three CSVs in `data/` |
| `scripts/crate_odds_evidence.py` | Prints the checks that back the method |
| `data/crate_prop_names.csv` | 260 prop IDs with their names (matched by position) |
| `data/crate_pool_odds.csv` | Per theme pool and item: layouts containing it and the chance per crate (394 rows) |
| `data/crate_zone_odds.csv` | Per zone type (including `default_unzoned`): weighted chance per crate (208 rows) |

## Confirmed selection rules (from `game_scarlett_master.exe`)

1. **Weighted providers (`VvfvuDA_0xABB1A97D`, `0x3bea820`).** Evaluates any `Condition` on each entry, sums
   `Chance` across valid entries, rolls a uniform `[0, 1)` float from the engine's MWC RNG (`0x5cdcfaa7`), and
   selects the entry where the cumulative weight crosses the roll. Entries point either to another provider or
   directly to a layout.
2. **Pool layout lists (`sopWKEA_0xC7733F67`, `0x3beab50`).** Cycles through the pool's `Layouts` array via
   `layouts[index++ % count]`. Each layout in a pool is therefore selected with **uniform `1 / N` probability**
   per crate.
3. **Zone-type overrides vs. default unzoned crates.**
   - `container_crates.ymt` maps 8 zone types (`airstrip`, `construction`, `industrial`, `military`, `abandoned`,
     `farm`, `medical`, `port`) to providers for all 4 crate models (`prop_am_con_crate_container_01a`,
     `prop_am_con_crate_01a`, `prop_am_con_crate_02a`, `prop_am_con_crate_pallet_01a`).
   - **Military** (`military_con_crate`) is a weighted provider: **20%** `ammo_con_crate` (9 layouts), **40%**
     `policepharm` (3 layouts), and **40%** layout `0c5c0e16` directly (which contains `prop_am_pu_ammo_exp_01a`).
   - **Port** (`port_con_crate`, `pool11`, 13 layouts) combines `food_con_crate` (7) and `pickups_con_crate` (6).
   - **Default (unzoned)** crates use a weighted provider: **80/110 (72.73%)** `pickups_con_crate` (6 layouts) and
     **30/110 (27.27%)** `construction_con_crate` (3 layouts).

## Pools (15 of 16 named)

| Pool | Name | Layouts | Notes |
|---|---|---|---|
| `pool00` | `airstrip_con_crate` | 3 | Used by `airstrip` zone |
| `pool01` | `ammo_con_crate` | 9 | 20% branch of `military_con_crate` |
| `pool02` | `construction_con_crate` | 3 | Used by `construction` zone; 30/110 branch of `default_unzoned` |
| `pool03` | `farm_con_crate` | 6 | Used by `farm` zone |
| `pool04` | `food_con_crate` | 7 | Subset of `port_con_crate` |
| `pool05` | `industrial_con_crate` | 7 | Used by `industrial` zone |
| `pool06` | `medical_con_crate` | 2 | Used by `medical` zone |
| `pool07` | `prison_con_crate` | 2 | Prison personal boxes / clothes / drugs |
| `pool08` | `weapons_con_crate` | 4 | Guncases, ammo boxes, tools, 4 weapon hashes |
| `pool09` | `abandoned_con_crate` | 3 | Used by `abandoned` zone |
| `pool10` | `drugs_con_crate` | 14 | Drug bags, lab gear, pharma |
| `pool11` | `port_con_crate` | 13 | Used by `port` zone (`food_con_crate` + `pickups_con_crate`) |
| `pool12` | `pool12_5ff745b2` | 6 | Luxury/art/decor/footwear (unhashed key `5ff745b2`) |
| `pool13` | `policepharm` | 3 | 40% branch of `military_con_crate` |
| `pool14` | `marina_con_crate` | 4 | Dock fenders, scuba/diving gear, rifle/handgun ammo |
| `pool15` | `pickups_con_crate` | 6 | 80/110 branch of `default_unzoned`; heals, snacks, ammo |

## Key zone-type odds (per crate, engine rules applied)

| Pickup | Zone type | Chance |
|---|---|---|
| Explosives (`prop_am_pu_ammo_exp_01a`) | `military` | 40.0% |
| Explosives | `construction` | 33.33% |
| Explosives | `industrial` | 28.57% |
| Explosives | `farm` | 16.67% |
| Explosives | `default_unzoned` | 9.09% |
| Molotov (`prop_am_con_molotov_01a`) | `construction` | 33.33% |
| Molotov | `industrial` | 28.57% |
| Molotov | `default_unzoned` | 9.09% |
| Trauma kit (`prop_am_com_bag_traumakit_01a`) | `medical` | 50.0% |
| Pen injector (`prop_am_pen_injector_02a`) | `medical` | 50.0% |
| Pills bottle (`prop_am_com_pills_bottle_02a`) | `medical` | 50.0% |
| Trauma kit / pen injector | `farm` | 33.33% each |
| Trauma kit / pen injector / pills bottle | `default_unzoned` | 12.12% each |
| Trauma kit / pen injector / pills bottle | `port` | 7.69% each |

The full tables are in `data/crate_pool_odds.csv` and `data/crate_zone_odds.csv`.

## Remaining caveats

- **Sticky-bomb identity is still unconfirmed.** No prop in `container_crates.ymt` is named "sticky", and
  `prop_am_pu_ammo_exp_01a` is not mapped to an ammo/weapon table in the extracted `common.rpf`/`data.rpf` files.
- **Crate weapon hashes (8 items, type `7a5e90d1`)** are included in the CSVs as `weapon_<hash>`; their
  human-readable weapon names are not yet decoded.
- **Map-wide crate counts/polygons are missing.** Only `construction` (and `prison`) match `popzone` area names
  in `leonida_traffic_data.json`; the other 7 crate zone types are crate/prop-container tags without polygons in
  the traffic data.
- **Non-crate sources.** Game text confirms sticky bombs are sold at Ammu-Nation and stocked by Yasmani
  (`e2c29ada` / `53071e9a`), but shop stock and prices are not in `container_crates.ymt`.

## Reproduce

Run from `crate_loot/scripts`:

```powershell
python -I build_crate_odds.py
python -I crate_odds_evidence.py
```
