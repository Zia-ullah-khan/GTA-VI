"""Read-only checks of the Chapter 1 flow chart claims against the extracted game data."""
import json
import re

ROOT = r"C:\Users\<user>\Downloads\GTA6.Xbox.v1.0.2.1-CYBERLEEK"
MISSION_ORDER = ROOT + r"\output\mission_order.json"
TEXT_TABLE = ROOT + r"\work\text\table_0019be000.json"
CMISSIONS = ROOT + r"\work\cmissions.json"
DISPATCHER = r"C:\Users\<user>\Downloads\americas_scripts_23_11_2026\0xD2601E252151E04B.ysc.cs"
SWEEP_FIRST_LINE = 572964
SWEEP_LAST_LINE = 573009


def joaat(text):
    value = 0
    for char in text.lower().encode("utf-8"):
        value = (value + char) & 0xFFFFFFFF
        value = (value + (value << 10)) & 0xFFFFFFFF
        value ^= value >> 6

    value = (value + (value << 3)) & 0xFFFFFFFF
    value ^= value >> 11
    value = (value + (value << 15)) & 0xFFFFFFFF
    return value


def all_missions(order):
    missions = []
    for section in ("main_story_missions", "side_missions", "unclassified_entries"):
        missions.extend(order.get(section) or [])

    return missions


def read_sweep_hashes():
    hashes = []
    with open(DISPATCHER, encoding="utf-8", errors="ignore") as handle:
        for number, line in enumerate(handle, 1):
            if number < SWEEP_FIRST_LINE:
                continue
            if number > SWEEP_LAST_LINE:
                break

            match = re.search(r"store_i32\(.*, 0x0, 0x([0-9A-Fa-f]+)\);", line)
            if match:
                hashes.append(int(match.group(1), 16) & 0xFFFFFFFF)

    return hashes


def main():
    order = json.load(open(MISSION_ORDER, encoding="utf-8"))
    text = json.load(open(TEXT_TABLE, encoding="utf-8"))
    missions = all_missions(order)
    by_hash = {int(mission["id_hash"], 16): mission for mission in missions if mission.get("id_hash")}

    print("=== MTL_WAKE sweep (func_10AA55) ===")
    for value in read_sweep_hashes():
        mission = by_hash.get(value)
        label = f"{mission['id']} / {mission.get('display_name')}" if mission else "NOT IN mission_order.json"
        print(f"  0x{value:08X} -> {label} | text={text.get(f'{value:08x}')!r}")

    print("=== Island Dreams / CSC_TRH_CHART ===")
    print(f"  joaat('csc_trh_chart') = 0x{joaat('csc_trh_chart'):08X}")
    for mission in missions:
        name = (mission.get("display_name") or "").lower()
        if "island dreams" in name or "TRH" in mission["id"]:
            print(f"  {mission['id']} {mission['id_hash']} name={mission.get('display_name')!r} "
                  f"chapter={mission.get('chapter')} auto={mission.get('auto_flagged_when')}")

    print("=== Chapter 1 rows in mission_order.json ===")
    chapter_one = [mission for mission in missions if mission.get("chapter") == 1]
    chapter_one.sort(key=lambda mission: (mission.get("replay_menu_position") is None,
                                          mission.get("replay_menu_position") or 0, mission["id"]))
    for mission in chapter_one:
        hours = sorted({(trigger.get("hour_start"), trigger.get("hour_end"))
                        for trigger in mission.get("triggers") or []}, key=str)
        auto = [link.get("flag_added_for") for link in mission.get("auto_flagged_when") or []]
        print(f"  pos={mission.get('replay_menu_position')!s:>4} list={mission.get('story_list_position')!s:>4} "
              f"{mission['id']:<30} {mission.get('display_name')!r:<26} prot={mission.get('protagonist')!s:<6} "
              f"hours={hours} auto={auto} prereq={mission.get('prerequisites')}")

    print("=== Text table checks ===")
    for key in ("2a09a6fd", "25c45e20", "03f726c6"):
        print(f"  {key}: {text.get(key)!r}")

    for needle in ("gone fishing", "just a scratch", "gear up", "coastal auto"):
        hits = [(key, value) for key, value in text.items() if isinstance(value, str) and needle in value.lower()]
        print(f"  '{needle}': {len(hits)} strings")
        for key, value in hits[:12]:
            print(f"     {key}: {value[:170]!r}")

    print("=== auto_flag_links / script_links summary ===")
    print(json.dumps(order.get("auto_flag_links"), indent=1)[:3000])
    print(json.dumps(order.get("status"), indent=1)[:2500])


if __name__ == "__main__":
    main()
