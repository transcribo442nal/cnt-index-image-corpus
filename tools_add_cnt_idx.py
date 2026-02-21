#!/usr/bin/env python3
from pathlib import Path

INP = Path("index_rows_keyed.tsv")
OUT = Path("index_rows_id.tsv")

def main() -> int:
    if not INP.exists():
        raise SystemExit(f"Missing input: {INP}")

    with INP.open("r", encoding="utf-8") as f, OUT.open("w", encoding="utf-8") as g:
        header = f.readline().rstrip("\n").split("\t")
        if header[:5] != ["lemma_key", "lemma", "refs_raw", "source_column", "line_no"]:
            raise SystemExit("Unexpected header in index_rows_keyed.tsv")

        g.write("cnt_idx\tlemma_key\tlemma\trefs_raw\tsource_column\tline_no\n")

        n = 0
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < 5:
                continue
            n += 1
            cnt_idx = f"CNT-IDX-{n:07d}"
            g.write(cnt_idx + "\t" + "\t".join(parts[:5]) + "\n")

    print(f"OK: wrote {OUT} with {n} rows")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
