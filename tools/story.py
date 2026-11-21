"""Story-pass chapter files (references/translation.md §Review, story pass).

    python -X utf8 tools/story.py   -> work/qa/story/chapters/chNN_<first>-<last>.txt

SOL blocks in id order (docs/synopsis.md §Order), split into chapters by block range. Each entry is
`>> id | JP` then `   EN`, control codes stripped, `\\` -> ` / `, `@@` -> ` // ` (page break). A (JP, EN) pair
already shown earlier is written as `>> id = <first id>` so duplicated blocks don't need a second read; the same
JP with a different EN is written in full (a consistency check).
Regenerate after every script edit, then `qa_gate.py init work/qa/story/manifest.tsv work/qa/story/chapters --glob "*.txt"`.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "work/qa/story/chapters"
CHAPTERS = [(1, 20), (21, 50), (51, 80), (81, 124), (125, 146), (147, 176)]
CODE_EN = re.compile(r"\{[^}]*\}")
CODE_JP = re.compile(r"\{[^}]*\}|[A-Za-z0-9\[\]]*[0-9][A-Za-z0-9\[\]]*")  # ASCII only: fullwidth digits are text


def show(text, code):
    return code.sub("", text).replace("@@", " // ").replace("\\\\", " / ").replace("\\", " / ").strip(" /")


def rows():
    for f in sorted((ROOT / "script/sol").glob("*.tsv")):
        for line in f.read_text(encoding="utf-8").splitlines()[1:]:
            if line:
                r = line.split("\t")
                yield int(f.stem), r[0], r[2], r[3]


def chapters():
    seen, out = {}, {c: [] for c in CHAPTERS}
    for block, sid, jp, en in rows():
        ch = next(c for c in CHAPTERS if c[0] <= block <= c[1])
        if (jp, en) in seen:
            out[ch].append(f">> {sid} = {seen[jp, en]}\n")
        else:
            seen[jp, en] = sid
            out[ch].append(f">> {sid} | {show(jp, CODE_JP)}\n   {show(en, CODE_EN)}\n")
    return {f"ch{i + 1:02}_{a:03}-{b:03}.txt": "".join(out[(a, b)]) for i, (a, b) in enumerate(CHAPTERS)}


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, text in chapters().items():
        assert text, name
        (OUT / name).write_text(text, encoding="utf-8", newline="\n")
        print(OUT / name, len(text))
