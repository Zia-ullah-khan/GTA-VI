"""Evidence for crate pickup odds.

1. Map each 64-bit prop ID in the decoded layout tree to a prop name by matching item positions
   against the names in container_crates.ymt.pso.xml (same layout, same position to 3 dp).
2. Flatten nested layout references and count, per theme pool, how many layouts contain each prop.
"""
import json, re, sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path("C:/Users/khans/Downloads")
TREE = ROOT / "GTA6-RE/work/containers/tree_1be4f000.json"
XML = ROOT / "GTA6.Xbox.v1.0.2.1-CYBERLEEK/container_crates.ymt.pso.xml"

# 1. names from the XML, keyed by layout hash and position
xml = Path("C:/Users/khans/Downloads/container_crates.ymt.pso.xml").read_text(encoding="utf-8", errors="ignore")
xmlprops = defaultdict(list)
for b in re.split(r'<Item type="PpdPDFA_0x6A7B2BC2">', xml)[1:]:
    m = re.search(r"<Name>([^<]*)</Name>", b)
    if not m:
        continue
    lay = m.group(1).split("_0x")[-1].lower()
    for it in re.finditer(r'<Item type="PwAYfDA_0xF42933B2">(.*?)</Item>', b, re.S):
        body = it.group(1)
        pm = re.search(r'<Position x="([^"]+)" y="([^"]+)" z="([^"]+)"', body)
        nm = re.search(r"<Prop>([^<]+)</Prop>", body)
        if pm and nm:
            pos = tuple(round(float(pm.group(i)), 3) for i in (1, 2, 3))
            xmlprops[lay].append((pos, nm.group(1)))

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
print("prop IDs named:", len(name), " with more than one name:", sum(len(v) > 1 for v in name.values()))
for key in ["b18cab8f33691f96", "ae37b2e124637e83", "66440646e4b7db41", "610992765c5c3f44", "b1dbbdcb99195042"]:
    print(f"  {key} -> {sorted(name.get(key, ['?']))}")

# 2. flatten layouts and count per pool
def flat(n, seen=frozenset()):
    if n in seen or n not in lay:
        return set()
    seen = seen | {n}
    out = set()
    for it in lay[n].get("9a18c89f", []):
        c = it.get("0e3117bd", {})
        if c.get("type") == "57d66554":
            out.add(c["2257ebb9"])
        elif c.get("type") == "1b790739":
            out |= flat(c["7efea5a0"], seen)
    return out

print("\npool sizes and named-pool checks (layout lists from the pasted report):")
REPORT = {"industrial": {"3663121a", "454460f3", "8a926675", "e723bc48", "e0be1036", "6bed5953", "d01e32bc"},
          "medical": {"c034dc35", "940d83e7"},
          "farm": {"0b8c5221", "56952ed0", "f0767425", "a743cfc3", "1808aaa3", "ea7ae4c8"}}
pools = B[2]["rows"]
for i, p in enumerate(pools):
    ls = p["c19c0de4"]
    match = [k for k, v in REPORT.items() if set(ls) == v]
    print(f"  pool{i:02d}: {len(ls)} layouts  matches report pool: {match or '-'}")
for who in ["8a926675", "e723bc48"]:
    print(f"\nlayout {who} contains molotov:", "b18cab8f33691f96" in flat(who))
print("pool05 molotov count:", sum("b18cab8f33691f96" in flat(l) for l in pools[5]["c19c0de4"]), "of", len(pools[5]["c19c0de4"]))
