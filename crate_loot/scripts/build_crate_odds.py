"""Build the crate pickup odds tables.

Reads the decoded layout tree and the XML prop list from the local work folder and writes:
  data/crate_prop_names.csv   prop ID -> prop name (position-matched)
  data/crate_pool_odds.csv    per pool, per item: layouts containing it and chance per crate
  data/crate_zone_odds.csv    per zone type (including default unzoned), weighted chance per crate
Nothing from the game is copied into the output beyond prop names and derived counts.
"""
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "data"
TREE = Path("C:/Users/khans/Downloads/GTA6-RE/work/containers/tree_1be4f000.json")
XML = Path("C:/Users/khans/Downloads/container_crates.ymt.pso.xml")

POOL_NAMES = {
    0: "airstrip_con_crate",
    1: "ammo_con_crate",
    2: "construction_con_crate",
    3: "farm_con_crate",
    4: "food_con_crate",
    5: "industrial_con_crate",
    6: "medical_con_crate",
    7: "prison_con_crate",
    8: "weapons_con_crate",
    9: "abandoned_con_crate",
    10: "drugs_con_crate",
    11: "port_con_crate",
    12: "pool12_5ff745b2",
    13: "policepharm",
    14: "marina_con_crate",
    15: "pickups_con_crate",
}

# Zone-type -> list of (weight, kind, target) from container_crates.ymt.pso.xml
ZONE_PROVIDERS = {
    "airstrip": [(1.0, "pool", "airstrip_con_crate")],
    "construction": [(1.0, "pool", "construction_con_crate")],
    "industrial": [(1.0, "pool", "industrial_con_crate")],
    "military": [
        (20.0, "pool", "ammo_con_crate"),
        (40.0, "pool", "policepharm"),
        (40.0, "layout", "0c5c0e16"),
    ],
    "abandoned": [(1.0, "pool", "abandoned_con_crate")],
    "farm": [(1.0, "pool", "farm_con_crate")],
    "medical": [(1.0, "pool", "medical_con_crate")],
    "port": [(1.0, "pool", "port_con_crate")],
    "default_unzoned": [
        (80.0, "pool", "pickups_con_crate"),
        (30.0, "pool", "construction_con_crate"),
    ],
}

xml = XML.read_text(encoding="utf-8", errors="ignore")
xmlprops = defaultdict(list)
for b in re.split(r'<Item type="PpdPDFA_0x6A7B2BC2">', xml)[1:]:
    m = re.search(r"<Name>([^<]*)</Name>", b)
    if not m:
        continue
    lay_id = m.group(1).split("_0x")[-1].lower()
    for it in re.finditer(r'<Item type="PwAYfDA_0xF42933B2">(.*?)</Item>', b, re.S):
        body = it.group(1)
        pm = re.search(r'<Position x="([^"]+)" y="([^"]+)" z="([^"]+)"', body)
        nm = re.search(r"<Prop>([^<]+)</Prop>", body)
        if pm and nm:
            xmlprops[lay_id].append((tuple(round(float(pm.group(i)), 3) for i in (1, 2, 3)), nm.group(1)))

t = json.loads(TREE.read_text(encoding="utf-8"))
B = {b["number"]: b for b in t["blocks"]}
lay = {r["acec22be"]: r for r in B[8]["rows"]}
name = defaultdict(set)
for r in B[8]["rows"]:
    for it in r.get("9a18c89f", []):
        pos = it.get("8b424621", {}).get("0c928991")
        c = it.get("0e3117bd", {})
        if c.get("type") == "57d66554" and pos:
            p = tuple(round(x, 3) for x in pos)
            for xp, xn in xmlprops.get(r["acec22be"], []):
                if all(abs(a - b) < 0.0015 for a, b in zip(p, xp)):
                    name[c["2257ebb9"]].add(xn)


def flat(n, seen=frozenset()):
    if n in seen or n not in lay:
        return set()
    seen = seen | {n}
    out = set()
    for it in lay[n].get("9a18c89f", []):
        c = it.get("0e3117bd", {})
        if c.get("type") == "57d66554":
            out.add(("prop", c["2257ebb9"]))
        elif c.get("type") == "7a5e90d1":
            out.add(("weapon", c["6aafc241"]))
        elif c.get("type") == "1b790739":
            out |= flat(c["7efea5a0"], seen)
    return out


def item_label(kind, item_id):
    if kind == "weapon":
        return f"weapon_{item_id}"
    return ";".join(sorted(name.get(item_id, ["unnamed"])))


OUT.mkdir(parents=True, exist_ok=True)
with (OUT / "crate_prop_names.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["prop_id", "prop_name"])
    for k in sorted(name, key=lambda k: sorted(name[k])[0]):
        w.writerow([k, ";".join(sorted(name[k]))])

pools = B[2]["rows"]
pool_sets = {}
pool_rows = []
for i, p in enumerate(pools):
    pname = POOL_NAMES[i]
    ls = p["c19c0de4"]
    sets = [flat(l) for l in ls]
    pool_sets[pname] = sets
    items = set().union(*sets)
    for kind, iid in sorted(items):
        c = sum((kind, iid) in s for s in sets)
        pool_rows.append([pname, len(ls), kind, iid, item_label(kind, iid), c, round(100 * c / len(ls), 1)])

with (OUT / "crate_pool_odds.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["pool", "layouts_in_pool", "item_type", "item_id", "item_name", "layouts_with_item", "chance_per_crate_pct"])
    w.writerows(pool_rows)

zone_rows = []
for zname, branches in ZONE_PROVIDERS.items():
    total_w = sum(w for w, _, _ in branches)
    item_probs = defaultdict(float)
    for w, kind, target in branches:
        bw = w / total_w
        if kind == "pool":
            sets = pool_sets[target]
            for s in sets:
                for it in s:
                    item_probs[it] += bw / len(sets)
        elif kind == "layout":
            for it in flat(target):
                item_probs[it] += bw
    for (ikind, iid), prob in sorted(item_probs.items(), key=lambda kv: (-kv[1], kv[0])):
        zone_rows.append([zname, ikind, iid, item_label(ikind, iid), round(100 * prob, 2)])

with (OUT / "crate_zone_odds.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["zone_type", "item_type", "item_id", "item_name", "chance_per_crate_pct"])
    w.writerows(zone_rows)

print("names:", len(name), "pool rows:", len(pool_rows), "zone rows:", len(zone_rows))
