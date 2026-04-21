#!/usr/bin/env python3
"""
split_history.py
Splits firm_history.json and director_history.json into chunks < 95 MB each
so they can be committed to GitHub (100 MB per-file hard limit).

Output files:  firm_history_1.json, firm_history_2.json, …
               director_history_1.json, director_history_2.json, …

The original files are NOT deleted — keep them locally, just add them to
.gitignore so only the chunked versions go into the repo.

Run from the project root:
    python demo/split_history.py
"""
import json, os, math

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAX_MB     = 90   # target ceiling per chunk (well below the 100 MB GitHub limit)

def split_file(filename):
    path = os.path.join(SCRIPT_DIR, filename)
    if not os.path.exists(path):
        print(f"  Not found, skipping: {filename}")
        return

    size_mb = os.path.getsize(path) / 1e6
    print(f"\nLoading {filename}  ({size_mb:.0f} MB) ...")
    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    base       = filename.replace('.json', '')
    max_bytes  = MAX_MB * 1_000_000
    chunk      = {}
    chunk_bytes = 2   # opening + closing brace
    chunk_idx  = 1

    print(f"  {len(data):,} entries  (splitting by byte size, target <= {MAX_MB} MB per chunk)")

    for key, val in data.items():
        entry_bytes = len(f',"{key}":'.encode()) + len(json.dumps(val, ensure_ascii=False).encode())
        if chunk and chunk_bytes + entry_bytes > max_bytes:
            out = os.path.join(SCRIPT_DIR, f'{base}_{chunk_idx}.json')
            with open(out, 'w', encoding='utf-8') as f:
                json.dump(chunk, f, ensure_ascii=False)
            mb = os.path.getsize(out) / 1e6
            print(f"  -> {base}_{chunk_idx}.json  ({mb:.1f} MB,  {len(chunk):,} entries)")
            chunk_idx  += 1
            chunk       = {}
            chunk_bytes = 2
        chunk[key]   = val
        chunk_bytes += entry_bytes

    if chunk:
        out = os.path.join(SCRIPT_DIR, f'{base}_{chunk_idx}.json')
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(chunk, f, ensure_ascii=False)
        mb = os.path.getsize(out) / 1e6
        print(f"  -> {base}_{chunk_idx}.json  ({mb:.1f} MB,  {len(chunk):,} entries)")

    print(f"  Done.")

split_file('firm_history.json')
split_file('director_history.json')

print("\nAll done.")
print("Add the *_N.json chunks to your repo.")
print("Add firm_history.json and director_history.json to .gitignore.")
