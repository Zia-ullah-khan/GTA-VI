"""Write output/SPEEDRUN_ROUTING_NOTES.md from mission_order.json, the scan logs and the self-check results."""

import argparse
import json
import sys
from pathlib import Path

from validate_final import check_json, check_mermaid

LANGUAGE_TABLE_OFFSETS = ["0x19be000", "0x2458000", "0x2f2c000", "0x3a0e000", "0x44b3000", "0x4f8f000", "0x5a1a000",
                          "0x644b000", "0x6f5a000", "0x7a24000", "0x84eb000", "0x9041000", "0x9b7e000"]
AUTOLAUNCH_MARKERS = ("AUTOLAUNCH", "AUTO-LAUNCH")

INTRO = """# Speedrun routing notes: main story, build 1.0.2.1 (Xbox dump)

Everything below comes from files in the dump or from the decompiled scripts in `americas_scripts_23_11_2026`.
Each claim is marked **observed** (read directly from data or code) or **inferred** (a conclusion drawn from
observed facts). Anything not recovered is listed under "Not recovered" and is `null` in the JSON.

## What was and was not recovered

- **Titles: recovered.** {titled} of {total} entries have their in-game English title.
- **Mission order: recovered as stored order.** The game ships its own ordered mission list ({story_count} entries).
  The flowchart follows it.
- **Prerequisite edges: not recovered.** No data field and no script check was found that gates one mission on
  another. `prerequisites`, `unlocks` and `is_bottleneck` are therefore `null`, and the arrows in the flowchart mean
  "next in the game's list", not "unlocks".
- **Protagonist per mission: recovered for {protagonist_count} main-story entries** from a required-player property
  on the mission trigger records.
- **Any% skips: {auto_count} main-story entries and {auto_side_count} side entries** are flagged by the game itself
  rather than by playing them.

## Correction to the previous version of these notes

The previous notes said that no localized text table exists in the dump and that display titles were unavailable.
That was wrong. The earlier extractor only inflated zlib streams that start exactly on a 0x1000 page boundary. The
text tables are stored with a 16-byte header in front of the stream (stream at page + 0x10), so they were skipped.
The titles quoted from another session for Chapter 1 (Prologue, Gone Fishing, Gear Up, Just a Scratch, Lab Fees and
so on) do match the dump's text table.
"""

PHASE1 = """## Phase 1: titles

**Observed**

- There is no `GXT2` container. All 24 `.rpf` / `.bin` files (161,307,960,768 bytes) were scanned at every byte
  offset for `GXT2` and `2TXG`, and every 16-byte-aligned zlib stream (2,247,302 streams) was inflated far enough to
  read its magic. Raw 4-byte hits: 66 (about 75 are expected by chance in that much data), none followed by a
  plausible header. Streams starting with the magic: 0. The `.ttpf` files (about 80 GB) were not scanned because the
  request named `.rpf` and `.bin`.
- The titles are in a different container: a resource whose inflated data carries the magic `0DRP` at offset 0x10.
  The English table is `data.rpf` @ 0x19be000 (zlib stream at 0x19be010, 3,866,624 bytes inflated, 36,888 entries).
  It is not encrypted. Layout: block table pointer at 0x38, block count at 0x4C; a hash table of 272-byte groups
  (16 control bytes, 16 entries of key hash + string index); string pools of NUL-terminated UTF-8.
- Keys are joaat hashes of the lowercased text key. The mission title key is the mission ID itself; the recap text
  key is `PROG_<ID>_DESC_REPLAY`; the objective text key is `<ID>_DESC`.
- Twelve more tables with the same layout sit in `data.rpf` at {languages}
  (one per language; only the first was parsed).
- The scripts folder holds 749 `.cs` files, a `.csproj` and three runtime files. Its sibling zip holds the same
  files. There is no `.ysc`, `.str` or string heap anywhere under `Downloads`, so the 55 `Vm.StringConstant` calls
  cannot be resolved. They are not needed for titles.

**Entries without a title** ({untitled_count}): {untitled}
"""

PHASE2 = """## Phase 2: main story versus side strands

**Observed**

- `<CMissions>` (`common.rpf` @ 0x219000) has 145 `<Item type="CMission">` rows. The only child tags are
  `UniqueMissionIndex`, `MissionId`, `Description` and `TextureName`, each with a single `value` attribute. There is
  no strand, category, protagonist or next-mission field.
- The story list in `story000.rpf` @ 0x3e30b5000 has a type field whose value is joaat("mission") and holds
  {story_count} IDs. A second list in the same file ({side_list_count} IDs) holds side content.

**Classification used**

The split into `main_story_missions` and `side_missions` follows the ID prefix rule from the request. It is not a
field in the game data. Result: {main} main-story entries, {side} side entries, {unclassified} entries whose ID name
could not be recovered (only a hash is stored), so the rule cannot be applied to them.

No side mission was promoted to the main-story chart, because none was proven to be a hard prerequisite.

**Main-story IDs left out of the chart** because nothing places them in an order: {unplaced}.
`INT_CRED` and `FIN_CONT` exist in `<CMissions>`; `FIN_CONT`'s recap text is "Return to the game pre-finale and
progress toward 100% completion, or start a new game." No edge from a finale to `INT_CRED` was found, so none is
drawn.
"""

PHASE3_HEAD = """## Phase 3: order, branches, protagonists, skips

### Flag store (`Virtual.type_37658EE3464E5234`)

**Observed.** All 31 call sites were read. `Method_0` adds an ID, `Method_1` tests for an ID. No `Method_1` result
gates enabling or launching another mission. The readers are: the "already added" test before `Method_0` in three
wrappers of `0x947D998BD81F7AC1`, the tests inside `func_10AA55`, and `func_10AD05`. `story000.ysc.cs` has no call
to this type. So this store yields no prerequisite edges.

### Auto-flags in `func_10AA55` (controller `0xD2601E252151E04B.ysc.cs`, lines 572807-573097)

**Observed.** The function receives a mission ID. For specific IDs it adds other IDs to the flag store.

**Inferred.** The function has no direct caller and sits next to the store's add hook, so it most likely runs when
the ID is added to the store (mission completion), not when the mission starts. The request described it as
"when the mission starts"; the code does not show that.

{auto_table}

**Inferred for routing.** Because the game sets these flags itself, the flagged missions do not have to be played
before the triggering mission. They are marked `any_percent_required: false`. Every other mission is `null`
(unknown), not `true`: nothing proves that the remaining missions are all mandatory.

When the ID is `BIL_FINAL_B` (line 572926) or `BIL_FINALE_M` (line 572935) the function calls
`_0x58BECE7D02A750A7(0x4EF9B888, -1, 1, -1)` instead.
"""

ORDER_TEXT = """### Stored mission order

**Observed.** `story000.rpf` @ 0x3e30b5000, list key 0xB95219D4, holds {story_count} IDs in a fixed order.
{main_sequence_count} of them are main-story entries by the prefix rule. The replay menu (`data.rpf` @ 0x12010000)
holds a second order. The two disagree for 18 adjacent pairs, so neither can be read as a strict unlock chain.
Twelve entries of the list are IDs that are not in `<CMissions>`; five of those were named by an exact joaat match
of an ID-shaped candidate (`MTL_CHECK`, `CLB_SETUP`, `COA_RAID`, `BIL_FINAL`, `COM_KMODSHP`), seven remain hashes.

Name recovery: 3,432,943 candidates were hashed against 29 targets, which gives about 0.02 expected false matches
in total. 14 targets matched.

{sequence_table}
"""

PROTAGONIST_TEXT = """### Protagonist locks

**Observed**

- Mission trigger records in `story000.rpf` @ 0x3e2372000 and `levels.rpf` @ 0x11bb116000 carry property
  0xDB880157 with one of two values.
- Controller lines 635272-635323 read that property. Value 0x4E21D02A is tested against the current player being
  `player_lucia` (0xD058819F), value 0x56D7FE7A against `player_jason` (0x072B3FF4). A mismatch sets an output flag.
- `ROB_BOAT_L_LUCIA` carries the Lucia value and `ROB_BOAT_J_JASON` the Jason value.
- Cross-check: for all 51 entries that have both this property and a recap text, the recap names the same
  character. No entry contradicts it.

**Inferred.** The property is the character the player must be controlling to start the mission. Entries without
the property are `protagonist: null`; that means "not stated in the data", not "either character".

Main-story entries by required player: Jason {jason_count}, Lucia {lucia_count}, differs by variant
{both_count}, not stated {none_count}.
"""

HOURS_TEXT = """### Time-of-day gates

**Observed.** Some trigger records carry two integer properties, 0x1FD5BB99 and 0xB376AD2B.
`0x947D998BD81F7AC1.ysc.cs` lines 89983-89999 read both into adjacent fields. `story000.ysc.cs` lines 116302-116328
enable `BIL_PICK_DAY_TIME_START` when a value is `< 17` and `BIL_PICK_NIGHT_TIME_START` otherwise.

**Inferred.** 0x1FD5BB99 is the opening hour and 0xB376AD2B the closing hour. The DAY and NIGHT records of
`BIL_PICK` hold mirrored values, which fits. The two data files disagree on some values; which file wins at runtime
was not established.

{hours_table}
"""

OTHER_FILES = """### Other files examined for flow data

- `story000.rpf` @ 0x35ff74000: a manifest of 609 `.pso.meta` file names (map states, mission areas, `flow`,
  `player_schedules_chapter2..5`). It lists names only. The files themselves could not be located by name because
  the archive's table of contents is encrypted.
- `story000.rpf` @ 0x11b4a0000 (5.5 MB): a hash map of about 67,000 entries, each a key plus two hashes, one of
  which is a mission ID for 93 missions. The schema has no ordering or condition field. Purpose not established.
- `story000.rpf` @ 0x3e2372000 and `levels.rpf` @ 0x11bb116000: trigger records (position, contact character,
  required player, hours, tags). No field references another mission as a condition.
- `audio.rpf` @ 0xb92ae0 (71 mission ID hashes): not decoded.
"""

NOT_RECOVERED = """## Not recovered

- Any prerequisite edge (`A` must be done before `B` becomes available). The enabling logic for most missions was
  not located. Of 250 calls to the record toggle `_0x480014E54CD33903`, only 9 use a `<CMissions>` ID.
- Which missions are strictly mandatory (`is_bottleneck`, `any_percent_required: true`).
- The condition that selects `BIL_MOTEL_VIOLENT` versus `BIL_MOTEL_NON_VIOLENT`, and the meaning of the unnamed
  argument that selects the `ROB_BOAT` variant.
- Names for seven IDs in the story list and most IDs in the side-content list (their titles are known where the
  text table has one).
- Whether `story000.rpf` or `levels.rpf` trigger data takes precedence where they differ.
- Any edge from a finale to `INT_CRED`.
"""


def table(header: list[str], rows: list[list]) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    lines += ["| " + " | ".join("" if cell is None else str(cell).replace("|", "/") for cell in row) + " |"
              for row in rows]
    return "\n".join(lines)


def position_text(entry: dict) -> str | None:
    for record in entry["triggers"]:
        if record["position"]:
            return ", ".join(f"{value:.0f}" for value in record["position"])

    return None


def auto_table(entries: list[dict]) -> str:
    rows = []
    for entry in entries:
        for flag in entry["auto_flagged_when"]:
            lines = ", ".join(text.split(" ")[0].split(":")[1] for text in flag["evidence"])
            unless = " or ".join(flag["unless_already_flagged"]) if flag["unless_already_flagged"] else ""
            rows.append([" / ".join(flag["flag_added_for"]), entry["id"], entry["display_name"],
                         "main" if entry["is_main_story"] else "side", unless, lines])

    rows.sort(key=lambda row: row[0], reverse=True)
    return table(["When this ID is handled", "Flag added for", "Title", "Class", "Skipped if already flagged",
                  "Controller lines"], rows)


def sequence_table(document: dict, by_id: dict[str, dict]) -> str:
    rows = []
    for mission_id in document["story_list_order"]:
        entry = by_id[mission_id]
        kind = {True: "main", False: "side", None: "unnamed"}[entry["is_main_story"]]
        rows.append([entry["story_list_position"], entry["chapter"], entry["display_name"], f"`{entry['id']}`",
                     kind, entry["protagonist"], position_text(entry)])

    return table(["#", "Ch", "Title", "ID", "Class", "Required player", "Trigger position (x, y, z)"], rows)


def variants_table(entries: list[dict], by_id: dict[str, dict]) -> str:
    rows = []
    for entry in entries:
        if not entry["variants"] or not entry["is_main_story"]:
            continue

        for variant_id in entry["variants"]:
            variant = by_id[variant_id]
            basis = "variant map" if "variant map" in variant["variant_basis"] else "ID name only"
            contact = next((r["contact_name"] or r["contact_hash"] for r in variant["triggers"]
                            if r["contact_hash"]), None)
            rows.append([f"`{entry['id']}`", f"`{variant_id}`", basis, variant["protagonist"], contact])

    return table(["Entry", "Variant", "Basis", "Required player", "Contact on trigger record"], rows)


def hours_table(entries: list[dict]) -> str:
    rows = []
    for entry in entries:
        for hours in entry["available_hours"]:
            source = "story000.rpf" if "story000" in hours["source"] else "levels.rpf"
            rows.append([f"`{entry['id']}`", entry["display_name"], hours["hour_property_0x1FD5BB99"],
                         hours["hour_property_0xB376AD2B"], source])

    return table(["ID", "Title", "0x1FD5BB99 (opens)", "0xB376AD2B (closes)", "Data file"], rows)


def autolaunch_table(entries: list[dict]) -> str:
    rows = []
    for entry in entries:
        if not any(marker in entry["id"] for marker in AUTOLAUNCH_MARKERS):
            continue

        basis = "variant map" if entry["variant_basis"] and "variant map" in entry["variant_basis"] else "ID name"
        facts = "; ".join(sorted({link["kind"] for link in entry["script_links"]})) or "none"
        rows.append([f"`{entry['id']}`", f"`{entry['variant_of']}`", basis,
                     "yes" if entry["triggers"] else "no", "yes" if entry["in_cmissions_table"] else "no", facts])

    return table(["Auto-launch ID", "Variant of", "Basis", "Has trigger record", "In CMissions", "Script facts"], rows)


def script_links_text(document: dict) -> str:
    lines = []
    for link in document["script_links"]:
        first, last = link["line_range"]
        cites = "; ".join(link["evidence"])
        lines.append(f"- **{link['kind']}** (`{link['file']}` lines {first}-{last}). {link['statement']}\n"
                     f"  Evidence: {cites}")

    return "\n".join(lines)


def build(document: dict, chart: dict, data: dict, problems: list[str]) -> str:
    main = document["main_story_missions"]
    everything = main + document["side_missions"] + document["unclassified_entries"]
    by_id = {entry["id"]: entry for entry in everything}
    untitled = [f"`{entry['id']}`" for entry in everything if not entry["display_name"]]
    auto = [entry for entry in everything if entry["auto_flagged_when"]]
    protagonists = [entry["protagonist"] for entry in main]
    sections = [
        INTRO.format(titled=document["status"]["titles_recovered"], total=len(everything),
                     story_count=len(document["story_list_order"]),
                     protagonist_count=sum(1 for value in protagonists if value),
                     auto_count=sum(1 for entry in auto if entry["is_main_story"]),
                     auto_side_count=sum(1 for entry in auto if not entry["is_main_story"])),
        PHASE1.format(languages=", ".join(LANGUAGE_TABLE_OFFSETS[1:]), untitled_count=len(untitled),
                      untitled=", ".join(untitled)),
        PHASE2.format(story_count=len(document["story_list_order"]),
                      side_list_count=len(document["side_content_list"]), main=len(main),
                      side=len(document["side_missions"]), unclassified=len(document["unclassified_entries"]),
                      unplaced=", ".join(f"`{i}`" for i in document["main_story_without_placement"])),
        PHASE3_HEAD.format(auto_table=auto_table(auto)),
        ORDER_TEXT.format(story_count=len(document["story_list_order"]),
                          main_sequence_count=len(document["main_story_sequence"]),
                          sequence_table=sequence_table(document, by_id)),
        "### Branches, variants and dual endings\n\n**Observed.** The variant map in `story000.rpf` @ 0x3e30b5000 "
        "groups alternative IDs under one entry. Rows marked \"ID name only\" are grouped because the ID starts "
        "with the entry's ID; that is a naming relation, not a data link.\n\n"
        "The ending splits twice in the data: `BIL_PENT` has Brian and Mendez variants, and `BIL_FINAL` has "
        "`BIL_FINAL_B` and `BIL_FINAL_M`. `<CMissions>` spells the Mendez finale `BIL_FINALE_M`; its trigger "
        "record names the contact `mendez`, and `BIL_FINAL_B`'s names `brian`. `func_10AD05` treats the story as "
        "finished when either `BIL_FINALE_M` or `BIL_FINAL_B` is flagged.\n\n"
        + variants_table(main, by_id) + "\n",
        PROTAGONIST_TEXT.format(jason_count=protagonists.count("Jason"), lucia_count=protagonists.count("Lucia"),
                                both_count=sum(1 for v in protagonists if v and v not in ("Jason", "Lucia")),
                                none_count=protagonists.count(None)),
        HOURS_TEXT.format(hours_table=hours_table(everything)),
        "### Auto-launch IDs\n\n**Observed.** These IDs exist. What launches them was not decoded, except that "
        "`MNY_HOTEL_AUTOLAUNCH` shares the `MNY_HOTEL` branch in `func_10AA55` (line 572955) and "
        "`ANT_CHASE_AUTOLAUNCH` suppresses the `ANT_CHASE` auto-flag (line 573017).\n\n"
        + autolaunch_table(everything) + "\n",
        "### Verified script facts\n\nEach fact was re-checked by a script that requires every cited hash to be "
        "present inside the cited line range.\n\n" + script_links_text(document) + "\n\n"
        "The first fact shows a script enabling the `MTL_MUD` record while also referencing a different mission "
        "(`HO_PAR_FRINT`). It does not prove that `HO_PAR_FRINT` is required for `MTL_MUD`: the script was not "
        "identified as the `HO_PAR_FRINT` mission script, and other enabling paths were not ruled out. For that "
        "reason it is recorded here and in `script_links`, not drawn as a prerequisite.\n",
        OTHER_FILES,
        NOT_RECOVERED,
        "## Self-check\n\n"
        f"- `mission_flow.mmd`: {chart['nodes']} nodes ({chart['rectangles']} rectangles, {chart['stadiums']} "
        f"stadiums), {chart['arrows']} arrows, {chart['orphans']} orphan nodes, no cycle among arrows. The file "
        "was also rendered to SVG with `@mermaid-js/mermaid-cli` without a parse error.\n"
        f"- `mission_order.json`: {data['main']} main-story entries, {data['side']} side entries, "
        f"{data['unclassified']} unclassified; order and variant edges ({data['edges']}) form a DAG. "
        "`auto_flag_links` are annotations, not dependency edges: they point from a later mission back to "
        "earlier ones and would form cycles if read as dependencies.\n"
        f"- Problems reported by `work/validate_final.py`: {len(problems)}.\n"
        "- The original dump files were only read. All tools and intermediates are under `work/`.\n",
    ]
    return "\n".join(sections)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out_dir", type=Path)
    args = parser.parse_args()

    order_path = args.out_dir / "mission_order.json"
    document = json.loads(order_path.read_text(encoding="utf-8"))
    chart_problems, chart = check_mermaid(args.out_dir / "mission_flow.mmd")
    json_problems, data = check_json(order_path)
    text = build(document, chart, data, chart_problems + json_problems)
    target = args.out_dir / "SPEEDRUN_ROUTING_NOTES.md"
    target.write_text(text, encoding="utf-8")
    print(f"{target.name}: lines={text.count(chr(10))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
