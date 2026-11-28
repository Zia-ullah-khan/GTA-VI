"""Render the main-story Mermaid flowchart from the mission_order document."""

import re

UNSAFE_NODE_CHARS = re.compile(r"[^A-Za-z0-9_]")
HEADER = [
    "flowchart TD",
    "%% Rectangle  = entry of the game's own ordered mission list (story000.rpf @ 0x3e30b5000, list 0xB95219D4)",
    "%% Stadium    = alternative variant of an entry (variant map / ID name), or a mission placed only by a script link",
    "%% Dashed box = flag is set by the game itself in func_10AA55 (auto-completed, not needed for Any%)",
    "%% A --> B    = B is the next main-story entry after A in that list. This is stored ORDER, not a proven unlock.",
    "%% A --- B    = B is a variant of A",
    "%% A -.- B    = script link, labelled: 'auto-flags' means flagging A makes the handler flag B as well",
    "%% Blue = trigger record requires Jason, pink = requires Lucia, both taken from property 0xDB880157",
]
CLASS_LINES = [
    "    classDef auto stroke-dasharray: 6 4",
    "    classDef jason fill:#dbeafe,stroke:#1d4ed8",
    "    classDef lucia fill:#fce7f3,stroke:#be185d",
]


def node_id(mission_id: str) -> str:
    return "m_" + UNSAFE_NODE_CHARS.sub("_", mission_id)


def node_label(entry: dict) -> str:
    title = entry["display_name"]
    text = f"{title} [{entry['id']}]" if title else f"[{entry['id']}]"
    return text.replace('"', "#quot;")


def node_line(entry: dict, in_sequence: bool) -> str:
    label = node_label(entry)
    if in_sequence:
        return f'        {node_id(entry["id"])}["{label}"]'

    return f'        {node_id(entry["id"])}(["{label}"])'


def chapter_blocks(shown: list[dict], sequence: set[str]) -> list[str]:
    lines = []
    chapters = sorted({entry["chapter"] for entry in shown if entry["chapter"] is not None})
    groups = [(chapter, f"Chapter {chapter}") for chapter in chapters]
    if any(entry["chapter"] is None for entry in shown):
        groups.append((None, "Chapter not established"))

    for chapter, title in groups:
        name = f"chapter_{chapter}" if chapter is not None else "chapter_unknown"
        lines.append(f'    subgraph {name}["{title}"]')
        lines.append("        direction TB")
        lines += [node_line(entry, entry["id"] in sequence) for entry in shown if entry["chapter"] == chapter]
        lines.append("    end")

    return lines


def link_lines(document: dict, shown_ids: set[str]) -> list[str]:
    lines = []
    sequence = document["main_story_sequence"]
    for previous, following in zip(sequence, sequence[1:]):
        lines.append(f"    {node_id(previous)} --> {node_id(following)}")

    for entry in document["main_story_missions"]:
        for variant in entry["variants"]:
            if entry["id"] in shown_ids and variant in shown_ids:
                lines.append(f"    {node_id(entry['id'])} --- {node_id(variant)}")

    for link in document["auto_flag_links"]:
        if link["from"] in shown_ids and link["to"] in shown_ids:
            lines.append(f"    {node_id(link['from'])} -.-|auto-flags| {node_id(link['to'])}")

    for link in document["script_links"]:
        if link["kind"] == "finish_test" and all(mission_id in shown_ids for mission_id in link["ids"]):
            first, second = link["ids"]
            lines.append(f"    {node_id(second)} -.-|either flag passes the finish test| {node_id(first)}")

    return lines


def class_lines(shown: list[dict]) -> list[str]:
    groups = {
        "auto": [e for e in shown if e["any_percent_required"] is False],
        "jason": [e for e in shown if e["protagonist"] == "Jason"],
        "lucia": [e for e in shown if e["protagonist"] == "Lucia"],
    }
    lines = list(CLASS_LINES)
    for name, members in groups.items():
        if members:
            lines.append(f"    class {','.join(node_id(e['id']) for e in members)} {name}")

    return lines


def build_mermaid(document: dict) -> str:
    shown = [entry for entry in document["main_story_missions"] if entry["in_flowchart"]]
    shown_ids = {entry["id"] for entry in shown}
    sequence = set(document["main_story_sequence"])
    lines = HEADER + chapter_blocks(shown, sequence) + link_lines(document, shown_ids) + class_lines(shown)
    return "\n".join(lines) + "\n"
