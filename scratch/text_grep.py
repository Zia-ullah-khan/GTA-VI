"""Search the extracted game text table with one or more regex patterns."""

import json
import re
import sys

TEXT_TABLE_PATH = r"C:\Users\<user>\Downloads\GTA6.Xbox.v1.0.2.1-CYBERLEEK\work\text\table_0019be000.json"
MAX_TEXT_LENGTH = 420


def load_text_table():
    with open(TEXT_TABLE_PATH, encoding="utf-8") as table_file:
        return json.load(table_file)


def search(table, pattern, limit, max_source_length):
    regex = re.compile(pattern, re.IGNORECASE)
    matches = [
        (key, text)
        for key, text in table.items()
        if isinstance(text, str) and len(text) <= max_source_length and regex.search(text)
    ]
    print(f"=== /{pattern}/ {len(matches)} matches (source strings up to {max_source_length} chars)")

    for key, text in sorted(matches, key=lambda match: match[1])[:limit]:
        flat = text.replace("\n", " \\n ")
        print(f"{key}  {flat[:MAX_TEXT_LENGTH]}")


def main(arguments):
    if not arguments:
        print("Usage: text_grep.py [--limit N] [--maxlen N] PATTERN [PATTERN ...]")
        return 2

    limit = 80
    max_source_length = 100000
    while arguments and arguments[0] in ("--limit", "--maxlen"):
        if arguments[0] == "--limit":
            limit = int(arguments[1])
        else:
            max_source_length = int(arguments[1])

        arguments = arguments[2:]

    table = load_text_table()
    for pattern in arguments:
        search(table, pattern, limit, max_source_length)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
