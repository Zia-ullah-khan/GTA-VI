"""Report speedrun-relevant fields of the mission trigger records, comparing the story000 and levels copies.

Read-only. Field names were recovered by hashing candidate names with joaat:
starthour, endhour, initialflags and partnerrequired are exact matches. The protagonist field keeps its hash
because its name did not match; its two values are labelled from the ROB_BOAT_J_JASON / ROB_BOAT_L_LUCIA rows.
"""

import json
import sys

FLOW_DIR = r"C:\Users\<user>\Downloads\GTA6.Xbox.v1.0.2.1-CYBERLEEK\work\flow"
COPIES = {"story000": "story_records.json", "levels": "levels_records.json"}

START_HOUR = "1fd5bb99"
END_HOUR = "b376ad2b"
PROTAGONIST = "db880157"
FLAGS_FIELD = "1cfb56b8"
PARTNER_REQUIRED = "dc34120d"
PROTAGONIST_LABELS = {"56d7fe7a": "Jason", "4e21d02a": "Lucia"}


def short(value):
    return value.split(":", 1)[1] if isinstance(value, str) and ":" in value else str(value)


def load_mission_rows(file_name):
    with open(f"{FLOW_DIR}\\{file_name}", encoding="utf-8") as records_file:
        rows = json.load(records_file)

    missions = {}
    for row in rows:
        if ":" not in row["id"]:
            continue

        properties = {short(key): short(value) for key, value in row["hash_properties"].items()}
        properties.update({short(key): short(value) for key, value in row["int_properties"].items()})
        flags = [short(flag) for flag in row["fields"].get(FLAGS_FIELD) or []]
        missions[short(row["id"])] = {"properties": properties, "flags": flags}

    return missions


def describe(mission):
    if mission is None:
        return "absent"

    properties = mission["properties"]
    protagonist = PROTAGONIST_LABELS.get(properties.get(PROTAGONIST), properties.get(PROTAGONIST, "-"))
    window = "-"
    if START_HOUR in properties or END_HOUR in properties:
        window = f"{properties.get(START_HOUR, '?')}-{properties.get(END_HOUR, '?')}"

    partner = "yes" if PARTNER_REQUIRED in mission["flags"] else "no"
    return f"protagonist={protagonist} hours={window} partnerrequired={partner}"


def main():
    copies = {name: load_mission_rows(file_name) for name, file_name in COPIES.items()}
    story = copies["story000"]
    levels = copies["levels"]
    print(f"Mission records: story000={len(story)} levels={len(levels)}")

    print("\n== Protagonist anchors")
    for anchor in ("ROB_BOAT_J_JASON", "ROB_BOAT_L_LUCIA"):
        print(f"{anchor}: {story[anchor]['properties'].get(PROTAGONIST)}")

    print("\n== Time windows (any copy)")
    for mission_id in sorted(set(story) | set(levels)):
        views = {name: copy.get(mission_id) for name, copy in copies.items()}
        if not any(view and START_HOUR in view["properties"] for view in views.values()):
            continue

        for name, view in views.items():
            print(f"{mission_id:38} {name:9} {describe(view)}")

    print("\n== partnerrequired flag")
    for name, copy in copies.items():
        flagged = sorted(mission_id for mission_id, mission in copy.items() if PARTNER_REQUIRED in mission["flags"])
        print(f"{name}: {flagged}")

    print("\n== Protagonist per mission (story000 copy; levels copy shown when it differs)")
    for label in ("Jason", "Lucia", "-"):
        print(f"-- {label}")
        for mission_id in sorted(story):
            if PROTAGONIST_LABELS.get(story[mission_id]["properties"].get(PROTAGONIST), "-") != label:
                continue

            line = f"   {mission_id}"
            other = levels.get(mission_id)
            if other is None:
                line += "   [absent from levels copy]"
            elif other["properties"].get(PROTAGONIST) != story[mission_id]["properties"].get(PROTAGONIST):
                line += f"   [levels copy: {describe(other)}]"

            print(line)

    print("\n== Missions only in one copy")
    print(f"story000 only: {sorted(set(story) - set(levels))}")
    print(f"levels only: {sorted(set(levels) - set(story))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
