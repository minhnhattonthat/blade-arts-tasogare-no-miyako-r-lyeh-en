"""Print script entries (JP + EN) by id, id prefix or regex over the text: the quick lookup for fixes and reviews.

    python -X utf8 tools/show.py sol.17.0 sol.58.10 DATA/STATUS.BIN:00AD8   exact ids
    python -X utf8 tools/show.py --jp 石碑 [--en stele]                       regex over JP / EN (both must match)
    python -X utf8 tools/show.py --en "\\.{4,}" --count                       only the number of hits
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import batches  # noqa: E402


def main(argv):
    jp_re = en_re = None
    count = "--count" in argv
    argv = [a for a in argv if a != "--count"]
    ids = []
    i = 0
    while i < len(argv):
        if argv[i] == "--jp":
            jp_re, i = re.compile(argv[i + 1]), i + 2
        elif argv[i] == "--en":
            en_re, i = re.compile(argv[i + 1]), i + 2
        else:
            ids.append(argv[i])
            i += 1
    entries = batches.index()
    hits = []
    for k, e in entries.items():
        if ids and k not in ids:
            continue
        if jp_re and not jp_re.search(e["jp"]):
            continue
        if en_re and not en_re.search(e["en"]):
            continue
        if ids or jp_re or en_re:
            hits.append(e)
    if count:
        print(len(hits))
        return 0
    for e in hits:
        print(f">> {e['id']}\n   JP {e['jp']}\n   EN {e['en']}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
