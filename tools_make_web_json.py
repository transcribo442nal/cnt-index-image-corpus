#!/usr/bin/env python3
from pathlib import Path
import csv, json

ROWS = Path("index_rows_id.tsv")
REFS = Path("index_refs_norm.tsv")

OUTDIR = Path("docs")
OUTDIR.mkdir(exist_ok=True)

def main():
    # index rows
    rows = []
    with ROWS.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            rows.append({
                "cnt_idx": row["cnt_idx"],
                "lemma_key": row["lemma_key"],
                "lemma": row["lemma"],
                "refs_raw": row["refs_raw"],
                "src": row["source_column"],
                "line": int(row["line_no"]),
            })

    # refs
    refs = []
    with REFS.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        for x in r:
            refs.append({
                "cnt_idx": x["cnt_idx"],
                "ref_no": int(x["ref_no"]),
                "ref_norm": x["ref_norm"],
                "ref_type": x["ref_type"],
                "sigla": x.get("sigla_prefix","").strip(),
                "marks": x.get("marks","").strip(),
                "attach_prev": int(x.get("attach_prev","0")),
                "src": x["source_column"],
                "line": int(x["line_no"]),
                "group_no": int(x["group_no"]),
            })

    (OUTDIR / "data_index.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    (OUTDIR / "data_refs.json").write_text(json.dumps(refs, ensure_ascii=False), encoding="utf-8")

    print("OK: wrote docs/data_index.json and docs/data_refs.json")

if __name__ == "__main__":
    main()
