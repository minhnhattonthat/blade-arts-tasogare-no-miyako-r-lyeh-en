"""QA overrides that show the pages solview could not reach (phase 8).

  python -X utf8 tools/solview_tails.py [work/qa/solview_report.txt] > work/qa/tails.tsv
  python -X utf8 build.py --qa-file work/qa/tails.tsv --out build/qa_tails
  python -X utf8 tools/solview.py <ids> --cue build/qa_tails/blade_arts_en.cue --out work/qa/solview_tails

The intro host's own timer cuts long voiced messages before their last page ("cut  ID pages N, lint expects M"
in the report). Each cut message is replaced by its unseen pages only (pages N.. of the en text), led by the
message's opening code group with colour codes reset to b0 (the name colour belongs to page 1), so the short
message ends before the timer does. Output: ID<TAB>TEXT for build.py --qa-file.
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def tail(en, shown):
    """en text of pages `shown`.. with the opening code group (colour reset) in front."""
    m = re.match(r"\{[^}]*\}", en)
    lead = re.sub(r"b\d", "b0", m.group(0)) if m else ""
    rest = "@@".join(en.split("@@")[shown:])
    return rest if rest.startswith(lead) else lead + rest


def main():
    report = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "work/qa/solview_report.txt")
    cuts = {m[1]: int(m[2]) for m in re.finditer(r"^cut\s+(\S+) pages (\d+)", report.read_text(encoding="utf-8"), re.M)}
    for f in sorted((ROOT / "script/sol").glob("*.tsv")):
        for r in csv.DictReader(f.open(encoding="utf-8", newline=""), delimiter="\t"):
            if r["id"] in cuts:
                sys.stdout.write(f"{r['id']}\t{tail(r['en'], cuts[r['id']])}\n")


if __name__ == "__main__":
    assert tail("{CSA0t5b2}W:{b0} a@@b@@c{g7i040}", 1) == "{CSA0t5b0}b@@c{g7i040}"
    assert tail("x@@y", 1) == "y"
    main()
