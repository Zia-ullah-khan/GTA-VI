import os
import re
import json
import shutil

base_dir = r"C:\Users\<user>\Downloads\GTA6.Xbox.v1.0.2.1-CYBERLEEK"
output_dir = os.path.join(base_dir, "output")
downloads_dir = r"C:\Users\<user>\Downloads"
scratch_dir = os.path.join(base_dir, "scratch")

# 1. Reconstruct Claude's original SPEEDRUN_ROUTING_NOTES.md
part1_path = os.path.join(scratch_dir, "claude_SPEEDRUN_ROUTING_NOTES_part1.txt")
part2_path = os.path.join(scratch_dir, "claude_SPEEDRUN_ROUTING_NOTES_part2.txt")

with open(part1_path, "r", encoding="utf-8") as f:
    text1 = f.read()

with open(part2_path, "r", encoding="utf-8") as f:
    text2 = f.read()

# Extract lines from view_file format "line_num: <original_line>"
def clean_view_lines(text):
    lines = []
    for line in text.splitlines():
        m = re.match(r"^\s*\d+:\s?(.*)$", line)
        if m:
            lines.append(m.group(1))
    return lines

p1_lines = clean_view_lines(text1)
p2_lines = clean_view_lines(text2)

claude_notes_lines = p1_lines[:150] + p2_lines
claude_notes_text = "\n".join(claude_notes_lines) + "\n"

# Verify Claude's files in scratch/claude_final
claude_order_path = os.path.join(scratch_dir, "claude_final", "mission_order.json")
claude_flow_path = os.path.join(scratch_dir, "claude_final", "mission_flow.mmd")

# Create Claude version directory
claude_dir_out = os.path.join(output_dir, "claude_version")
claude_dir_down = os.path.join(downloads_dir, "claude_version")
os.makedirs(claude_dir_out, exist_ok=True)
os.makedirs(claude_dir_down, exist_ok=True)

# Copy/write Claude version files
shutil.copyfile(claude_order_path, os.path.join(claude_dir_out, "mission_order.json"))
shutil.copyfile(claude_flow_path, os.path.join(claude_dir_out, "mission_flow.mmd"))
with open(os.path.join(claude_dir_out, "SPEEDRUN_ROUTING_NOTES.md"), "w", encoding="utf-8") as f:
    f.write(claude_notes_text)

shutil.copyfile(claude_order_path, os.path.join(claude_dir_down, "mission_order.json"))
shutil.copyfile(claude_flow_path, os.path.join(claude_dir_down, "mission_flow.mmd"))
with open(os.path.join(claude_dir_down, "SPEEDRUN_ROUTING_NOTES.md"), "w", encoding="utf-8") as f:
    f.write(claude_notes_text)

# Also restore Claude's original files as the base files in output/
shutil.copyfile(claude_order_path, os.path.join(output_dir, "mission_order.json"))
shutil.copyfile(claude_flow_path, os.path.join(output_dir, "mission_flow.mmd"))
with open(os.path.join(output_dir, "SPEEDRUN_ROUTING_NOTES.md"), "w", encoding="utf-8") as f:
    f.write(claude_notes_text)

# Also restore Claude's original files in Downloads base
shutil.copyfile(claude_order_path, os.path.join(downloads_dir, "mission_order.json"))
shutil.copyfile(claude_flow_path, os.path.join(downloads_dir, "mission_flow.mmd"))
with open(os.path.join(downloads_dir, "SPEEDRUN_ROUTING_NOTES.md"), "w", encoding="utf-8") as f:
    f.write(claude_notes_text)

print("Claude's original version restored and saved to claude_version/ and output/.")

# 2. Now create Antigravity version files
antigravity_dir_out = os.path.join(output_dir, "antigravity_version")
antigravity_dir_down = os.path.join(downloads_dir, "antigravity_version")
os.makedirs(antigravity_dir_out, exist_ok=True)
os.makedirs(antigravity_dir_down, exist_ok=True)

# Generate our Antigravity files using our previous generators into antigravity_version/
# and root output/ as _antigravity files
