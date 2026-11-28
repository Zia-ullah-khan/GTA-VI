"""Self-check for output/mission_flow.mmd and output/mission_order.json.

Mermaid: every line must match the small grammar the generator emits, blocks must balance, every link endpoint must
be a declared node, and no node may be left without a link. JSON: order and variant edges must form a DAG, and the
chart must show exactly the main-story entries marked in_flowchart.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from flowchart import node_id

NODE = r"m_[A-Za-z0-9_]+"
LABEL = r'"[^"\n]+"'
LINE_PATTERNS = {
    "comment": re.compile(r"^%%.*$"),
    "header": re.compile(r"^flowchart TD$"),
    "subgraph": re.compile(rf"^    subgraph [a-z0-9_]+\[{LABEL}\]$"),
    "direction": re.compile(r"^        direction TB$"),
    "end": re.compile(r"^    end$"),
    "rect": re.compile(rf"^        ({NODE})\[{LABEL}\]$"),
    "stadium": re.compile(rf"^        ({NODE})\(\[{LABEL}\]\)$"),
    "arrow": re.compile(rf"^    ({NODE}) --> ({NODE})$"),
    "line": re.compile(rf"^    ({NODE}) --- ({NODE})$"),
    "dotted": re.compile(rf"^    ({NODE}) -\.-\|[^|\n]+\| ({NODE})$"),
    "classdef": re.compile(r"^    classDef [a-z]+ [^\n]+$"),
    "class": re.compile(rf"^    class {NODE}(,{NODE})* [a-z]+$"),
}
ROOT_NODE = "m_INT_PROLO"


def find_cycle(edges: dict[str, list[str]]) -> list[str]:
    state = {}
    for start in edges:
        if start in state:
            continue

        stack = [(start, iter(edges.get(start, [])))]
        state[start] = "open"
        while stack:
            node, children = stack[-1]
            child = next(children, None)
            if child is None:
                state[node] = "done"
                stack.pop()
                continue

            if state.get(child) == "open":
                return [name for name, _ in stack] + [child]

            if child not in state:
                state[child] = "open"
                stack.append((child, iter(edges.get(child, []))))

    return []


def check_mermaid(path: Path) -> tuple[list[str], dict]:
    problems = []
    nodes = {}
    linked = set()
    arrows = {}
    depth = 0
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "flowchart TD":
        problems.append("first line is not 'flowchart TD'")

    for number, line in enumerate(lines, start=1):
        kind, match = next(((k, p.match(line)) for k, p in LINE_PATTERNS.items() if p.match(line)), (None, None))
        if kind is None:
            problems.append(f"line {number} does not match the chart grammar: {line!r}")
            continue

        if kind == "subgraph":
            depth += 1
        elif kind == "end":
            depth -= 1
        elif kind in ("rect", "stadium"):
            if match.group(1) in nodes:
                problems.append(f"line {number} declares {match.group(1)} twice")

            nodes[match.group(1)] = kind
        elif kind in ("arrow", "line", "dotted"):
            linked.update(match.groups())
            if kind == "arrow":
                arrows.setdefault(match.group(1), []).append(match.group(2))

        if depth < 0:
            problems.append(f"line {number} closes a block that was not opened")

    if depth != 0:
        problems.append("subgraph blocks are not balanced")

    problems += [f"link endpoint {name} is not a declared node" for name in sorted(linked - nodes.keys())]
    orphans = sorted(name for name in nodes if name not in linked and name != ROOT_NODE)
    problems += [f"orphan node {name}" for name in orphans]
    cycle = find_cycle(arrows)
    if cycle:
        problems.append(f"arrows form a cycle: {' -> '.join(cycle)}")

    stats = {"nodes": len(nodes), "rectangles": sum(1 for k in nodes.values() if k == "rect"),
             "stadiums": sum(1 for k in nodes.values() if k == "stadium"), "orphans": len(orphans),
             "arrows": sum(len(v) for v in arrows.values()), "node_ids": set(nodes)}
    return problems, stats


def check_json(path: Path) -> tuple[list[str], dict]:
    problems = []
    document = json.loads(path.read_text(encoding="utf-8"))
    main = document["main_story_missions"]
    everything = main + document["side_missions"] + document["unclassified_entries"]
    ids = [entry["id"] for entry in everything]
    if len(ids) != len(set(ids)):
        problems.append("duplicate mission ids across arrays")

    known = set(ids)
    edges = {}
    sequence = document["main_story_sequence"]
    for previous, following in zip(sequence, sequence[1:]):
        edges.setdefault(previous, []).append(following)

    for entry in everything:
        for variant in entry["variants"]:
            edges.setdefault(entry["id"], []).append(variant)

        for field in ("prerequisites", "unlocks"):
            for other in entry[field] or []:
                if other not in known:
                    problems.append(f"{entry['id']}.{field} names unknown id {other}")

        for other in entry["prerequisites"] or []:
            edges.setdefault(other, []).append(entry["id"])

        if not entry["evidence"]:
            problems.append(f"{entry['id']} has no evidence entry")

    cycle = find_cycle(edges)
    if cycle:
        problems.append(f"dependency edges form a cycle: {' -> '.join(cycle)}")

    stats = {"main": len(main), "side": len(document["side_missions"]),
             "unclassified": len(document["unclassified_entries"]),
             "edges": sum(len(v) for v in edges.values()),
             "titled_main": sum(1 for entry in main if entry["display_name"]),
             "chart_ids": {node_id(entry["id"]) for entry in main if entry["in_flowchart"]}}
    return problems, stats


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out_dir", type=Path)
    args = parser.parse_args()

    chart_problems, chart = check_mermaid(args.out_dir / "mission_flow.mmd")
    json_problems, data = check_json(args.out_dir / "mission_order.json")
    problems = chart_problems + json_problems
    if chart["node_ids"] != data["chart_ids"]:
        problems.append(f"chart nodes differ from in_flowchart entries: "
                        f"{sorted(chart['node_ids'] ^ data['chart_ids'])}")

    print(f"mermaid: nodes={chart['nodes']} rectangles={chart['rectangles']} stadiums={chart['stadiums']} "
          f"arrows={chart['arrows']} orphans={chart['orphans']}")
    print(f"json: main={data['main']} (titled {data['titled_main']}) side={data['side']} "
          f"unclassified={data['unclassified']} dag_edges={data['edges']}")
    for problem in problems:
        print(f"PROBLEM: {problem}")

    print("self-check passed" if not problems else f"self-check failed: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
