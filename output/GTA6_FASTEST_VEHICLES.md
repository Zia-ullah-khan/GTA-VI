# GTA VI — fastest vehicles and where a fixed one spawns

Built for route planning. Every figure is read out of the shipped data; locations come from the game's own vehicle catalog, and descriptions are quoted verbatim.

## Where this comes from

| What | Source | Nature |
|---|---|---|
| Performance | `common.rpf` payload `0x612000`, `CVehiclePerformanceMaps` | plain XML, 251 vehicles |
| Cross-check | `common.rpf` payload `0x616000`, `CVehicleBaseRatingsAndEstimatesMap` | plain XML, independent estimates |
| Spawn location | `GRID_SML_L_VEH_<model>_<KIND>_<AREA>_<label>` catalog tokens | 267 special spawns, authoritative for area |
| Flavour text | the game's text table | quoted, bound only when unambiguous |

The two performance files are independent and agree on ordering, which is the main reason to trust them.

**A model can have several special spawns.** The catalog marks them `UNIQUE` (collectible), `CHAR` (a named character's car), `EXCON`, `CMP`, `AMB`, `MIS`. The Emerus alone has five. Because each has its own description, a description is only attached below when a model has **exactly one** special spawn — 29 of 267. The other 201 are left blank rather than guessed at. The area, which comes from the token itself, is reliable in every case.

251 vehicles have performance entries; 203 are road-capable (aircraft and boats have no braking distance or turn radius in the data). 83 special spawns resolve to a named area across 30 areas.

## The pick-up list — fastest road vehicles with a fixed spawn you can place

Area comes from the catalog token, so it is reliable. Where the model has only one special spawn the game's own description is quoted too.

| # | Model | km/h | 0–60 | Area | Catalog label | Description |
|---|---|---|---|---|---|---|
| 1 | `emerus` | 260 | 2.92 | **Kelly County** | Racecar | — |
| 2 | `tempesta` | 256 | 2.78 | **Oceanbeach** | Police | — |
| 3 | `tempesta` | 256 | 2.78 | **Tequesta** | Iridescentgreen | — |
| 4 | `comet7` | 246 | 3.12 | **Salton** | Motel | — |
| 5 | `italirsx` | 244 | 2.60 | **Crosstown** | Statusauto | — |
| 6 | `coquette4` | 230 | 3.68 | **Capri** | Police | — |
| 7 | `coquette4` | 230 | 3.68 | **Stockyard** | Vicevinyl | — |
| 8 | `vigero3` | 220 | 4.58 | **Keylento** | Custom | — |
| 9 | `cypher` | 216 | 4.07 | **Bayside** | Artistcar | — |
| 10 | `cypher` | 216 | 4.07 | **Crosstown** | Statusauto | — |
| 11 | `paragon` | 212 | 3.97 | **Waningsands** | Blackandgold | Ascot Paragon with a striking rose gold finish. Discovered outside a huge property in Waning Sands. |
| 12 | `cometretro` | 208 | 4.55 | **Capri** | Musician | — |
| 13 | `banshee` | 207 | 5.35 | **Hamlet** | Liftedracecar | Unusual Bravado Banshee, lifted and reinforced for dirt track racing by an Emma Gary. Discovered in a junkyard in Hamlet. |
| 14 | `toros` | 206 | 4.05 | **Leaflinks** | Goldenwheels | — |
| 15 | `double` | 204 | 3.77 | **Laperle** | Sound4Sound | — |
| 16 | `coquette2` | 201 | 6.05 | **Crosstown** | Rustyclassic | — |
| 17 | `dominator7` | 199 | 5.35 | **Ambrosia** | Americanaracecar | — |
| 18 | `dominator7` | 199 | 5.35 | **Kelly County** | Racecar | — |
| 19 | `dominator7` | 199 | 5.35 | **Rockridge** | Blackwindows | — |
| 20 | `fcr` | 197 | 4.53 | **Airport** | Goldenwheels | — |
| 21 | `stallion` | 193 | 5.58 | **Waningsands** | Restomod | — |
| 22 | `baller8` | 192 | 5.47 | **Washingtonbeach** | Black | — |
| 23 | `gauntlet5` | 192 | 7.03 | **Ambrosia** | Bigblock | — |
| 24 | `gauntlet5` | 192 | 7.03 | **Grayson** | Rustedout | — |
| 25 | `penumbra` | 191 | 6.68 | **Capri** | Pink | Maibatsu Penumbra with hot pink accents and underglow. Found in a hotel parking lot in Capri. |
| 26 | `esskey` | 190 | 5.77 | **Southside** | Thicktires | Unusually rugged Principe Esskey, specially modded for off-roading with extra-thick tires. Found at a Southside convenience store. |
| 27 | `elegy` | 189 | 5.27 | **Kelly County** | Driftcar | — |
| 28 | `baller2` | 188 | 5.53 | **Belville** | Goldenwheels | — |
| 29 | `jubilee` | 186 | 5.70 | **Leaflinks** | Bronze | — |
| 30 | `penumbraff` | 186 | 6.83 | **Ambrosia** | Racecar | — |

## Fast cars that are placed only by description

These have no area in the catalog token, so the location below is whatever the game's text says. Only unambiguous bindings are shown.

| Model | km/h | 0–60 | Kind | Description |
|---|---|---|---|---|
| `thrax` | 276 | 2.43 | CHAR | Custom Truffade Thrax belonging to Andrew Node, found at his luxury residence on Starfish Island. |
| `zorrusso` | 240 | 3.52 | EXCON | One-of-a-kind Granforma Zorrusso modified to racing specifications, found at a luxury residence in Peacock Estates. |
| `schutzen` | 222 | 3.97 | MIS | Benefactor Schutzen owned by Vice City rapper DWNPLY. Found outside a Pay 'n' Spray in Stockyard. |
| `jugular` | 220 | 3.68 | EXCON | Race-ready Ocelot Jugular found at a wealthy residence in Belville. |
| `lectro` | 205 | 4.70 | AMB | Bespoke Principe Lectro with a custom livery and racing mods, discovered at Emilio's Auto Center in Rockridge. |
| `dominator` | 197 | 5.73 | CMP | Vapid Dominator ASP optimized for racing with a patriotic paint job. Discovered at Ambrosia Raceway Park. |
| `hermes` | 192 | 5.78 | EXCON | '50 Albany Hermes with custom flame decals. Discovered in a shipping container on Draper Island. |
| `astron` | 191 | 4.50 | AMB | Pfister Astron with hot pink accents. Discovered in a garage at a house in Belville. |
| `vamos` | 169 | 8.58 | EXCON | Rusted '74 Declasse Vamos once owned by outlaws Martha and Lyle. Found in an abandoned shed in Bonanza. |
| `futo` | 166 | 8.98 | UNIQUE | Heavily modded '85 Karin Futo with thick tires and extra lights. Found in a shipping container in Port Gellhorn. |
| `dorado` | 154 | 11.22 | UNIQUE | Custom Bravado Dorado with a unique roof livery, discovered at a car wash in Ambrosia. |
| `yosemite` | 152 | 9.97 | EXCON | '67 Declasse Yosemite with off-roading modifications. Found outside a residence in Watson Bay. |

`thrax`, the fastest non-aircraft in the game, is here rather than above: its catalog token is `THRAX_CHAR_ANDREWNODE`, a named character's car with no area field. It is the only special Thrax in the catalog, so the description binding is safe.

## Fastest overall, spawn or not

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

`lazer` at 417 km/h is the jet; `valkyrie` and `buzzard` are helicopters.

## Best acceleration among road cars

Top speed rarely matters on a short city leg.

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

## Best car waiting in each area

| Area | Best road vehicle | km/h | others there |
|---|---|---|---|
| **Airport** | `fcr` | 197 | — |
| **Ambrosia** | `dominator7` | 199 | `gauntlet5`, `penumbraff`, `picador`, `caracara4x4`, `zombieb` |
| **Bayside** | `cypher` | 216 | `dominatorclassic` |
| **Belville** | `baller2` | 188 | `zion2` |
| **Capri** | `coquette4` | 230 | `cometretro`, `penumbra`, `bobcatxl`, `caracara4x4`, `sungrazer` |
| **Crosstown** | `italirsx` | 244 | `cypher`, `coquette2` |
| **Downtown** | `cavalcade3` | 178 | — |
| **Frogswater** | `picador` | 186 | — |
| **Gellhorn** | `cliffhanger` | 167 | `bandito` |
| **Grassrivers** | `sovereign107` | 185 | `bison900`, `enduro`, `sanchez`, `sanchez`, `boxville` |
| **Grayson** | `gauntlet5` | 192 | — |
| **Hamlet** | `banshee` | 207 | `bandito` |
| **Kelly County** | `emerus` | 260 | `dominator7`, `elegy`, `sovereign107`, `manchez` |
| **Keylento** | `vigero3` | 220 | `ruiner`, `akane`, `woodland`, `hustler`, `yougaxl` |
| **Laperle** | `double` | 204 | — |
| **Leaflinks** | `toros` | 206 | `jubilee` |
| **Leonard County** | `sanchez` | 147 | `declasse500` |
| **Lummox County** | `zombieb` | 161 | — |
| **Millport** | `yougaxl` | 126 | — |
| **Oceanbeach** | `tempesta` | 256 | — |
| **Peacockbay** | `cavalcade3` | 178 | — |
| **Portgellhorn** | `blista2` | 172 | `yosemite1500`, `caracara4x4`, `marshall` |
| **Rockridge** | `dominator7` | 199 | — |
| **Salton** | `comet7` | 246 | — |
| **Southside** | `esskey` | 190 | — |
| **Stockyard** | `coquette4` | 230 | — |
| **Tequesta** | `tempesta` | 256 | `schafters` |
| **Waningsands** | `paragon` | 212 | `stallion` |
| **Washingtonbeach** | `baller8` | 192 | `zombieb` |
| **Watsonbay** | `phoenix` | 166 | `youga2`, `blazer4`, `journey`, `journey` |

## Caveats

- `topSpeed` is unlabelled in the file. It behaves like metres per second, so km/h is `× 3.6`. The ordering does not depend on this.
- An area is a named region, not a parking space. Exact coordinates would need the `VEHICLEGEN_OVERVIEW_FILE` named in the content manifest, which is not decoded here.
- Story availability is not modelled. A vehicle existing at a spot does not mean it is reachable at that point in a run.
- 201 of 267 spawns have no description shown because the model has more than one special spawn and the text cannot be bound to a specific one. The area is still reliable.

Full tables: `gta6_vehicle_spawns.csv` (every special spawn) and `gta6_vehicle_performance.csv` (all 251 vehicles).
