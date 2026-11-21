"""Marker script (phase 5): every visible Japanese run becomes English filler of the same pixel width, the string's
first run starting with its id, so a tour shows which string each box is and how English fills it. Control codes
stay where they were. build.py --marker uses it.

    sol.10.3 "CSA0t0e00894最後の…\\\\どこの…" -> "{CSA0t0e00894}[10.3] The quick brown…{\\\\}fox jumps…"
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import en  # noqa: E402
import rawtext  # noqa: E402

FILLER = "The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs!".split()
# Raw strings that are not text for the marker: data tables, printf formats, debug and dev-only lines.
RAW_SKIP = ("data:", "fullwidth space", "printf", "debug", "dev:")
RAW_TAG = {"SLPM_866.02": "E", "DATA/STATUS.BIN": "S", "DATA/LOADSAVE.BIN": "L", "DATA/BOSS0P.BIN": "B",
           "DATA/BOSS3P.BIN": "B", "DATA/GAME.BIN": "G"}


def fill(px, tag=""):
    """English text about `px` wide (never narrower than the tag)."""
    words, k = [tag] if tag else [], 0
    while en.width(" ".join(words)) < px - 3:
        words.append(FILLER[k % len(FILLER)])
        k += 1
    while len(words) > 1 and en.width(" ".join(words)) > px + 2:
        words.pop()
    return " ".join(words)


def exact(px):
    """A width-gate line exactly `px` wide: '[' + letters + ']' so both edges show in a zoomed shot."""
    body, k = "", 0
    letters = "MWmwHNabdegnopq0123456789"
    while px - en.width("[" + body + "]") > 16:
        body += letters[k % len(letters)]
        k += 1
    by_w = {}
    for c in en.CHARSET:
        by_w.setdefault(en.WIDTH[c], c)
    combos = {0: ""}  # exact top-up for the last few px from letters of each width
    for _ in range(4):
        for w0, s0 in list(combos.items()):
            for w, c in by_w.items():
                combos.setdefault(w0 + w, s0 + c)
    s = "[" + body + combos[px - en.width("[" + body + "]")] + "]"
    assert en.width(s) == px, (px, en.width(s))
    return s


def runs(jp):
    """[(kind, text)]: 'byte' = a {n}/{0B} escape of a raw string, 'code' = an ASCII control-code run, 'text'."""
    out = []
    for m in re.finditer(r"\{(?:n|[01][0-9A-F])\}|[\x00-\x7f]+?(?=\{(?:n|[01][0-9A-F])\}|[^\x00-\x7f]|$)|[^\x00-\x7f]+",
                         jp):
        t = m[0]
        out.append(("byte" if t.startswith("{") and t.endswith("}") else "code" if t < "\x80" else "text", t))
    return out


def build(jp, tag, scale=1.0):
    out, first = [], True
    for kind, t in runs(jp):
        if kind == "byte":
            out.append(t)
        elif kind == "code":
            out.append("{%s}" % t)
        else:
            out.append(fill(int(len(t) * en.JP_PITCH * scale), tag if first else ""))
            first = False
    return "".join(out)


SOL_SCALE = {}  # block id -> filler scale, lowered by build.py for blocks whose full-width markers overflow


def sol_marker(row):
    """None for an empty string or one with an odd code run (sol.132.110's broken `b`: left as it is)."""
    if not row["jp"]:
        return None
    s = build(row["jp"], "[%s]" % row["id"].split(".", 1)[1], SOL_SCALE.get(int(row["id"].split(".")[1]), 1.0))
    try:
        en.encode(s)
    except ValueError:
        return None
    return s


def raw_marker(row):
    """Marker for a raw string, no longer than the original bytes (written in place; the NUL stays put)."""
    if any(row["notes"].startswith(p) for p in RAW_SKIP):
        return None
    path, off = row["id"].rsplit(":", 1)
    tag = RAW_TAG[path] + off.lstrip("0")
    limit = len(rawtext.encode(row["jp"]))
    for scale in (1.0, 0.8, 0.6, 0.4, 0.2, 0.0):
        s = build(row["jp"], tag if scale else "", scale)
        if len(en.encode(s)) <= limit:
            return s
        s = build(row["jp"], tag[:2] if scale else "", scale)
        if len(en.encode(s)) <= limit:
            return s
    return None


if __name__ == "__main__":
    print(build("CSA0t0e00894最後の最後\\\\どこ", "[10.3]"))
    print(raw_marker({"id": "DATA/BOSS0P.BIN:0E0FC", "jp": "BKA2BKC111何か・・・いる？{n}", "notes": ""}))
