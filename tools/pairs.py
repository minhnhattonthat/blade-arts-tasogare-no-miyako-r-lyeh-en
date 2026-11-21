"""Reviewer pairs file for translated batches (docs/reviewer-brief.md).

    python -X utf8 tools/pairs.py b002 [b003 ...]   -> work/qa/review/<batch>.pairs.txt

Each entry: `>> id | form limit | JP` then `EN`, in batch (script) order, so neighbours are the context.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TL = ROOT / "work/tl"
OUT = ROOT / "work/qa/review"


def pairs(batch):
    src = [line.split("\t") for line in (TL / f"{batch}.tsv").read_text(encoding="utf-8").splitlines() if line]
    out = dict(line.split("\t", 1) for line in (TL / f"{batch}.out.tsv").read_text(encoding="utf-8").splitlines() if line)
    return "".join(f">> {r[0]} | {r[2]} {r[3]} | {r[4]}\n   {out.get(r[0], '(missing)')}\n\n" for r in src)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for b in sys.argv[1:]:
        (OUT / f"{b}.pairs.txt").write_text(pairs(b), encoding="utf-8", newline="\n")
        print(OUT / f"{b}.pairs.txt")
