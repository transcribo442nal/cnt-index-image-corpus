#!/usr/bin/env python3
import glob
import re
from pathlib import Path

SRC_DIR = Path("ocr_clean")
OUT_ROWS = Path("index_rows_stitched.tsv")
OUT_REJ = Path("parse_rejects_stitched.tsv")

ENTRY_RE = re.compile(r"^([A-Za-zÆŒæœ][A-Za-zÆŒæœ'’\-\.\(\) ]*?)\s+(\d.*)$")
HEADER_RE = re.compile(r"^(?:[A-Z]\.|[IVXLCDM]+\.)$")

def norm_space(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())

def is_refs_only(line: str) -> bool:
    return bool(re.match(r"^\d", line))

def is_lemma_tail(line: str) -> bool:
    # Small tail fragments like "bacue" or broken endings. Conservative.
    return bool(re.match(r"^[A-Za-zÆŒæœ]{2,12}$", line))

def main() -> int:
    files = sorted(glob.glob(str(SRC_DIR / "*.txt")))
    if not files:
        raise SystemExit(f"No files found in {SRC_DIR}/")

    rows = []
    rejects = []

    # Track last accepted row for stitching
    last = None  # dict with lemma/refs/source/line_no

    for fpath in files:
        source = Path(fpath).stem
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            for ln, raw in enumerate(f, start=1):
                s = raw.strip()
                if not s:
                    continue
                if HEADER_RE.match(s):
                    continue
                if s.upper().startswith(("INDEX", "ALPHABET", "ALPHABETIC", "TIRON", "TIRONIAN")):
                    continue

                # Clean mid-line pipes that survived
                s = norm_space(s.replace("|", " "))

                m = ENTRY_RE.match(s)
                if m:
                    last = {
                        "lemma": norm_space(m.group(1)),
                        "refs":  norm_space(m.group(2)),
                        "source": source,
                        "line_no": ln,
                    }
                    rows.append(last)
                    continue

                # Stitch refs-only lines onto previous row
                if last and is_refs_only(s):
                    last["refs"] = norm_space(last["refs"] + " " + s)
                    continue

                # Stitch lemma tail fragments (rare, conservative)
                if last and is_lemma_tail(s):
                    last["lemma"] = norm_space(last["lemma"] + s)
                    continue

                rejects.append((source, ln, "NO_MATCH", s))

    with OUT_ROWS.open("w", encoding="utf-8") as fw:
        fw.write("lemma\trefs_raw\tsource_column\tline_no\n")
        for r in rows:
            fw.write(f"{r['lemma']}\t{r['refs']}\t{r['source']}\t{r['line_no']}\n")

    with OUT_REJ.open("w", encoding="utf-8") as fr:
        fr.write("source_column\tline_no\treason\tline\n")
        for source, ln, reason, s in rejects:
            fr.write(f"{source}\t{ln}\t{reason}\t{s}\n")

    print(f"OK: wrote {OUT_ROWS} with {len(rows)} rows")
    print(f"OK: wrote {OUT_REJ} with {len(rejects)} rejects")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
