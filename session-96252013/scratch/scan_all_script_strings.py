import os
import re
from collections import Counter

scripts_dir = r"C:\Users\<user>\Downloads\americas_scripts_23_11_2026"

def scan_all_scripts():
    all_strings = Counter()
    mission_strings = {}
    
    files = [f for f in os.listdir(scripts_dir) if f.endswith(".ysc.cs") and f != "shared.ysc.cs"]
    print(f"Total files to scan (excluding shared.ysc.cs): {len(files)}")
    
    # Patterns of interest:
    # 1. Mission names or titles
    # 2. Cutscene names, audio scenes, subtitles, speech
    # 3. Blip names, objective text
    # 4. Hash mappings
    
    for filename in files:
        filepath = os.path.join(scripts_dir, filename)
        file_strings = set()
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                # check string literals
                matches = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', line)
                for s in matches:
                    if len(s) >= 4 and not s.startswith("type_") and not s.startswith("box<") and not s.startswith("try_cast<") and not "System." in s and not "InvalidOperationException" in s:
                        file_strings.add(s)
        if file_strings:
            mission_strings[filename] = file_strings
            for s in file_strings:
                all_strings[s] += 1
                
    print(f"Files with strings: {len(mission_strings)}")
    print(f"Total unique strings found: {len(all_strings)}")
    
    # Print the most interesting strings (strings with letters and spaces or underscores, or looking like mission names)
    interesting = []
    for s, count in all_strings.items():
        if re.search(r'[A-Za-z]', s):
            interesting.append((s, count))
            
    interesting.sort(key=lambda x: x[0].lower())
    print("\nSample unique strings found in scripts (first 100):")
    for s, c in interesting[:100]:
        print(f"  [{c} files] {s}")
        
    # Write all interesting strings to a file in scratch
    out_path = r"C:\Users\<user>\.gemini\antigravity-cli\brain\96252013-4633-45e8-b6a2-59b18be9e68c\scratch\decompiled_script_strings.txt"
    with open(out_path, "w", encoding="utf-8") as out:
        for s, c in interesting:
            out.write(f"{c}\t{s}\n")
    print(f"\nWritten {len(interesting)} strings to {out_path}")

if __name__ == "__main__":
    scan_all_scripts()
