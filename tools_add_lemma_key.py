#!/usr/bin/env python3
from pathlib import Path
import re

INP = Path("index_rows_stitched.tsv")
OUT = Path("index_rows_keyed.tsv")

def lemma_key(s: str) -> str:
    s = s.strip().lower()
    # normalize ligatures
    s = s.replace("æ", "ae").replace("œ", "oe")
    # normalize quotes/apostrophes
    s = s.replace("’", "").replace("'", "")
    # keep alnum, turn everything else into space
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def main() -> int:
    if not INP.exists():
        raise SystemExit(f"Missing input: {INP}")

    with INP.open("r", encoding="utf-8") as f, OUT.open("w", encoding="utf-8") as g:
        header = f.readline().rstrip("\n")
        cols = header.split("\t")
        # Expect: lemma, refs_raw, source_column, line_no
        if cols[:4] != ["lemma", "refs_raw", "source_column", "line_no"]:
            raise SystemExit(f"Unexpected header in {INP}: {header}")

        g.write("lemma_key\tlemma\trefs_raw\tsource_column\tline_no\n")

        n = 0
        empty = 0
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < 4:
                continue
            lemma, refs, src, ln = parts[0], parts[1], parts[2], parts[3]
            key = lemma_key(lemma)
            if not key:
                empty += 1
                # still emit for auditability
                key = "__EMPTY__"
            g.write(f"{key}\t{lemma}\t{refs}\t{src}\t{ln}\n")
            n += 1

    print(f"OK: wrote {OUT} with {n} rows ({empty} empty keys)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
