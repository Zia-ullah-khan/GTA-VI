import json
import re

chart_path = r"C:\Users\<user>\.gemini\antigravity-cli\brain\96252013-4633-45e8-b6a2-59b18be9e68c\gta6_mission_flow_chart.md"
order_path = r"C:\Users\<user>\Downloads\GTA6.Xbox.v1.0.2.1-CYBERLEEK\output\mission_order.json"

with open(chart_path, "r", encoding="utf-8") as f:
    text = f.read()

with open(order_path, "r", encoding="utf-8") as f:
    order_doc = json.load(f)

# Extract table lines in section 7
table_matches = re.findall(r"\|\s*\*\*Ch\.\s*(\d+)\*\*\s*\|\s*\*\*(\d+)\.\s*([^*|]+?)\*\*\s*\|", text)
print(f"Table matches found in Section 7: {len(table_matches)}")
table_titles = {}
for ch, num, name in table_matches:
    table_titles[int(num)] = name.strip()

for k in sorted(table_titles.keys())[:30]:
    print(f"  {k:2d}: {table_titles[k]}")

# Also find in mermaid nodes like M01["1. Prologue..."], M23["23. What's in the Bag?..."]
node_matches = re.findall(r'\[\"(\d+)\.\s+([^<\"\n]+)', text)
print(f"\nNode matches found: {len(node_matches)}")
node_titles = {}
for num, name in node_matches:
    n = int(num)
    if n not in node_titles:
        node_titles[n] = name.strip()

for k in sorted(node_titles.keys())[:30]:
    print(f"  {k:2d}: {node_titles[k]}")
