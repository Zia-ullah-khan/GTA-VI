import json
import os

FLOW_DIR = r"C:\Users\<user>\Downloads\GTA6.Xbox.v1.0.2.1-CYBERLEEK\work\flow"

with open(os.path.join(FLOW_DIR, "tree_3e2372000.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

print("Blocks in tree_3e2372000.json:")
for b in data["blocks"]:
    rows = b.get("rows", [])
    sample = json.dumps(rows[0])[:100] if rows else ""
    print(f"  Blk #{b['number']:3d} kind={b['kind']} rows={len(rows):5d} sample={sample}")

blk90 = next(b for b in data["blocks"] if b["number"] == 90)["rows"]
print("\n=== blk90 entries matching Chapter 1 IDs ===")
ch1_keys = [
    "62131f35", "03da4607", "cc31ef42", "5cb7db5c", "ab5b5242",
    "349c946f", "d244cb70", "e48c934a", "2d7d2164", "5ae70594",
    "c8513199", "21d03e4f", "2f494854", "97628e9f", "07560abe",
    "fab575e7", "bdcb784e", "5adb2543", "dfa7f6e3"
]
for i, row in enumerate(blk90):
    s = json.dumps(row)
    hits = [k for k in ch1_keys if k in s]
    if hits:
        print(f"  blk90[{i}] b53667be={row.get('b53667be')} b69b0f02={row.get('b69b0f02')} hits={hits}")
