"""Print every hash list found under chosen blocks of a decoded PSO tree, resolving unnamed hashes via the text table."""

import argparse
import json
import sys
from pathlib import Path


def load_text(path: Path | None) -> dict[int, str]:
    if path is None:
        return {}

    return {int(key, 16): value for key, value in json.loads(path.read_text(encoding="utf-8")).items()}


def render(value: str, text: dict[int, str]) -> str:
    if ":" in value:
        return value.split(":", 1)[1]

    title = text.get(int(value, 16))
    return value if title is None else f"{value}«{title}»"


def walk(value, path: str, text: dict[int, str], minimum: int) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            walk(item, f"{path}.{key}", text, minimum)

        return

    if not isinstance(value, list):
        return

    if value and all(isinstance(item, str) for item in value):
        if len(value) >= minimum:
            print(f"{path} [{len(value)}]: " + ", ".join(render(item, text) for item in value))

        return

    for index, item in enumerate(value):
        walk(item, f"{path}[{index}]", text, minimum)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tree", type=Path)
    parser.add_argument("blocks", type=int, nargs="+")
    parser.add_argument("--text", type=Path)
    parser.add_argument("--min", type=int, default=1)
    args = parser.parse_args()

    document = json.loads(args.tree.read_text(encoding="utf-8"))
    text = load_text(args.text)
    for block in document["blocks"]:
        if block["number"] not in args.blocks:
            continue

        for index, row in enumerate(block["rows"]):
            key = row.get("6098a50e", "") if isinstance(row, dict) else ""
            walk(row, f"b{block['number']}r{index}({key})", text, args.min)

    return 0


if __name__ == "__main__":
    sys.exit(main())
