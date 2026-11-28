"""Locate extracted XML documents by root element and summarize their element and attribute structure."""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

UTF8_BOM = b"\xef\xbb\xbf"
ELEMENT = re.compile(r"<([A-Za-z_][\w:.-]*)")
ATTRIBUTE = re.compile(r"\s([A-Za-z_][\w:.-]*)=[\"']")


def is_xml(data: bytes) -> bool:
    return data.startswith(b"<") or data.startswith(UTF8_BOM)


def root_element(text: str) -> str:
    for name in ELEMENT.findall(text[:4000]):
        return name

    return ""


def summarize(path: Path, text: str, top: int) -> None:
    print(f"{path.name} bytes={len(text.encode('utf-8'))} lines={text.count(chr(10))}")
    print("elements:")
    for name, count in Counter(ELEMENT.findall(text)).most_common(top):
        print(f"   {count:>6}  {name}")

    print("attributes:")
    for name, count in Counter(ATTRIBUTE.findall(text)).most_common(top):
        print(f"   {count:>6}  {name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("extracted_dir", type=Path)
    parser.add_argument("root")
    parser.add_argument("--save", type=Path)
    parser.add_argument("--top", type=int, default=60)
    args = parser.parse_args()

    if not args.extracted_dir.is_dir():
        print(f"Not a directory: {args.extracted_dir}", file=sys.stderr)
        return 1

    matches = 0
    for path in sorted(args.extracted_dir.glob("*.bin")):
        data = path.read_bytes()
        if not is_xml(data):
            continue

        text = data.decode("utf-8-sig", errors="replace")
        if root_element(text) != args.root:
            continue

        matches += 1
        summarize(path, text, args.top)
        if args.save:
            target = args.save if matches == 1 else args.save.with_name(f"{args.save.stem}_{matches}{args.save.suffix}")
            target.write_text(text, encoding="utf-8")
            print(f"saved: {target}")

    if matches == 0:
        print(f"No XML document with root <{args.root}>", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
