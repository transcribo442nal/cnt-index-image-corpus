#!/usr/bin/env python3
from pathlib import Path
import csv
import re

INP = Path("index_refs_grouped.tsv")
OUT = Path("index_refs_norm.tsv")

RE_INT = re.compile(r"^\d+$")
RE_NUMPAIR = re.compile(r"^(\d+),(\d+)$")
RE_SIGLA = re.compile(r"^[A-Za-z]\.?$")
RE_MARK = re.compile(r"^[\^°\*]+$")
RE_RANGE_START = re.compile(r"^(\d+)-$")

def main() -> int:
    if not INP.exists():
        raise SystemExit(f"Missing {INP}")

    with INP.open("r", encoding="utf-8") as f, OUT.open("w", encoding="utf-8") as g:
        r = csv.DictReader(f, delimiter="\t")
        fieldnames = [
            "cnt_idx","ref_no","ref_norm","ref_type",
            "sigla_prefix","marks","attach_prev",
            "source_column","line_no","group_no"
        ]
        w = csv.DictWriter(g, delimiter="\t", fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()

        cur_idx = None
        ref_no = 0
        prev_was_ref = False

        out_count = 0

        for row in r:
            idx = row["cnt_idx"]
            group_no = row["group_no"]
            toks = row["group_tokens"].split()
            src = row["source_column"]
            ln = row["line_no"]

            if idx != cur_idx:
                cur_idx = idx
                ref_no = 0
                prev_was_ref = False

            def emit(ref_norm, ref_type, sigla_prefix="", marks="", attach_prev="0"):
                nonlocal ref_no, out_count, prev_was_ref
                ref_no += 1
                w.writerow({
                    "cnt_idx": idx,
                    "ref_no": str(ref_no),
                    "ref_norm": ref_norm,
                    "ref_type": ref_type,
                    "sigla_prefix": sigla_prefix,
                    "marks": marks,
                    "attach_prev": attach_prev,
                    "source_column": src,
                    "line_no": ln,
                    "group_no": group_no,
                })
                out_count += 1
                prev_was_ref = (ref_type in ["REF","RANGE_START"])

            # Case: SIGLA only (e.g., v.)
            if len(toks) == 1 and RE_SIGLA.match(toks[0]):
                emit(toks[0], "SIGLA_ONLY", attach_prev="1" if prev_was_ref else "0")
                continue

            # Case: RANGE_START like 5-
            if len(toks) == 1 and RE_RANGE_START.match(toks[0]):
                n = RE_RANGE_START.match(toks[0]).group(1)
                emit(n, "RANGE_START")
                continue

            # Peel trailing marks
            marks = []
            while toks and RE_MARK.match(toks[-1]):
                marks.insert(0, toks.pop())

            # Peel leading sigla prefixes (often 1 letter)
            sigla = []
            while toks and RE_SIGLA.match(toks[0]):
                sigla.append(toks.pop(0))

            # Now normalize numeric core
            if len(toks) == 1 and RE_NUMPAIR.match(toks[0]):
                emit(toks[0], "REF", sigla_prefix=" ".join(sigla), marks=" ".join(marks))
                continue

            if len(toks) == 2 and RE_INT.match(toks[0]) and RE_INT.match(toks[1]):
                emit(f"{toks[0]},{toks[1]}", "REF", sigla_prefix=" ".join(sigla), marks=" ".join(marks))
                continue

            if len(toks) == 1 and RE_INT.match(toks[0]):
                emit(toks[0], "REF", sigla_prefix=" ".join(sigla), marks=" ".join(marks))
                continue

            # Fallback: preserve group tokens as OTHER
            emit(" ".join(sigla + toks + marks), "OTHER", sigla_prefix=" ".join(sigla), marks=" ".join(marks))

        print(f"OK: wrote {OUT} with {out_count} normalized refs")
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
