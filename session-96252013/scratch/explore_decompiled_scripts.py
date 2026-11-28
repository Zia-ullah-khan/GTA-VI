import os
import re

SCRIPTS_DIR = r"C:\Users\<user>\Downloads\americas_scripts_23_11_2026"

def run_exploration():
    files = [f for f in os.listdir(SCRIPTS_DIR) if f.endswith(".cs")]
    named_files = [f for f in files if not f.startswith("0x")]
    hash_files = [f for f in files if f.startswith("0x")]
    
    print(f"Total .cs files: {len(files)}")
    print(f"Named .cs files ({len(named_files)}):")
    for nf in sorted(named_files):
        sz = os.path.getsize(os.path.join(SCRIPTS_DIR, nf))
        print(f"  {nf} ({sz:,} bytes)")
        
    print(f"\nHash-named files: {len(hash_files)}")
    
    # Check for string literals across named files (excluding shared.ysc.cs to keep it fast)
    print("\nScanning named files for string literals and interesting identifiers...")
    interesting_terms = ["mission", "heist", "jason", "lucia", "donnie", "brian", "cal", "stage", "chapter", "objective"]
    
    hits = {}
    for nf in named_files:
        if nf == "shared.ysc.cs":
            continue
        p = os.path.join(SCRIPTS_DIR, nf)
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            for idx, line in enumerate(f):
                line_lower = line.lower()
                for term in interesting_terms:
                    if term in line_lower:
                        if term not in hits:
                            hits[term] = []
                        if len(hits[term]) < 5:
                            hits[term].append(f"{nf}:{idx+1}: {line.strip()[:100]}")
                            
    for term, lines in hits.items():
        print(f"\n=== Hits for '{term}' ===")
        for l in lines:
            print(f"  {l}")

if __name__ == "__main__":
    run_exploration()
