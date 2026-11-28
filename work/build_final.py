"""Build output/mission_order.json from recovered game data and verified script facts.

Nothing is inferred beyond what each field's *_basis text states; unknown values stay null.
"""

import argparse
import json
import sys
from pathlib import Path

from build_outputs import CMISSIONS_SOURCE, PROGRESS_SOURCE, build_listed_missions
from decomp_common import joaat
from flow_sources import (LISTS_SOURCE, SIDE_LIST_KEY, STORY_LIST_KEY, TRIGGER_SOURCES, IdResolver,
                          flatten_text_keys, load_json, load_named_list, load_titles, load_triggers,
                          load_variant_map)
from flowchart import build_mermaid

MAIN_PREFIXES = ("INT", "MTL", "BIL", "CLB", "ROB", "BAN", "MNY", "AIR", "COA", "ANT", "FIN")
SIDE_PREFIXES = ("COM", "FT", "CSC", "CTI", "HO", "UP", "AO")
TEXT_SOURCE = "data.rpf @ 0x19be000 (0DRP text table, English)"
PREFIX_RULE = "ID prefix rule supplied in the request (not a field in the game data)"


def classify(mission_id: str) -> tuple[bool | None, str]:
    if mission_id.startswith("0x"):
        return None, "ID name not recovered, so the prefix rule cannot be applied"

    prefix = mission_id.split("_")[0].upper()
    if prefix in MAIN_PREFIXES:
        return True, f"{PREFIX_RULE}: prefix {prefix} is in the main-story set"

    if prefix in SIDE_PREFIXES:
        return False, f"{PREFIX_RULE}: prefix {prefix} is in the side-strand set"

    return False, f"prefix {prefix} is not covered by the rule; kept with side entries"


def id_hash(mission_id: str) -> str:
    if mission_id.startswith("0x"):
        return mission_id.upper().replace("0X", "0x")

    return f"0x{joaat(mission_id.lower()):08X}"


class Catalog:
    """All known mission entries keyed by ID, created on first sight in priority order."""

    def __init__(self, table: dict[str, dict], text: dict[str, str], titles: dict[str, str]):
        self._table = table
        self._text = text
        self._titles = titles
        self.entries = {}

    def Ensure(self, mission_id: str, name_basis: str) -> dict:
        row = self._table.get(mission_id.upper())
        if row is not None:
            mission_id = row["id"]

        if mission_id in self.entries:
            return self.entries[mission_id]

        hash_text = id_hash(mission_id)
        is_main, basis = classify(mission_id)
        key = mission_id.upper()
        evidence = [f"{CMISSIONS_SOURCE} Item[UniqueMissionIndex={row['index']}]"] if row else []
        display = self._text.get(key) or self._titles.get(hash_text[2:].lower())
        if display:
            evidence.append(f"{TEXT_SOURCE} key hash {hash_text}")

        entry = {
            "id": mission_id, "id_hash": hash_text,
            "id_name_basis": "CMissions table" if row else name_basis,
            "display_name": display,
            "replay_menu_title": None,
            "recap_description": self._text.get(f"PROG_{key}_DESC_REPLAY"),
            "objective_description": self._text.get(f"{key}_DESC"),
            "is_main_story": is_main, "classification_basis": basis,
            "chapter": None, "chapter_basis": None,
            "story_list_position": None, "replay_menu_position": None,
            "in_cmissions_table": row is not None,
            "unique_mission_index": row["index"] if row else None,
            "variant_of": None, "variant_basis": None, "variants": [],
            "protagonist": None, "protagonist_basis": None,
            "triggers": [], "trigger_type": None, "available_hours": [],
            "prerequisites": None, "unlocks": None,
            "prerequisites_status": "not recovered: no prerequisite data or gating script check was found",
            "story_list_previous_main": None, "story_list_next_main": None,
            "is_bottleneck": None,
            "any_percent_required": None, "any_percent_basis": None,
            "auto_flagged_when": [], "script_links": [], "scripts_referencing_id": [],
            "in_flowchart": False, "evidence": evidence,
        }
        self.entries[mission_id] = entry
        return entry


def add_story_list(catalog: Catalog, items: list[str], resolver: IdResolver) -> list[str]:
    order = []
    for position, item in enumerate(items):
        basis = ("exact joaat match of an ID-shaped candidate" if resolver.IsRecovered(item)
                 else "unnamed: only the hash is stored in the game data")
        entry = catalog.Ensure(resolver.Name(item), basis)
        entry["story_list_position"] = position
        entry["evidence"].append(f"{LISTS_SOURCE} list 0x{STORY_LIST_KEY.upper()} item[{position}]")
        order.append(entry["id"])

    return order


def add_menu(catalog: Catalog, menu: list[dict], text: dict[str, str]) -> None:
    for mission in menu:
        entry = catalog.Ensure(mission["id"], "replay menu item id")
        chapter = int(mission["chapter_or_act"].split()[-1])
        entry["chapter"] = chapter
        entry["chapter_basis"] = "replay menu chapter filter"
        entry["replay_menu_position"] = mission["replay_menu_position"]
        label = mission["display_name_text_key"].upper()
        title = text.get(label)
        if title and title != entry["display_name"]:
            entry["replay_menu_title"] = title

        if entry["display_name"] is None:
            entry["display_name"] = title

        entry["evidence"].append(mission["evidence"][0])


def add_side_list(catalog: Catalog, items: list[str], resolver: IdResolver) -> None:
    for position, item in enumerate(items):
        entry = catalog.Ensure(resolver.Name(item), "unnamed: only the hash is stored in the game data")
        entry["evidence"].append(f"{LISTS_SOURCE} list 0x{SIDE_LIST_KEY.upper()} item[{position}]")


def link_variant(catalog: Catalog, base: dict, variant_id: str, basis: str, name_basis: str) -> None:
    variant = catalog.Ensure(variant_id, name_basis)
    if variant["id"] == base["id"] or variant["variant_of"] is not None:
        return

    variant["variant_of"] = base["id"]
    variant["variant_basis"] = basis
    variant["is_main_story"] = base["is_main_story"]
    variant["classification_basis"] = f"variant of {base['id']}"
    variant["evidence"].append(f"variant of {base['id']}: {basis}")
    base["variants"].append(variant["id"])


def add_variants(catalog: Catalog, variant_map: list[dict], resolver: IdResolver, table: dict[str, dict]) -> None:
    for index, row in enumerate(variant_map):
        base = catalog.Ensure(resolver.Name(row["base"]), "exact joaat match of an ID-shaped candidate")
        for item in row["variants"]:
            basis = "exact joaat match of an ID-shaped candidate" if resolver.IsRecovered(item) else "unnamed hash"
            link_variant(catalog, base, resolver.Name(item), f"{LISTS_SOURCE} variant map row[{index}]", basis)

    placed = [e for e in catalog.entries.values()
              if e["story_list_position"] is not None or e["replay_menu_position"] is not None]
    for base in sorted(placed, key=lambda e: -len(e["id"])):
        prefix = base["id"].upper() + "_"
        for key, row in table.items():
            candidate = catalog.Ensure(row["id"], "CMissions table")
            is_placed = candidate["story_list_position"] is not None or candidate["replay_menu_position"] is not None
            if key.startswith(prefix) and not is_placed:
                link_variant(catalog, base, row["id"], "ID name begins with the base ID (name relation only)",
                             "CMissions table")


def fill_chapters(catalog: Catalog, order: list[str], table: dict[str, dict]) -> None:
    known = [(position, catalog.entries[i]["chapter"]) for position, i in enumerate(order)
             if catalog.entries[i]["chapter"] is not None]
    for position, mission_id in enumerate(order):
        entry = catalog.entries[mission_id]
        if entry["chapter"] is not None:
            continue

        before = [chapter for p, chapter in known if p < position]
        after = [chapter for p, chapter in known if p > position]
        if before and after and before[-1] == after[0]:
            entry["chapter"] = before[-1]
            entry["chapter_basis"] = "story-list neighbours on both sides are replay-menu entries of this chapter"
        elif before and not after:
            entry["chapter"] = before[-1]
            entry["chapter_basis"] = "last story-list entry; every preceding replay-menu entry nearby is this chapter"

    for entry in catalog.entries.values():
        if entry["chapter"] is None and entry["variant_of"]:
            base = catalog.entries[entry["variant_of"]]
            entry["chapter"] = base["chapter"]
            entry["chapter_basis"] = f"variant of {base['id']}" if base["chapter"] else None

    for entry in catalog.entries.values():
        row = table.get(entry["id"].upper())
        tag = row.get("grid_chapter") if row else None
        if entry["chapter"] is None and tag and tag.startswith("CH"):
            entry["chapter"] = int(tag[2:])
            entry["chapter_basis"] = f"CMissions texture name tag {tag} (naming convention, weakest basis)"


def add_triggers(catalog: Catalog, triggers: dict[str, list[dict]]) -> None:
    for mission_id, records in triggers.items():
        entry = catalog.Ensure(mission_id, "trigger record id")
        entry["triggers"] = records
        entry["trigger_type"] = "map_trigger_record"
        for record in records:
            entry["evidence"].append(f"{record['source']} record id {entry['id_hash']}")
            if record["hour_start"] is not None or record["hour_end"] is not None:
                entry["available_hours"].append({"hour_property_0x1FD5BB99": record["hour_start"],
                                                 "hour_property_0xB376AD2B": record["hour_end"],
                                                 "source": record["source"]})


def fill_protagonists(catalog: Catalog) -> None:
    for entry in catalog.entries.values():
        family = [entry] + [catalog.entries[v] for v in entry["variants"]]
        if entry["trigger_type"] is None and any(member["triggers"] for member in family):
            entry["trigger_type"] = "map_trigger_record_on_variants"

        required = {record["required_player"] for member in family for record in member["triggers"]
                    if record["required_player"]}
        if len(required) == 1:
            entry["protagonist"] = required.pop()
            entry["protagonist_basis"] = "required-player property 0xDB880157 on the trigger record(s)"
        elif len(required) == 2:
            entry["protagonist"] = "Jason or Lucia (differs by variant or data file)"
            entry["protagonist_basis"] = "required-player property 0xDB880157 differs between trigger records"


def add_auto_flags(catalog: Catalog, facts: list[dict]) -> list[dict]:
    links = []
    for fact in facts:
        if fact["kind"] != "handler_sets_flag":
            continue

        target = catalog.Ensure(fact["target"], "CMissions table")
        sources = [fact["when_argument_equals"]] + fact["also_when_argument_equals"]
        target["auto_flagged_when"].append({"flag_added_for": sources,
                                            "unless_already_flagged": fact["only_if_neither_flag_set"],
                                            "evidence": fact["evidence"]})
        target["any_percent_required"] = False
        target["any_percent_basis"] = (f"func_10AA55 sets this mission's flag itself when {' / '.join(sources)} is "
                                       "added to the flag store, so the game does not need it played by then "
                                       "(inference from the handler; the handler is the observed part)")
        links.append({"kind": "auto_flag", "from": sources[0], "to": target["id"], "also_from": sources[1:],
                      "evidence": fact["evidence"]})

    return links


def add_script_links(catalog: Catalog, script_links: list[dict], references: dict[str, list[str]]) -> None:
    for link in script_links:
        for mission_id in link["ids"] + link["related_ids"]:
            catalog.Ensure(mission_id, "CMissions table")["script_links"].append(
                {"kind": link["kind"], "statement": link["statement"], "evidence": link["evidence"]})

    for mission_id, scripts in references.items():
        if mission_id in catalog.entries:
            catalog.entries[mission_id]["scripts_referencing_id"] = scripts


def link_sequence(catalog: Catalog, order: list[str]) -> list[str]:
    main_order = [i for i in order if catalog.entries[i]["is_main_story"]]
    for previous, following in zip(main_order, main_order[1:]):
        catalog.entries[previous]["story_list_next_main"] = following
        catalog.entries[following]["story_list_previous_main"] = previous

    return main_order


def mark_flowchart(catalog: Catalog, main_order: list[str], auto_links: list[dict], finish_pair: list[str]) -> None:
    shown = set(main_order)
    for entry in catalog.entries.values():
        if entry["is_main_story"] and entry["variant_of"] in shown:
            shown.add(entry["id"])

    for link in auto_links:
        if catalog.entries[link["to"]]["is_main_story"] and link["from"] in shown:
            shown.add(link["to"])

    if any(mission_id in shown for mission_id in finish_pair):
        shown.update(finish_pair)

    for mission_id in shown:
        catalog.entries[mission_id]["in_flowchart"] = True


def build_document(catalog: Catalog, order: list[str], main_order: list[str], auto_links: list[dict],
                   script_links: list[dict], side_list: list[str], version: str) -> dict:
    entries = list(catalog.entries.values())
    rank = {mission_id: position for position, mission_id in enumerate(order)}
    entries.sort(key=lambda e: (rank.get(e["variant_of"] or e["id"], len(rank)), e["variant_of"] is not None))
    main = [e for e in entries if e["is_main_story"] is True]
    return {
        "game_version": version,
        "generated_from": {"mission_table": CMISSIONS_SOURCE, "replay_menu": PROGRESS_SOURCE,
                           "titles": TEXT_SOURCE, "story_list_and_variant_map": LISTS_SOURCE,
                           "trigger_records": TRIGGER_SOURCES},
        "status": {
            "titles_recovered": sum(1 for e in entries if e["display_name"]),
            "prerequisite_edges_recovered": 0,
            "note": "story_list_order is the order stored in the game's own mission list. It is an order, not a "
                    "proven prerequisite chain. prerequisites/unlocks/is_bottleneck stay null because no data "
                    "field or script check that gates one mission on another was found.",
        },
        "story_list_order": order,
        "main_story_sequence": main_order,
        "main_story_missions": main,
        "side_missions": [e for e in entries if e["is_main_story"] is False],
        "unclassified_entries": [e for e in entries if e["is_main_story"] is None],
        "side_content_list": side_list,
        "auto_flag_links": auto_links,
        "script_links": script_links,
        "main_story_without_placement": [e["id"] for e in main if not e["in_flowchart"]],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    work = args.work
    flow = work / "flow"
    table = {entry["id"].upper(): entry for entry in load_json(work / "cmissions.json")}
    text = flatten_text_keys(load_json(work / "text" / "mission_text.json"))
    titles = load_titles(work / "text" / "table_0019be000.json")
    resolver = IdResolver(load_json(flow / "id_names.json"), titles)
    lists = load_json(flow / "tree_3e30b5000.json")
    evidence = load_json(work / "decomp_evidence.json")
    script_links = load_json(flow / "script_links.json")
    triggers = load_triggers({"story000": flow / "story_records.json", "levels": flow / "levels_records.json"},
                             load_json(flow / "hash_names.json"))

    catalog = Catalog(table, text, titles)
    order = add_story_list(catalog, load_named_list(lists, STORY_LIST_KEY)["items"], resolver)
    add_menu(catalog, build_listed_missions(load_json(work / "progress_missions.json"), table), text)
    side_items = load_named_list(lists, SIDE_LIST_KEY)["items"]
    add_side_list(catalog, side_items, resolver)
    for row in table.values():
        catalog.Ensure(row["id"], "CMissions table")

    add_variants(catalog, load_variant_map(lists), resolver, table)
    fill_chapters(catalog, order, table)
    add_triggers(catalog, triggers)
    fill_protagonists(catalog)
    auto_links = add_auto_flags(catalog, evidence["facts"])
    add_script_links(catalog, script_links, evidence["scripts_referencing_mission_id"])
    main_order = link_sequence(catalog, order)
    finish_pair = next(link["ids"] for link in script_links if link["kind"] == "finish_test")
    mark_flowchart(catalog, main_order, auto_links, finish_pair)

    document = build_document(catalog, order, main_order, auto_links, script_links,
                              [resolver.Name(item) for item in side_items], args.version)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "mission_order.json").write_text(json.dumps(document, indent=2, ensure_ascii=False),
                                                     encoding="utf-8")
    (args.out_dir / "mission_flow.mmd").write_text(build_mermaid(document), encoding="utf-8")
    print(f"main={len(document['main_story_missions'])} side={len(document['side_missions'])} "
          f"unclassified={len(document['unclassified_entries'])} sequence={len(main_order)} "
          f"titles={document['status']['titles_recovered']}")
    print(f"main story without placement: {document['main_story_without_placement']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
