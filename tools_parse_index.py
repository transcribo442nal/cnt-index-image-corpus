#!/usr/bin/env python3
import glob
import os
import re
from pathlib import Path

SRC_DIR = Path("ocr_clean")
OUT_ROWS = Path("index_rows.tsv")
OUT_REJ = Path("parse_rejects.tsv")

# Match: lemma + whitespace + refs starting with a digit
# Lemma allows Latin letters incl. ligatures and common punctuation.
ENTRY_RE = re.compile(
    r"^([A-Za-zÆŒæœ][A-Za-zÆŒæœ'’\-\.\(\) ]*?)\s+(\d.*)$"
)

# Simple header/section lines we ignore
HEADER_RE = re.compile(r"^(?:[A-Z]\.|[IVXLCDM]+\.)$")

def norm_space(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())

def main() -> int:
    files = sorted(glob.glob(str(SRC_DIR / "*.txt")))
    if not files:
        raise SystemExit(f"No files found in {SRC_DIR}/")

    rows = 0
    rej = 0

    with OUT_ROWS.open("w", encoding="utf-8") as fw, OUT_REJ.open("w", encoding="utf-8") as fr:
        fw.write("lemma\trefs_raw\tsource_column\tline_no\n")
        fr.write("source_column\tline_no\treason\tline\n")

        for fpath in files:
            source = Path(fpath).stem  # p001-c01
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                for i, line in enumerate(f, start=1):
                    raw = line.rstrip("\n")
                    s = raw.strip()

                    if not s:
                        continue
                    if HEADER_RE.match(s):
                        continue
                    # Skip obvious non-entry banners if they appear
                    if s.upper().startswith(("INDEX", "ALPHABET", "ALPHABETIC", "TIRON", "TIRONIAN")):
                        continue

                    m = ENTRY_RE.match(s)
                    if m:
                        lemma = norm_space(m.group(1))
                        refs = norm_space(m.group(2))
                        fw.write(f"{lemma}\t{refs}\t{source}\t{i}\n")
                        rows += 1
                    else:
                        fr.write(f"{source}\t{i}\tNO_MATCH\t{s}\n")
                        rej += 1

    print(f"OK: wrote {OUT_ROWS} with {rows} rows")
    print(f"OK: wrote {OUT_REJ} with {rej} rejects")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
