"""Match unknown 32-bit hashes from the mission trigger table against joaat of candidate names."""

import itertools
import sys

UNKNOWN_HASHES = {
    "56d7fe7a", "4e21d02a", "d7bf2ddc", "7a7df43c", "e89e9893", "63723981", "e47da526", "dc34120d", "b5a39dd3",
    "db880157", "51ccaea7", "f0af2c92", "b376ad2b", "1fd5bb99", "832592a0", "1cfb56b8", "f9af2922", "2c17a3be",
    "61082633", "cbd2b2cd", "00a1607f", "8bbbcfd5", "bce72a85", "e649394c", "a5336e7b", "bd72abe5", "7e7d13fb",
    "d92a50cb", "ad1e37e4", "1fef187b", "6383db02", "b4e8cacf", "c8ae0a70", "89f23435", "86199a43", "db158746",
    "7e60d9cc", "2fe5af54", "7deb89e3", "58197a18", "072b3ff4", "baf5c37e", "0f450ed3", "c3990870", "2b393413",
    "873c07c8", "715d2c95", "f7550e55", "dfa7f6e3", "e72af09f", "909572cc", "48af935a", "9d0641a8", "d3d89735",
    "0c5b75fb", "8efcbd7f", "4224e41c", "e9a1b741", "398f50c8", "333f7fb4", "b69b0f02",
}

PEOPLE = [
    "jason", "lucia", "cal", "brian", "lori", "donnie", "raul", "boobie", "drequan", "dre_quan", "dre", "mattia",
    "kat", "vicki", "dunk", "moses", "billy", "wyman", "tyrone", "randy", "mia", "halifax", "evelyn", "andrea",
    "karim", "felipe", "nicole", "valentina", "abe", "andres", "petra", "nate", "cisco", "francisco", "kordell",
    "raina", "royce", "giorgio", "vinny", "kevin", "liz", "mendez", "kenton", "joey", "mandy", "arnold", "linda",
    "yasmani", "santino", "omar", "roxy", "baeluxe", "bae_luxe", "dimez", "terro", "viper", "shirley", "tomas",
    "monty", "pete", "benedict", "gallo", "boobie_ike", "abraham", "gustavo", "cesar", "rafa", "bush", "dwnply",
    "charles", "rocky", "dr_bill", "kolt", "mario", "danica", "camila",
]
PREFIXES = ["", "player_", "char_", "contact_", "cs_", "ig_", "npc_", "ped_", "character_", "protagonist_"]
WORDS = [
    "day", "night", "any", "either", "both", "none", "morning", "evening", "starthour", "endhour", "start_hour",
    "end_hour", "hourstart", "hourend", "timestart", "timeend", "start_time", "end_time", "mintime", "maxtime",
    "min_hour", "max_hour", "minhour", "maxhour", "opentime", "closetime", "protagonist", "player", "character",
    "contact", "giver", "missiongiver", "blip", "blipname", "blipsprite", "flags", "conditions", "requirements",
    "position", "radius", "heading", "trigger", "triggertype", "phonecall", "phone_call", "call", "text", "sms",
    "email", "walkin", "walk_in", "interior", "location", "safehouse", "vehicle", "onfoot", "on_foot", "wanted",
    "nowanted", "no_wanted", "notwanted", "partner", "together", "solo", "alone", "withpartner", "with_partner",
    "requirepartner", "requires_partner", "bothplayers", "switch", "canswitch", "weather", "timeofday",
    "time_of_day", "priority", "name", "id", "mission", "missionid", "script", "scriptname", "enabled", "type",
    "true", "false", "default", "invalid", "story", "strand", "chapter", "heist", "bank", "airport",
]


def joaat(text):
    value = 0
    for byte in text.lower().encode("utf-8"):
        value = (value + byte) & 0xFFFFFFFF
        value = (value + (value << 10)) & 0xFFFFFFFF
        value ^= value >> 6

    value = (value + (value << 3)) & 0xFFFFFFFF
    value ^= value >> 11
    value = (value + (value << 15)) & 0xFFFFFFFF
    return value


def candidates(extra_words):
    for prefix, person in itertools.product(PREFIXES, PEOPLE):
        yield prefix + person

    for word in WORDS + extra_words:
        yield word


def main(extra_words):
    found = {}
    for name in candidates(extra_words):
        digest = f"{joaat(name):08x}"
        if digest in UNKNOWN_HASHES:
            found.setdefault(digest, set()).add(name)

    for digest in sorted(found):
        print(digest, sorted(found[digest]))

    print(f"Matched {len(found)} of {len(UNKNOWN_HASHES)} hashes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
