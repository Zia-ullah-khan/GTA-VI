"""Load the decoded game-data sources used by the final deliverables.

Every loader returns plain data plus the artifact location it came from, so each output field can cite its origin.
"""

import json
from pathlib import Path

LISTS_SOURCE = "pack/story000/story000.rpf @ 0x3e30b5000 (PSO, 262,496 bytes inflated)"
STORY_LIST_KEY = "b95219d4"
SIDE_LIST_KEY = "4f7ef576"
VARIANT_MAP_KEY = "54f9a1be"
LIST_BLOCK = 24
LIST_VALUE_FIELD = "063fa3f2"
LIST_KEY_FIELD = "6098a50e"
LIST_ITEMS_FIELD = "ef2037f0"
LIST_TYPE_FIELD = "5538a0a1"
VARIANT_ROWS_FIELD = "d05707e4"
VARIANT_BASE_FIELD = "26516057"
VARIANT_ITEMS_FIELD = "68eb1b31"

TRIGGER_SOURCES = {
    "story000": "pack/story000/story000.rpf @ 0x3e2372000 (PSO, 2,166,996 bytes inflated)",
    "levels": "levels.rpf @ 0x11bb116000 (PSO, 1,498,864 bytes inflated)",
}
REQUIRED_PLAYER_KEY = "db880157"
CONTACT_KEY = "f0af2c92"
HOUR_START_KEY = "1fd5bb99"
HOUR_END_KEY = "b376ad2b"
FLAGS_KEY = "832592a0"
REQUIRED_PLAYER_VALUES = {"4e21d02a": "Lucia", "56d7fe7a": "Jason"}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class IdResolver:
    """Turns '<hash>' or '<hash>:<NAME>' into a display ID, using only exact joaat matches recorded earlier."""

    def __init__(self, recovered_names: dict[str, list[str]], titles: dict[str, str]):
        self._recovered = {key: names[0] for key, names in recovered_names.items() if len(names) == 1}
        self._titles = titles

    def Name(self, value: str) -> str:
        if ":" in value:
            return value.split(":", 1)[1]

        return self._recovered.get(value, f"0x{value.upper()}")

    def IsRecovered(self, value: str) -> bool:
        return ":" not in value and value in self._recovered

    def Title(self, value: str) -> str | None:
        return self._titles.get(value.split(":", 1)[0])


def _list_rows(tree: dict) -> list[dict]:
    for block in tree["blocks"]:
        if block["number"] == LIST_BLOCK:
            return [row for row in block["rows"] if isinstance(row.get(LIST_VALUE_FIELD), dict)]

    raise ValueError(f"Block {LIST_BLOCK} missing from list tree")


def load_named_list(tree: dict, key: str) -> dict:
    for row in _list_rows(tree):
        if row[LIST_KEY_FIELD] == key:
            value = row[LIST_VALUE_FIELD]
            return {"key": key, "type_hash": value[LIST_TYPE_FIELD], "items": value[LIST_ITEMS_FIELD]}

    raise ValueError(f"List {key} missing from list tree")


def load_variant_map(tree: dict) -> list[dict]:
    for row in _list_rows(tree):
        if row[LIST_KEY_FIELD] == VARIANT_MAP_KEY:
            return [{"base": entry[VARIANT_BASE_FIELD], "variants": entry[VARIANT_ITEMS_FIELD]}
                    for entry in row[LIST_VALUE_FIELD][VARIANT_ROWS_FIELD]]

    raise ValueError("Variant map missing from list tree")


def _trigger(row: dict, source: str, contact_names: dict[str, list[str]]) -> dict:
    properties = {**row["hash_properties"], **row["int_properties"]}
    contact = properties.get(CONTACT_KEY)
    contact_hash = contact.split(":", 1)[0] if contact else None
    required = properties.get(REQUIRED_PLAYER_KEY)
    return {
        "source": TRIGGER_SOURCES[source],
        "position": row["positions"][0] if row["positions"] else None,
        "required_player_hash": f"0x{required.upper()}" if required else None,
        "required_player": REQUIRED_PLAYER_VALUES.get(required) if required else None,
        "contact_hash": f"0x{contact_hash.upper()}" if contact_hash else None,
        "contact_name": (contact_names.get(contact_hash) or [None])[0] if contact_hash else None,
        "hour_start": properties.get(HOUR_START_KEY),
        "hour_end": properties.get(HOUR_END_KEY),
        "flags": properties.get(FLAGS_KEY),
    }


def load_triggers(paths: dict[str, Path], contact_names: dict[str, list[str]]) -> dict[str, list[dict]]:
    """Map mission ID -> trigger records, one per data file that defines it."""
    triggers = {}
    for source, path in paths.items():
        for row in load_json(path):
            if ":" not in row["id"]:
                continue

            name = row["id"].split(":", 1)[1]
            triggers.setdefault(name, []).append(_trigger(row, source, contact_names))

    return triggers


def load_titles(table_path: Path) -> dict[str, str]:
    return {key: value for key, value in load_json(table_path).items() if value}


def flatten_text_keys(mission_text: dict) -> dict[str, str]:
    flat = dict(mission_text.get("other_keys", {}))
    for keys in mission_text["missions"].values():
        flat.update(keys)

    return {key.upper(): value for key, value in flat.items()}
