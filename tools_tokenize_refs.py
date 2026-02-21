#!/usr/bin/env python3
from pathlib import Path
import re

INP = Path("index_rows_id.tsv")
OUT = Path("index_refs.tsv")

# Token patterns (ordered by "specificity")
RE_NUMPAIR = re.compile(r"^\d+,\d+$")          # 121,98
RE_NUM     = re.compile(r"^\d+$")              # 121
RE_SIGLA   = re.compile(r"^[A-Za-z]\.?$")      # v.  J  K.
RE_MARK    = re.compile(r"^[\^°\*]+$")         # ^  °  **

def kind(tok: str) -> str:
    if RE_NUMPAIR.match(tok): return "NUMPAIR"
    if RE_NUM.match(tok):     return "NUM"
    if RE_MARK.match(tok):    return "MARK"
    if RE_SIGLA.match(tok):   return "SIGLA"
    return "OTHER"

def normalize_refs(s: str) -> str:
    s = s.strip()
    # unify separators
    s = s.replace(";", " ; ")
    s = s.replace(",", ",")
    # detach common marks (keep them as tokens)
    s = s.replace("^", " ^ ")
    s = s.replace("°", " ° ")
    s = s.replace("*", " * ")
    # collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s

def split_tokens(s: str):
    # split on spaces, but keep ";" as its own token
    parts = s.split(" ")
    toks = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # drop empty punctuation-only noise except our explicit separator
        if p in [",", ".", ":"]:
            continue
        toks.append(p)
    return toks

def main() -> int:
    if not INP.exists():
        raise SystemExit(f"Missing input: {INP} (run v1.7 tools_add_cnt_idx.py first)")

    with INP.open("r", encoding="utf-8") as f, OUT.open("w", encoding="utf-8") as g:
        hdr = f.readline().rstrip("\n").split("\t")
        if hdr[:6] != ["cnt_idx","lemma_key","lemma","refs_raw","source_column","line_no"]:
            raise SystemExit("Unexpected header in index_rows_id.tsv")

        g.write("cnt_idx\tref_token\tref_kind\tsource_column\tline_no\n")

        n = 0
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < 6:
                continue
            cnt_idx, refs_raw, src, ln = parts[0], parts[3], parts[4], parts[5]

            refs_norm = normalize_refs(refs_raw)
            toks = split_tokens(refs_norm)

            for t in toks:
                # keep ';' as a structural separator token (useful later)
                if t == ";":
                    g.write(f"{cnt_idx}\t;\tSEP\t{src}\t{ln}\n")
                    n += 1
                    continue

                # strip trailing commas that OCR sometimes leaves dangling
                t2 = t.rstrip(",")
                if not t2:
                    continue

                g.write(f"{cnt_idx}\t{t2}\t{kind(t2)}\t{src}\t{ln}\n")
                n += 1

    print(f"OK: wrote {OUT} with {n} tokens")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
