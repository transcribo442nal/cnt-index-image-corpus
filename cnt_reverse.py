#!/usr/bin/env python3
from pathlib import Path
import csv
import sys

ROWS = Path("index_rows_id.tsv")
REFS = Path("index_refs_norm.tsv")

def load_rows():
    m = {}
    with ROWS.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            m[row["cnt_idx"]] = row
    return m

def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: ./cnt_reverse.py 121,98", file=sys.stderr)
        print("   or: ./cnt_reverse.py 121,98 --all (include OTHER/SIGLA_ONLY)", file=sys.stderr)
        return 2

    target = sys.argv[1].strip()
    include_all = "--all" in sys.argv[2:]

    if not ROWS.exists() or not REFS.exists():
        print("Missing required TSVs. Need index_rows_id.tsv and index_refs_norm.tsv", file=sys.stderr)
        return 2

    rows = load_rows()

    hits = []
    with REFS.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        for ref in r:
            if (ref["ref_type"] in ["SIGLA_ONLY"] and not include_all):
                continue
            if (ref["ref_type"] == "OTHER" and not include_all):
                continue
            if ref["ref_norm"] == target:
                cnt_idx = ref["cnt_idx"]
                row = rows.get(cnt_idx)
                lemma = row["lemma"] if row else "<?>"
                lemma_key = row["lemma_key"] if row else "<?>"
                hits.append((lemma_key, lemma, cnt_idx, ref))

    hits.sort(key=lambda x: (x[0], x[2], int(x[3]["ref_no"])))

    if not hits:
        print(f"No hits for ref_norm={target}", file=sys.stderr)
        return 1

    print(f"ref_norm={target}  hits={len(hits)}")
    for lemma_key, lemma, cnt_idx, ref in hits:
        sig = (ref.get("sigla_prefix") or "").strip()
        marks = (ref.get("marks") or "").strip()
        extra = ""
        if sig: extra += f" sigla={sig}"
        if marks: extra += f" marks={marks}"
        print(f"{lemma_key}\t{lemma}\t{cnt_idx}\t({ref['source_column']}:{ref['line_no']} g{ref['group_no']} r{ref['ref_no']}){extra}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
