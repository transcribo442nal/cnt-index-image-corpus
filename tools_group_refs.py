#!/usr/bin/env python3
from pathlib import Path
import csv

INP = Path("index_refs.tsv")
OUT = Path("index_refs_grouped.tsv")

def main() -> int:
    if not INP.exists():
        raise SystemExit(f"Missing {INP}")

    rows_out = 0
    with INP.open("r", encoding="utf-8") as f, OUT.open("w", encoding="utf-8") as g:
        r = csv.DictReader(f, delimiter="\t")
        fieldnames = ["cnt_idx","group_no","group_tokens","source_column","line_no"]
        w = csv.DictWriter(g, delimiter="\t", fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()

        cur_idx = None
        cur_src = None
        cur_ln = None
        group_no = 0
        buf = []

        def flush():
            nonlocal rows_out, buf, group_no
            if cur_idx is None:
                return
            if not buf:
                return
            group_no += 1
            w.writerow({
                "cnt_idx": cur_idx,
                "group_no": str(group_no),
                "group_tokens": " ".join(buf),
                "source_column": cur_src,
                "line_no": cur_ln,
            })
            rows_out += 1
            buf = []

        for row in r:
            idx = row["cnt_idx"]
            tok = row["ref_token"]
            src = row["source_column"]
            ln  = row["line_no"]

            if cur_idx != idx:
                # new entry: flush previous
                flush()
                cur_idx = idx
                cur_src = src
                cur_ln = ln
                group_no = 0
                buf = []

            if tok == ";":
                flush()
                continue

            buf.append(tok)

        flush()

    print(f"OK: wrote {OUT} with {rows_out} groups")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
