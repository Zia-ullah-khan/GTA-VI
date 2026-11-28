"""Brute-force names for the hashed keys and values of the mission trigger table using the dump's identifier words."""

import collections
import itertools
import re
import sys

from joaat_candidates import UNKNOWN_HASHES, joaat

WORDS_PATH = r"C:\Users\<user>\Downloads\GTA6.Xbox.v1.0.2.1-CYBERLEEK\work\words_dump_identifiers.txt"
PAIR_VOCABULARY_SIZE = 700
EXTRA_TOKENS = [
    "jason", "lucia", "player", "protagonist", "character", "char", "only", "both", "either", "any", "required",
    "requires", "require", "allowed", "available", "for", "as", "is", "can", "must", "needs", "partner", "contact",
    "giver", "owner", "mission", "trigger", "start", "end", "hour", "time", "flags", "flag", "condition",
    "conditions", "interior", "location", "blip", "icon", "sprite", "color", "colour", "label", "name", "title",
    "type", "category", "strand", "group", "chapter", "story", "phone", "call", "text", "message", "walk", "in",
    "on", "off", "enabled", "disabled", "visible", "hidden", "locked", "unlocked", "radius", "range", "distance",
    "priority", "state", "status", "mode", "who", "selected", "active", "current", "main", "male", "female",
    "primary", "secondary", "one", "two", "zero", "first", "second", "a", "b", "p", "pt", "pc", "id", "index",
    "letter", "initial", "short", "long", "display", "map", "world", "ambient", "activity", "event", "content",
    "discoverable", "discovered", "default", "shop", "store", "safehouse", "property", "vehicle", "wanted", "heat",
]


def load_identifier_words():
    with open(WORDS_PATH, encoding="utf-8") as words_file:
        return [line.strip().lower() for line in words_file if line.strip() and not line.startswith("#")]


def build_pair_vocabulary(identifiers):
    counts = collections.Counter()
    for identifier in identifiers:
        counts.update(token for token in re.split(r"[^a-z0-9]+", identifier) if len(token) > 1)

    common = [token for token, _ in counts.most_common(PAIR_VOCABULARY_SIZE)]
    return sorted(set(common) | set(EXTRA_TOKENS))


def candidates(identifiers, vocabulary):
    yield from identifiers
    yield from vocabulary

    for first, second in itertools.product(vocabulary, repeat=2):
        yield first + second
        yield first + "_" + second


def main():
    identifiers = load_identifier_words()
    vocabulary = build_pair_vocabulary(identifiers)
    print(f"Hashing {len(identifiers)} identifiers and pairs of {len(vocabulary)} tokens")

    found = {}
    for name in candidates(identifiers, vocabulary):
        digest = f"{joaat(name):08x}"
        if digest in UNKNOWN_HASHES:
            found.setdefault(digest, set()).add(name)

    for digest in sorted(found):
        print(digest, sorted(found[digest]))

    print(f"Matched {len(found)} of {len(UNKNOWN_HASHES)} hashes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
