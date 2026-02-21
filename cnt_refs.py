#!/usr/bin/env python3
from pathlib import Path
import csv
import sys

ROWS = Path("index_rows_id.tsv")
REFS = Path("index_refs_norm.tsv")

def load_row(cnt_idx: str):
    with ROWS.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            if row["cnt_idx"] == cnt_idx:
                return row
    return None

def load_refs(cnt_idx: str):
    out = []
    with REFS.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            if row["cnt_idx"] != cnt_idx:
                continue
            out.append(row)
    # already in order in file, but be safe:
    out.sort(key=lambda x: int(x["ref_no"]))
    return out

def fmt_ref(r):
    # REF / RANGE_START / SIGLA_ONLY / OTHER
    t = r["ref_type"]
    sig = (r.get("sigla_prefix") or "").strip()
    marks = (r.get("marks") or "").strip()
    core = (r.get("ref_norm") or "").strip()

    if t == "SIGLA_ONLY":
        return core
    if t == "RANGE_START":
        s = f"{core}-"
    else:
        s = core

    if sig:
        s = f"{sig} {s}"
    if marks:
        s = f"{s} {marks}"
    return s.strip()

def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: ./cnt_refs.py CNT-IDX-0000123", file=sys.stderr)
        return 2

    cnt_idx = sys.argv[1].strip()

    if not ROWS.exists() or not REFS.exists():
        print("Missing required TSVs. Need index_rows_id.tsv and index_refs_norm.tsv", file=sys.stderr)
        return 2

    row = load_row(cnt_idx)
    if not row:
        print(f"Not found: {cnt_idx}", file=sys.stderr)
        return 1

    refs = load_refs(cnt_idx)

    print(f"{cnt_idx}")
    print(f"lemma_key: {row['lemma_key']}")
    print(f"lemma:     {row['lemma']}")
    print(f"refs_raw:  {row['refs_raw']}")
    print(f"source:    {row['source_column']}:{row['line_no']}")
    print("")
    print("refs_norm:")
    for r in refs:
        print(f"  - {fmt_ref(r)}    ({r['source_column']}:{r['line_no']} g{r['group_no']} r{r['ref_no']})")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
