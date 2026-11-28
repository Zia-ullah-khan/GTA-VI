# Fastest vehicles and where a fixed one spawns

Built from the game's vehicle performance table and its special-spawn catalog. The figures are the game's own values, and areas come from catalog identifiers. Game-text descriptions are left out of this copy.

## Sources

| Data | Source | Notes |
|---|---|---|
| Performance | `CVehiclePerformanceMaps`, plain XML | 251 vehicles |
| Cross-check | `CVehicleBaseRatingsAndEstimatesMap`, plain XML | independent estimates; broadly agrees on the ordering |
| Special spawns | `GRID_SML_L_VEH_<model>_<KIND>_<AREA>_…` catalog identifiers | 267 entries |

**Units.** `topSpeed` is unlabelled in the file. It behaves like metres per second, so km/h is `× 3.6`. The ordering does not depend on this.

A model can have several special spawns, each tagged with a kind (UNIQUE, CHAR, EXCON, CMP, AMB, MIS and others). The pick-up table lists each one separately.

## Pick-up list: fastest road vehicles with a placed spawn

| # | Model | km/h | 0–60 | Area | Catalog label |
|---|---|---|---|---|---|
| 1 | `emerus` | 260 | 2.92 | Kelly County | Racecar |
| 2 | `tempesta` | 256 | 2.78 | Ocean Beach | Police |
| 3 | `tempesta` | 256 | 2.78 | Tequesta | Iridescentgreen |
| 4 | `comet7` | 246 | 3.12 | Salton | Motel |
| 5 | `italirsx` | 244 | 2.60 | Crosstown | Statusauto |
| 6 | `coquette4` | 230 | 3.68 | Capri | Police |
| 7 | `coquette4` | 230 | 3.68 | Stockyard | Vicevinyl |
| 8 | `vigero3` | 220 | 4.58 | Key Lento | Custom |
| 9 | `cypher` | 216 | 4.07 | Bayside | Artistcar |
| 10 | `cypher` | 216 | 4.07 | Crosstown | Statusauto |
| 11 | `paragon` | 212 | 3.97 | Waning Sands | Blackandgold |
| 12 | `cometretro` | 208 | 4.55 | Capri | Musician |
| 13 | `banshee` | 207 | 5.35 | Hamlet | Liftedracecar |
| 14 | `toros` | 206 | 4.05 | Leaf Links | Goldenwheels |
| 15 | `double` | 204 | 3.77 | La Perle | Sound4Sound |
| 16 | `coquette2` | 201 | 6.05 | Crosstown | Rustyclassic |
| 17 | `dominator7` | 199 | 5.35 | Ambrosia | Americanaracecar |
| 18 | `dominator7` | 199 | 5.35 | Kelly County | Racecar |
| 19 | `dominator7` | 199 | 5.35 | Rockridge | Blackwindows |
| 20 | `fcr` | 197 | 4.53 | Airport | Goldenwheels |
| 21 | `stallion` | 193 | 5.58 | Waning Sands | Restomod |
| 22 | `baller8` | 192 | 5.47 | Washington Beach | Black |
| 23 | `gauntlet5` | 192 | 7.03 | Ambrosia | Bigblock |
| 24 | `gauntlet5` | 192 | 7.03 | Grayson | Rustedout |
| 25 | `penumbra` | 191 | 6.68 | Capri | Pink |
| 26 | `esskey` | 190 | 5.77 | Southside | Thicktires |
| 27 | `elegy` | 189 | 5.27 | Kelly County | Driftcar |
| 28 | `baller2` | 188 | 5.53 | Belville | Goldenwheels |
| 29 | `jubilee` | 186 | 5.70 | Leaf Links | Bronze |
| 30 | `penumbraff` | 186 | 6.83 | Ambrosia | Racecar |

## Fastest overall

| Model | top (m/s) | km/h | 0–60 | brake 60–0 | road? |
|---|---|---|---|---|---|
| `lazer` | 116.0 | 417 | 1.80 | 0.0 | no |
| `thrax` | 76.6 | 276 | 2.43 | 16.8 | yes |
| `emerus` | 72.3 | 260 | 2.92 | 17.1 | yes |
| `pulsebike` | 71.8 | 258 | 4.13 | 17.7 | yes |
| `vitello` | 71.4 | 257 | 2.75 | 18.8 | yes |
| `tempesta` | 71.0 | 256 | 2.78 | 17.8 | yes |
| `gauntlet4` | 69.5 | 250 | 3.32 | 21.0 | yes |
| `furia` | 69.2 | 249 | 2.78 | 19.4 | yes |
| `comet7` | 68.2 | 245 | 3.12 | 19.5 | yes |
| `valkyrie` | 67.7 | 244 | 4.98 | 0.0 | no |
| `italirsx` | 67.7 | 244 | 2.60 | 18.1 | yes |
| `buzzard` | 66.9 | 241 | 7.23 | 0.0 | no |
| `zorrusso` | 66.7 | 240 | 3.52 | 18.2 | yes |
| `mallard` | 64.3 | 232 | 0.73 | 0.0 | no |
| `infernus2` | 64.2 | 231 | 3.93 | 20.1 | yes |
| `neon` | 64.0 | 230 | 3.02 | 20.9 | yes |
| `coquette4` | 63.9 | 230 | 3.68 | 19.3 | yes |
| `mambagt` | 62.6 | 226 | 3.95 | 23.6 | yes |

`lazer` is the jet, and `valkyrie` and `buzzard` are helicopters. Aircraft and boats have no braking distance or turn radius in the data, so they are marked not road.

## Best acceleration among road cars

| Model | 0–60 | km/h |
|---|---|---|
| `thrax` | 2.43 | 276 |
| `italirsx` | 2.60 | 244 |
| `vitello` | 2.75 | 257 |
| `tempesta` | 2.78 | 256 |
| `furia` | 2.78 | 249 |
| `emerus` | 2.92 | 260 |
| `neon` | 3.02 | 230 |
| `comet7` | 3.12 | 245 |
| `gauntlet4` | 3.32 | 250 |
| `sfb1000` | 3.42 | 223 |
| `zorrusso` | 3.52 | 240 |
| `coquette4` | 3.68 | 230 |

## Best road car in each placed area

| Area | Best road vehicle | km/h | Others there |
|---|---|---|---|
| Airport | `fcr` | 197 | — |
| Ambrosia | `dominator7` | 199 | `gauntlet5`, `penumbraff`, `picador`, `caracara4x4`, `zombieb` |
| Bayside | `cypher` | 216 | `dominatorclassic` |
| Belville | `baller2` | 188 | `zion2` |
| Capri | `coquette4` | 230 | `cometretro`, `penumbra`, `bobcatxl`, `caracara4x4`, `sungrazer` |
| Crosstown | `italirsx` | 244 | `cypher`, `coquette2` |
| Downtown | `cavalcade3` | 178 | — |
| Frogswater | `picador` | 186 | — |
| Gellhorn | `cliffhanger` | 167 | `bandito` |
| Grassrivers | `sovereign107` | 185 | `bison900`, `enduro`, `sanchez`, `sanchez`, `boxville` |
| Grayson | `gauntlet5` | 192 | — |
| Hamlet | `banshee` | 207 | `bandito` |
| Kelly County | `emerus` | 260 | `dominator7`, `elegy`, `sovereign107`, `manchez` |
| Key Lento | `vigero3` | 220 | `ruiner`, `akane`, `woodland`, `hustler`, `yougaxl` |
| La Perle | `double` | 204 | — |
| Leaf Links | `toros` | 206 | `jubilee` |
| Leonard County | `sanchez` | 147 | `declasse500` |
| Lummox County | `zombieb` | 161 | — |
| Millport | `yougaxl` | 126 | — |
| Ocean Beach | `tempesta` | 256 | — |
| Peacock Bay | `cavalcade3` | 178 | — |
| Port Gellhorn | `blista2` | 172 | `yosemite1500`, `caracara4x4`, `marshall` |
| Rockridge | `dominator7` | 199 | — |
| Salton | `comet7` | 246 | — |
| Southside | `esskey` | 190 | — |
| Stockyard | `coquette4` | 230 | — |
| Tequesta | `tempesta` | 256 | `schafters` |
| Waning Sands | `paragon` | 212 | `stallion` |
| Washington Beach | `baller8` | 192 | `zombieb` |
| Watson Bay | `phoenix` | 166 | `youga2`, `blazer4`, `journey`, `journey` |

## Caveats

- `topSpeed` is unlabelled in the file and behaves like metres per second. Braking and acceleration units are unlabelled too, so the tables rely on ordering rather than absolute values.
- An area is a named region, not a parking space. Exact positions would need the vehicle generator data, which is not decoded here.
- Story availability is not modelled. A vehicle existing at a spot does not mean it is reachable at that point in a run.
- The game's own descriptions of individual vehicles are left out of this copy.

Files in this folder: `vehicle-spawns.csv` (every special spawn, with its area and kind) and `vehicle-performance.csv` (all 251 vehicles).
