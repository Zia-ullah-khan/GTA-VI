"""Build output/mission_order.json and output/mission_flow.mmd from extracted evidence only.

Dependency edges were not recoverable from this dump, so prerequisite-type fields are emitted as null (unknown),
never as empty lists, and the diagram contains no dependency arrows.
"""

import argparse
import json
import re
import sys
from pathlib import Path

CMISSIONS_SOURCE = "common.rpf @ 0x219000 (zlib payload, XML root <CMissions>)"
PROGRESS_SOURCE = "data.rpf @ 0x12010000 (zlib payload, RBF0 root <uiProgressDataset>)"
PROGRESS_PATH = "Topics/record/Categories/missions_card/.../Filters/{filter_id}/Items[{position}]"
LABEL_PREFIX = "PROG_"
CHAPTER_NUMBERS = {"missions_chapter_1": 1, "missions_chapter_2": 2, "missions_chapter_3": 3,
                   "missions_chapter_4": 4, "missions_chapter_5": 5}
UNSAFE_NODE_CHARS = re.compile(r"[^A-Za-z0-9_]")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def texture_chapter(entry: dict | None) -> int | None:
    if entry is None or not entry["grid_chapter"] or not entry["grid_chapter"].startswith("CH"):
        return None

    return int(entry["grid_chapter"][2:])


def find_variants(base_id: str, table: dict[str, dict], listed: set[str]) -> list[str]:
    prefix = base_id.upper() + "_"
    return sorted(entry["id"] for key, entry in table.items() if key.startswith(prefix) and key not in listed)


def canonical_id(raw_id: str, table: dict[str, dict]) -> str:
    entry = table.get(raw_id.upper())
    return entry["id"] if entry else raw_id.upper()


def label_mission_id(label: str, table: dict[str, dict]) -> str | None:
    candidate = label.upper()
    if candidate.startswith(LABEL_PREFIX):
        candidate = candidate[len(LABEL_PREFIX):]

    return table[candidate]["id"] if candidate in table else None


def build_listed_missions(listing: list[dict], table: dict[str, dict]) -> list[dict]:
    listed_keys = set()
    for category in listing:
        for group in category["filters"]:
            listed_keys.update(item["item_id"].upper() for item in group["items"])

    missions = []
    for category in listing:
        for group in category["filters"]:
            chapter = CHAPTER_NUMBERS[group["filter_id"]]
            for item in group["items"]:
                entry = table.get(item["item_id"].upper())
                mission_id = canonical_id(item["item_id"], table)
                unlock_id = canonical_id(item["unlock_id"], table)
                labelled_as = label_mission_id(item["label"], table)
                evidence = [f"{PROGRESS_SOURCE} "
                            + PROGRESS_PATH.format(filter_id=group["filter_id"], position=item["position"])]
                if entry:
                    evidence.append(f"{CMISSIONS_SOURCE} Item[UniqueMissionIndex={entry['index']}]")

                missions.append({
                    "id": mission_id,
                    "display_name": None,
                    "display_name_text_key": item["label"],
                    "label_names_different_cmissions_id": labelled_as if labelled_as != mission_id else None,
                    "replay_entry_unlock_id": unlock_id,
                    "replay_entry_keyed_to_other_mission": unlock_id != mission_id,
                    "replay_entry_evaluator": item["evaluator"],
                    "chapter_or_act": f"Chapter {chapter}",
                    "replay_menu_position": item["position"],
                    "texture_chapter_tag": texture_chapter(entry),
                    "chapter_sources_agree": texture_chapter(entry) in (None, chapter),
                    "in_cmissions_table": entry is not None,
                    "unique_mission_index": entry["index"] if entry else None,
                    "name_prefixed_variant_entries": find_variants(mission_id, table, listed_keys),
                    "protagonist": None,
                    "prerequisites": None,
                    "unlocks": None,
                    "trigger_type": None,
                    "is_bottleneck": None,
                    "any_percent_required": None,
                    "evidence": evidence,
                })

    return missions


def build_unlisted_entries(table: dict[str, dict], missions: list[dict]) -> list[dict]:
    listed = {m["id"].upper() for m in missions}
    claimed = {variant.upper() for m in missions for variant in m["name_prefixed_variant_entries"]}
    unlisted = []
    for key, entry in sorted(table.items(), key=lambda pair: pair[1]["index"]):
        if key in listed:
            continue

        unlisted.append({
            "id": entry["id"],
            "unique_mission_index": entry["index"],
            "texture_chapter_tag": texture_chapter(entry),
            "name_prefix_of_listed_mission": key in claimed,
            "evidence": [f"{CMISSIONS_SOURCE} Item[UniqueMissionIndex={entry['index']}]"],
        })

    return unlisted


def build_replay_links(missions: list[dict]) -> list[dict]:
    return [{
        "replay_entry": mission["id"],
        "unlock_id_mission": mission["replay_entry_unlock_id"],
        "evaluator": mission["replay_entry_evaluator"],
        "meaning": "The progress-menu replay entry is keyed to another mission's state. "
                   "This is menu-reveal data, not a mission availability prerequisite.",
        "evidence": mission["evidence"][0] + " fields ID vs UnlockId",
    } for mission in missions if mission["replay_entry_keyed_to_other_mission"]]


def attach_script_references(entries: list[dict], script_evidence: dict | None) -> None:
    if script_evidence is None:
        return

    references = script_evidence["scripts_referencing_mission_id"]
    for entry in entries:
        entry["decompiled_mission_scripts_referencing_id"] = references.get(entry["id"], [])


def flag_links(missions: list[dict], script_evidence: dict | None) -> list[tuple[str, str]]:
    if script_evidence is None:
        return []

    listed = {mission["id"] for mission in missions}
    links = []
    for fact in script_evidence["facts"]:
        if fact["kind"] != "handler_sets_flag":
            continue

        if fact["when_argument_equals"] in listed and fact["target"] in listed:
            links.append((fact["when_argument_equals"], fact["target"]))

    return links


def build_document(missions: list[dict], unlisted: list[dict], table_size: int, version: str,
                   script_evidence: dict | None) -> dict:
    return {
        "metadata": {
            "build_version": version,
            "build_version_evidence": "appxmanifest.xml and MicrosoftGame.Config <Identity Version>",
            "status": "partial_inventory_with_script_evidence" if script_evidence else "partial_inventory_only",
            "decompiled_script_source": script_evidence["source_dir"] if script_evidence else None,
            "decompiled_script_caveat": "Separate folder supplied by the user. Its relationship to this build is "
                                        "not verified beyond 144 of 145 CMissions ID hashes occurring in it. "
                                        "It contains no string heap, so no display text.",
            "script_flow_facts_recovered": len(script_evidence["facts"]) if script_evidence else 0,
            "prerequisite_edges_recovered": 0,
            "replay_menu_cross_mission_links_recovered": sum(
                1 for m in missions if m["replay_entry_keyed_to_other_mission"]),
            "total_main_story_mission_count": None,
            "total_mandatory_any_percent_count": None,
            "replay_menu_mission_entries": len(missions),
            "cmissions_table_entries": table_size,
            "null_means": "unknown: not recoverable from this dump. It does not mean none or false.",
            "ordering_caveat": "replay_menu_position is the progress-menu display order inside each chapter filter. "
                               "It is not an unlock order and must not be used as a prerequisite chain.",
            "blockers": [
                "No game executable in the dump, so no key material and no native tables",
                "RPF9 name tables are encrypted, so extracted files have no names",
                "Script objects in script.rpf and story000_script.rpf use 32-bit hashed identifiers and "
                "block-cipher-encrypted string tables (LSNS)",
                "67% of story000_script.rpf (52.2 MB in 31 regions) is neither zlib nor plaintext",
                "No localized text table was found in readable form, so display titles are unavailable",
                "The decompiled scripts reference strings only as heap offsets (Vm.StringConstant) and the heap "
                "is not included, natives are mostly unnamed hashes, and mission scripts reference only their "
                "own mission ID, so availability conditions were not found in script code",
            ],
        },
        "missions": missions,
        "script_flow_evidence": script_evidence["facts"] if script_evidence else None,
        "replay_menu_cross_mission_links": build_replay_links(missions),
        "cmissions_entries_not_in_replay_menu": unlisted,
    }


def node_id(mission_id: str) -> str:
    return "m_" + UNSAFE_NODE_CHARS.sub("_", mission_id)


def build_mermaid(missions: list[dict], script_evidence: dict | None) -> str:
    lines = [
        "%% Replay-menu mission listing recovered from uiProgressDataset and CMissions.",
        "%% NO mission prerequisite edges were recovered.",
        "%% Dashed 'replay entry UnlockId' links: the target's menu entry carries the source as UnlockId.",
        "%% Dashed 'handler sets flag' links: decompiled func_10AA55 sets the target's flag when called with the",
        "%% source ID. Neither link type is an unlock prerequisite.",
        "%% Order inside each chapter is progress-menu display order, not unlock order.",
        "flowchart TD",
        "    notice{{\"No unlock prerequisites recovered. Listing only, in replay-menu display order\"}}",
    ]
    chapters = sorted({m["chapter_or_act"] for m in missions})
    for chapter in chapters:
        lines.append(f"    subgraph {chapter.replace(' ', '_')}[\"{chapter} (replay-menu filter)\"]")
        lines.append("        direction TB")
        for mission in (m for m in missions if m["chapter_or_act"] == chapter):
            shape = "unverified" if mission["chapter_sources_agree"] else "disputed"
            lines.append(f"        {node_id(mission['id'])}[\"{mission['id']}\"]:::{shape}")

        lines.append("    end")

    for mission in missions:
        if mission["replay_entry_keyed_to_other_mission"]:
            lines.append(f"    {node_id(mission['replay_entry_unlock_id'])} -.->|replay entry UnlockId| "
                         f"{node_id(mission['id'])}")

    for source, target in flag_links(missions, script_evidence):
        lines.append(f"    {node_id(source)} -.->|handler sets flag| {node_id(target)}")

    lines.append("    classDef unverified fill:#f4f4f4,stroke:#888,color:#222")
    lines.append("    classDef disputed fill:#fff3cd,stroke:#b58900,color:#222")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cmissions", type=Path, required=True)
    parser.add_argument("--progress", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--script-evidence", type=Path)
    args = parser.parse_args()

    required = [args.cmissions, args.progress] + ([args.script_evidence] if args.script_evidence else [])
    for path in required:
        if not path.is_file():
            print(f"Not a file: {path}", file=sys.stderr)
            return 1

    table = {entry["id"].upper(): entry for entry in load_json(args.cmissions)}
    script_evidence = load_json(args.script_evidence) if args.script_evidence else None
    missions = build_listed_missions(load_json(args.progress), table)
    unlisted = build_unlisted_entries(table, missions)
    attach_script_references(missions, script_evidence)
    attach_script_references(unlisted, script_evidence)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    document = build_document(missions, unlisted, len(table), args.version, script_evidence)
    (args.out_dir / "mission_order.json").write_text(json.dumps(document, indent=2), encoding="utf-8")
    (args.out_dir / "mission_flow.mmd").write_text(build_mermaid(missions, script_evidence), encoding="utf-8")

    disputed = [m["id"] for m in missions if not m["chapter_sources_agree"]]
    missing = [m["id"] for m in missions if not m["in_cmissions_table"]]
    print(f"listed missions={len(missions)} unlisted cmissions entries={len(unlisted)}")
    print(f"chapter sources disagree ({len(disputed)}): {disputed}")
    print(f"in replay menu but not in CMissions ({len(missing)}): {missing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
