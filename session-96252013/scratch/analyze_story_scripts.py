import os
import re

scripts_dir = r"C:\Users\<user>\Downloads\americas_scripts_23_11_2026"

def analyze_story_strings():
    story_file = os.path.join(scripts_dir, "story000.ysc.cs")
    strings_found = set()
    native_calls = set()
    
    with open(story_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            # find string literals
            for m in re.finditer(r'"([^"\\]*(?:\\.[^"\\]*)*)"', line):
                val = m.group(1)
                if len(val) >= 3 and not val.startswith("type_"):
                    strings_found.add(val)
            # find Native calls
            for m in re.finditer(r'Native\.([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)', line):
                native_calls.add(f"{m.group(1)}.{m.group(2)}")
                
    print(f"story000 strings count: {len(strings_found)}")
    print("Sample strings:")
    for s in sorted(list(strings_found))[:50]:
        print("  ", s)
        
    print(f"\nstory000 native calls count: {len(native_calls)}")
    print("Sample native calls:")
    for n in sorted(list(native_calls))[:50]:
        print("  ", n)

if __name__ == "__main__":
    analyze_story_strings()
