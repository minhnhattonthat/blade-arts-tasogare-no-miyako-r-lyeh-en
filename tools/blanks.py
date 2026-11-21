"""Restore the JP's leading/trailing blank (fullwidth space) in every en cell that dropped it (the lint rule in
batches.layout_problems). Leading: after the opening codes; trailing: before the closing codes. Rewrites through
extract.write_tsv. Usage: python -X utf8 tools/blanks.py"""
import re

import batches
import extract

LEAD = re.compile(r"^((?:\{[^}]*\})*)")
TRAIL = re.compile(r"((?:\{[^}]*\})*)$")


def fix(entry):
    text = entry["en"]
    for p in batches.layout_problems(entry, text):
        if p.startswith("leading"):
            text = LEAD.sub(lambda m: m[1] + "　", text, count=1)
        elif p.startswith("trailing"):
            text = TRAIL.sub(lambda m: "　" + m[1], text, count=1)
    return text


def main():
    n = 0
    for path, cols, entries in batches.docs():
        changed = False
        for e in entries:
            if e["en"] and (new := fix(e)) != e["en"]:
                e["en"], changed, n = new, True, n + 1
        if changed:
            extract.write_tsv(path, cols, [[e[c] for c in cols] for e in entries])
    print(f"{n} rows fixed")


if __name__ == "__main__":
    main()
