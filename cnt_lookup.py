#!/usr/bin/env python3
import sys
import re
from pathlib import Path

TSV = Path("index_rows_keyed.tsv")

def norm_key(q: str) -> str:
    q = q.strip().lower()
    q = q.replace("æ", "ae").replace("œ", "oe")
    q = q.replace("’", "").replace("'", "")
    q = re.sub(r"[^a-z0-9]+", " ", q)
    q = re.sub(r"\s+", " ", q).strip()
    return q

def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: ./cnt_lookup.py <lemma or prefix> [--prefix]", file=sys.stderr)
        return 2

    q = " ".join(a for a in sys.argv[1:] if a != "--prefix")
    prefix_mode = "--prefix" in sys.argv[1:]

    key = norm_key(q)
    if not key:
        print("Empty query after normalization.", file=sys.stderr)
        return 2

    if not TSV.exists():
        print(f"Missing {TSV}. Run tools_add_lemma_key.py first.", file=sys.stderr)
        return 2

    hits = 0
    with TSV.open("r", encoding="utf-8") as f:
        header = f.readline()
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 5:
                continue
            lemma_key, lemma, refs, src, ln = parts[0], parts[1], parts[2], parts[3], parts[4]

            ok = lemma_key.startswith(key) if prefix_mode else (lemma_key == key)
            if ok:
                hits += 1
                print(f"{lemma}\t{refs}\t({src}:{ln})")

    if hits == 0:
        mode = "prefix" if prefix_mode else "exact"
        print(f"No {mode} matches for: {q}  [key={key}]", file=sys.stderr)
        return 1

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
