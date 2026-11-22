"""Polish pass helper (docs/polish.md): show the JP/EN of every id an unticked line names, and start a fix batch.

    python -X utf8 tools/polish.py show [FROM_LINE TO_LINE]   unticked lines with each named id's JP and EN
    python -X utf8 tools/polish.py dump ID...                id<TAB>en per id (draft NAME.out.tsv from it)
    python -X utf8 tools/polish.py batch NAME ID...          work/tl/NAME.tsv listing the ids (write NAME.out.tsv by
                                                             hand, then `tools/batches.py merge NAME --overwrite`, which
                                                             copies each fix to every string with the same JP and form)
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import batches  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r"sol\.\d+\.\d+|[A-Z0-9_]+:[0-9A-F]{5}")


def ids_in(line):
    """sol ids, raw ids, and short forms ("17.23", "11.2") after a full sol id on the same line."""
    found = ID.findall(line)
    found += [f"sol.{m}" for m in re.findall(r"(?<![\w.])(\d+\.\d+)(?![\w.])", line) if f"sol.{m}" not in found]
    return list(dict.fromkeys(found))


def show(lo, hi):
    entries = batches.index()
    lines = (ROOT / "docs/polish.md").read_text(encoding="utf-8").splitlines()
    for n, line in enumerate(lines, 1):
        if not (lo <= n <= hi) or not line.startswith("- [ ]"):
            continue
        print(f"L{n} {line[6:]}")
        for i in ids_in(line):
            e = entries.get(i)
            print(f"   {i}  JP {e['jp']}\n   {' ' * len(i)}  EN {e['en']}" if e else f"   {i}  (no such id)")


if __name__ == "__main__":
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "show":
        show(int(args[0]) if args else 0, int(args[1]) if len(args) > 1 else 10**9)
    elif cmd == "dump":  # id<TAB>en lines, a starting point for NAME.out.tsv
        entries = batches.index()
        print("".join(f"{i}\t{entries[i]['en']}\n" for i in args), end="")
    elif cmd == "batch":
        (batches.TL / f"{args[0]}.tsv").write_text("".join(f"{i}\n" for i in args[1:]), encoding="utf-8", newline="\n")
        print(f"{batches.TL / args[0]}.tsv: {len(args) - 1} ids")
    else:
        sys.exit(__doc__)
