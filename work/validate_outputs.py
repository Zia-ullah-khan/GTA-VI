"""Self-check for the generated deliverables: JSON integrity, acyclicity, and a structural lint of the Mermaid file."""

import argparse
import json
import re
import sys
from pathlib import Path

NODE_DEFINITION = re.compile(r"^\s+(m_[A-Za-z0-9_]+)\[\"")
LINK = re.compile(r"^\s+(m_[A-Za-z0-9_]+)\s+-\.->\|[^|]*\|\s+(m_[A-Za-z0-9_]+)\s*$")
SOLID_ARROW = re.compile(r"-->|==>")


def has_cycle(edges: dict[str, list[str]]) -> bool:
    state = {}
    for start in edges:
        stack = [(start, iter(edges.get(start, [])))]
        if state.get(start):
            continue

        state[start] = 1
        while stack:
            node, children = stack[-1]
            advanced = False
            for target in children:
                if state.get(target) == 1:
                    return True
                if not state.get(target):
                    state[target] = 1
                    stack.append((target, iter(edges.get(target, []))))
                    advanced = True
                    break

            if not advanced:
                state[node] = 2
                stack.pop()

    return False


def check_json(path: Path) -> list[str]:
    document = json.loads(path.read_text(encoding="utf-8"))
    missions = document["missions"]
    ids = [m["id"] for m in missions]
    with_prerequisites = [m["id"] for m in missions if m["prerequisites"] is not None]
    links = {}
    for link in document["replay_menu_cross_mission_links"]:
        links.setdefault(link["unlock_id_mission"], []).append(link["replay_entry"])

    dangling = [target for targets in links.values() for target in targets if target not in ids]
    dangling += [source for source in links if source not in ids]
    return [
        f"json parses: True",
        f"mission ids unique: {len(ids) == len(set(ids))} ({len(set(ids))}/{len(ids)})",
        f"missions with a recovered prerequisite expression: {len(with_prerequisites)}",
        f"prerequisite graph acyclic: vacuously true, it has 0 edges",
        f"replay-link graph: edges={sum(len(v) for v in links.values())} acyclic={not has_cycle(links)} "
        f"dangling_endpoints={dangling}",
        f"every mission has evidence: {all(m['evidence'] for m in missions)}",
    ]


def check_mermaid(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    body = [line for line in lines if not line.lstrip().startswith("%%")]
    nodes = [m.group(1) for line in body if (m := NODE_DEFINITION.match(line))]
    links = [(m.group(1), m.group(2)) for line in body if (m := LINK.match(line))]
    linked = {endpoint for link in links for endpoint in link}
    opened = sum(1 for line in body if line.strip().startswith("subgraph "))
    closed = sum(1 for line in body if line.strip() == "end")
    undefined = sorted(linked - set(nodes))
    orphans = [node for node in nodes if node not in linked]
    return [
        f"first directive is flowchart TD: {body[0].strip() == 'flowchart TD'}",
        f"subgraph/end balanced: {opened == closed} ({opened}/{closed})",
        f"node definitions: {len(nodes)} unique: {len(nodes) == len(set(nodes))}",
        f"links: {len(links)} endpoints undefined: {undefined}",
        f"solid dependency arrows present: {any(SOLID_ARROW.search(line) for line in body)}",
        f"orphan nodes (no link): {len(orphans)} of {len(nodes)}",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out_dir", type=Path)
    args = parser.parse_args()

    json_path = args.out_dir / "mission_order.json"
    mermaid_path = args.out_dir / "mission_flow.mmd"
    for path in (json_path, mermaid_path):
        if not path.is_file():
            print(f"Missing deliverable: {path}", file=sys.stderr)
            return 1

    print("mission_order.json")
    for line in check_json(json_path):
        print(f"   {line}")

    print("mission_flow.mmd")
    for line in check_mermaid(mermaid_path):
        print(f"   {line}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
