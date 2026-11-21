"""Translation batches (docs/translator-brief.md): split untranslated text, check translator output, merge it back.

    python -X utf8 tools/batches.py split [--size 3500]   work/tl/bNNN.tsv and build/terms_bNNN.txt for untranslated JP
    python -X utf8 tools/batches.py check [bNNN ...]      a batch's .out.tsv; with no batch, all shipped English (for check.py)
    python -X utf8 tools/batches.py merge bNNN ... [--overwrite]   check, then write the English into script/
    python -X utf8 tools/batches.py fit "text" FORM       width per line of one en string (FORM: subtitle, ws2203, ...)

Copied from the skill's assets/batches.py; the ADAPTER section reads script/sol + script/raw TSVs (tools/extract.py)
and the en syntax of tools/en.py. Batch TSV: id, speaker, form, limit, JP with its control-code runs in braces
(`\\\\` line and `@@` page stay bare, as in the en column). Output: work/tl/bNNN.out.tsv, id<TAB>English, every id
once, same order. Raw strings longer than their bytes in place are warnings (relocation is phase 7), not errors.
"""
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import en  # noqa: E402
import extract  # noqa: E402
import rawtext  # noqa: E402

TL = ROOT / "work/tl"
SCRIPT = ROOT / "script"
GLOSSARY = ROOT / "glossary.md"
MAX_ENTRIES = 150

# ---- ADAPTER: this game's text format ----
CODE_RUN = re.compile(r"\{(?:n|[01][0-9A-F])\}|[\x00-\x7f]+")  # jp: ASCII runs are codes, {n}/{0B} raw bytes
LAYOUT = re.compile(r"\\\\|@@")
FREE = re.compile(r"g\d")  # px gaps: the English places them freely
ATOM = re.compile(r"[A-Za-z\[%]+[-+0-9]*|[^A-Za-z\[%]")
VARIABLE = r"\{%[sd]\}"  # printf field: "1st" comes out as "1th"
# every name + honorific in the script (a scan for [kana/kanji]+さん/様/ちゃん/君 found only these; the rest are words
# such as ジイさん "the old man", 貴様, 模様)
HONORIFICS = {r"ナカムラ様": "-sama", r"リズィちゃん": "-chan", r"キキ君": "-kun"}
RAW_SKIP = ("data:", "fullwidth space", "debug", "dev:", "card:")
RAW_FORM = {"DATA/STATUS.BIN": ("status", 252, 3), "DATA/BOSS0P.BIN": ("boss", 286, 2),
            "DATA/BOSS3P.BIN": ("boss", 286, 2), "DATA/LOADSAVE.BIN": ("loadsave", 200, 1),
            "SLPM_866.02": ("exe", 252, 3), "DATA/GAME.BIN": ("exe", 252, 3)}


def docs():
    """(path, cols, entries) per script file; entries are the TSV rows as dicts."""
    for path in sorted((SCRIPT / "sol").glob("*.tsv")):
        yield path, extract.SOL_COLS, extract.read_tsv(path, extract.SOL_COLS)
    for path in sorted((SCRIPT / "raw").glob("*.tsv")):
        yield path, extract.RAW_COLS, extract.read_tsv(path, extract.RAW_COLS)


def is_raw(entry):
    return not entry["id"].startswith("sol.")


def needs_english(entry):
    """Text only: no JP letters (pure code strings), dev/debug/data rows and card titles stay as they are."""
    if not re.search(r"[^\x00-\x7f]", entry["jp"]) or entry["en"]:
        return False
    return not (is_raw(entry) and entry["notes"].startswith(RAW_SKIP))


def group_of(entry):
    """Identical strings (blocks 4/5, 24/117, 91-95... repeat whole scenes) are translated once: the batch holds the
    group's first id and merge copies its English to the rest."""
    return form(entry), entry["jp"]


def entry_key(entry):
    return entry["id"]


def braced(jp):
    """jp with its code runs in braces: what translators copy into the English."""
    return CODE_RUN.sub(lambda m: m[0] if m[0].startswith("{") else _brace_run(m[0]), jp)


def _brace_run(t):
    out = []
    for part in re.split(r"(\\\\|@@)", t):
        if part:
            out.append(part if LAYOUT.fullmatch(part) else "{%s}" % part)
    return "".join(out)


def form(entry):
    """(form, px per line, lines per page)."""
    if is_raw(entry):
        return RAW_FORM[entry["id"].rsplit(":", 1)[0]]
    jp = entry["jp"]
    if m := re.search(r"WS(\d\d)(\d\d)", jp):
        return f"ws{m[1]}{m[2]}", int(m[1]) * 12, int(m[2])
    if re.search(r"\[DD\d", jp):
        return "choice", 288, 2
    return "subtitle", 288, 2


def limit_label(entry):
    f, px, lines = form(entry)
    voiced = " voiced:keep@@" if re.search(r"e\d{5}", entry["jp"]) else ""
    return f"{px}px x{lines}{voiced}"


def lines_of(text, entry):
    sep = r"\{n\}|\\\\" if is_raw(entry) else r"\\\\"
    return [re.split(sep, page) for page in text.split("@@")]


def pages_of(text, entry):
    out = []
    for page in lines_of(text, entry):
        if len(page) > 1 and re.fullmatch(r"(\{[^}]*\}|[ 　])*", page[-1]):
            page = page[:-1]  # a trailing {n} or \\ (+ codes) ends the page: the last line's \\ waits like @@
        out.append(page)
    return out


def screens(text, entry):
    """Pages the player sees: lines past the box's count start a new page by themselves."""
    n = form(entry)[2]
    return sum(-(-len(p) // n) for p in pages_of(text, entry))


def width_problems(entry, text):
    f, px, nlines = form(entry)
    out = []
    for page in pages_of(text, entry):
        if len(page) > nlines:
            out.append(f"{len(page)} lines on a page (max {nlines}; start a new page with @@)")
        for line in page:
            if (w := en.width(line)) > px:
                out.append(f"line {w} px > {px}: {line[:40]!r}")
    if re.search(r"e\d{5}", entry["jp"]) and (a := screens(text, entry)) != (b := screens(braced(entry["jp"]), entry)):
        out.append(f"voiced: {a} pages but JP has {b} (voice timing cuts pages; match the JP's @@)")
    return out


def warnings(entry, text):
    if is_raw(entry):
        try:
            n, room = len(en.encode(text)), len(rawtext.encode(entry["jp"]))
        except ValueError:
            return []
        disc, off = entry["id"].rsplit(":", 1)
        off, hdr = int(off, 16), rawtext.FILES[disc][1]
        room = min(int(entry["room"]), ((off - hdr + room + 1 + 3) & ~3) + hdr - off) - 1  # same as build.raw_texts
        plain = [r for r in entry["refs"].split(",") if r not in ("", "-") and "+" not in r]
        if n > room and (not plain or "+" in entry["refs"]):  # build.py relocates only via a data word
            return [f"{n} bytes > {room} in place and no data-word pointer: build.py will reject it"]
    return []


def code_atoms(text, from_jp):
    if from_jp:
        runs = [m[0] for m in CODE_RUN.finditer(text)]
        runs = [r.strip("{}") if r.startswith("{") else r for r in runs]
    else:
        runs = re.findall(r"\{([^}]*)\}", text)
    atoms = Counter()
    for r in runs:
        for a in ATOM.findall(LAYOUT.sub("", r)):
            if not FREE.fullmatch(a) and a.strip():
                atoms["b4" if a == "b" and from_jp else a] += 1  # sol.132.110's bare b: a JP typo for b4 (Rei's colour)
    return atoms


def encodable(char, jp):
    """ASCII from the English font; other symbols only if the JP has them (★, fullwidth space for centring)."""
    if char in en.WIDTH:
        return True
    if ord(char) < 0x80 or re.match(r"[぀-ヿ一-鿿Ａ-Ｚａ-ｚ０-９]", char):
        return False
    return char in jp
# ---- end of ADAPTER ----


def kind(char):
    if "぀" <= char <= "ゟ":
        return "hiragana"
    if "゠" <= char <= "ヿ":
        return "katakana"
    if "一" <= char <= "鿿" or char == "々":
        return "kanji"
    return "other"


def has_term(jp, term):
    """term occurs as a whole kana or kanji run: ミン isn't in タイミング, くも isn't in ぼくも."""
    for m in re.finditer(re.escape(term), jp):
        a, b = m.start(), m.end()
        if (a == 0 or kind(jp[a - 1]) != kind(term[0])) and (b == len(jp) or kind(jp[b]) != kind(term[-1])):
            return True
    return False


def glossary():
    """[(JP forms, EN forms, avoid forms)] from glossary.md's | JP | EN | max | notes | Avoid | tables."""
    rows = []
    if not GLOSSARY.exists():
        return rows
    for line in GLOSSARY.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) >= 2 and cells[0] not in ("JP", "") and not set(cells[0]) <= set("-: "):
            avoid = [x.strip() for x in cells[4].split("/") if x.strip()] if len(cells) > 4 else []
            rows.append(([x.strip() for x in cells[0].split("/")], [x.strip() for x in cells[1].split("/")], avoid))
    return rows


def plain(text):
    """Letters only: codes and layout out, for glossary matching."""
    return " ".join(re.sub(r"\{[^}]*\}|\\\\|@@", " ", text).split())


def layout_problems(entry, text):
    """Leading/trailing blanks the JP has (an indent leaves room for a cursor), and stub last lines: a multi-line page
    ending on under 6 letters, unless the JP page ends on a stub too."""
    out = []
    jp = braced(entry["jp"])
    for side, rx in (("leading", r"^(?:\{[^}]*\})*[ 　]"), ("trailing", r"[ 　](?:\{[^}]*\})*$")):
        if re.search(rx, jp) and not re.search(rx, text):
            out.append(f"{side} blank in the JP is missing")
    jp_pages = pages_of(jp, entry)
    for k, page in enumerate(pages_of(text, entry)):
        last = re.sub(r"\{[^}]*\}", "", page[-1]).strip()
        jp_page = jp_pages[k] if k < len(jp_pages) else [""]
        jp_stub = len(jp_page) > 1 and len(re.sub(r"\{[^}]*\}", "", jp_page[-1]).strip()) < 6
        if len(page) > 1 and len(last) < 6 and last.strip(".!?…") and not jp_stub:  # a lone "..." is a timed pause
            out.append(f"stub last line {last!r}: rewrap so the page's last line holds more than one short word")
    return out


def problems(entry, text, terms):
    """Every rule, on one line of English."""
    jp = entry["jp"]
    if not text.strip():
        return ["empty English"]
    out = []
    if "\t" in text or re.search(r"(?<!\\)\\u[0-9a-fA-F]{4}", text):
        out.append("escape sequence or tab in the English (line break is \\\\, page break @@)")
    body = re.sub(r"\{[^}]*\}|\\\\|@@", "", text)
    measurable = False
    if bad := sorted({c for c in body if not encodable(c, jp)}):
        out.append(f"characters not in the font {bad}")
    else:
        try:
            en.encode(text)
            measurable = True
        except ValueError as e:
            out.append(f"does not encode: {e}")
    want, have = code_atoms(jp, True), code_atoms(text, False)
    if want != have:
        out.append(f"control codes differ: missing {dict(want - have)} extra {dict(have - want)}")
    if re.search(r"\.{4,}", re.sub(r"\{[^}]*\}|\\\\|@@", " ", text)):
        out.append('ellipsis of 4+ dots: one "..." per pause however long the JP run (glossary, D11)')
    if re.search(VARIABLE + r"(st|nd|rd|th)\b", text):
        out.append('ordinal suffix after a variable (write "No. {%s}")')
    jp_plain = CODE_RUN.sub("", jp)
    en_terms = plain(text).lower()
    for jps, ens, avoid in terms:
        if any(has_term(jp_plain, j) for j in jps) and not any(" ".join(e.split()).lower() in en_terms for e in ens):
            out.append(f"glossary: {jps[0]} -> {ens[0]}")
        out += [f"glossary Avoid: {a}" for a in avoid if re.search(rf"\b{re.escape(a)}\b", plain(text))]
    for jp_form, en_form in HONORIFICS.items():
        if re.search(jp_form, jp_plain) and en_form.lower() not in text.lower():
            out.append(f"honorific {jp_form[-2:]} needs {en_form}")
    out += layout_problems(entry, text)
    return out + (width_problems(entry, text) if measurable else [])


def index():
    result = {}
    for _, _, entries in docs():
        for e in entries:
            key = entry_key(e)
            if key in result:
                raise ValueError(f"duplicate batch key {key!r}")
            result[key] = e
    return result


def read_tsv(path):
    return [line.split("\t") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def existing():
    return sorted(TL.glob("b[0-9][0-9][0-9].tsv"))


def split(size):
    """Numbers on from the last batch and leaves out ids already batched, so a repeat run can't duplicate work."""
    index()
    TL.mkdir(parents=True, exist_ok=True)
    (ROOT / "build").mkdir(exist_ok=True)
    taken = {r[0] for p in existing() for r in read_tsv(p)}
    n = max((int(p.stem[1:]) for p in existing()), default=0)
    groups = {}
    for _, _, entries in docs():
        for e in entries:
            if needs_english(e) and entry_key(e) not in taken:
                groups.setdefault(group_of(e), [e])  # one representative per identical string
    batches, cur, chars = [], [], 0
    for group in groups.values():
        c = sum(len(CODE_RUN.sub("", e["jp"])) for e in group)
        if cur and (chars + c > size or len(cur) + len(group) > MAX_ENTRIES):
            batches.append(cur)
            cur, chars = [], 0
        cur += group
        chars += c
    if cur:
        batches.append(cur)
    terms = glossary()
    for batch in batches:
        n += 1
        name = f"b{n:03d}"
        path = TL / f"{name}.tsv"
        if path.exists():
            sys.exit(f"{path} already exists")
        rows = [f"{entry_key(e)}\t\t{form(e)[0]}\t{limit_label(e)}\t{braced(e['jp'])}" for e in batch]
        path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
        jps = " ".join(CODE_RUN.sub("", e["jp"]) for e in batch)
        used = [(j, ens[0]) for jpl, ens, _ in terms for j in jpl if has_term(jps, j)]
        (ROOT / f"build/terms_{name}.txt").write_text("".join(f"{j}\t{e}\n" for j, e in used)
                                                      or "(no glossary terms in this batch)\n", encoding="utf-8", newline="\n")
    print(f"{len(batches)} new batches in {TL}, {len(taken)} ids already batched")


def check_batch(batch, entries, terms):
    want = [r[0] for r in read_tsv(TL / f"{batch}.tsv")]
    out = TL / f"{batch}.out.tsv"
    if not out.exists():
        return [f"{out.name} missing"], [], {}
    rows = [(r[0], "\t".join(r[1:])) for r in read_tsv(out)]
    bad, warn = [], []
    if [r[0] for r in rows] != want:
        got = [r[0] for r in rows]
        dup = sorted(i for i, c in Counter(got).items() if c > 1)
        bad.append(f"ids differ: missing {sorted(set(want) - set(got))[:8]} extra {sorted(set(got) - set(want))[:8]} "
                   f"duplicate {dup[:8]} (order must match too)")
    for eid, text in rows:
        if eid in entries:
            bad += [f"{eid}: {p}: {text!r}" for p in problems(entries[eid], text, terms)]
            warn += [f"{eid}: {p}" for p in warnings(entries[eid], text)]
    return bad, warn, dict(rows)


def merge(new, overwrite):
    """Refuses to replace different English unless told to, before anything is written. Copies each string's English
    to every untranslated identical string (group_of)."""
    entries = index()
    by_group = {group_of(entries[k]): v for k, v in new.items() if k in entries}
    new = dict(new)
    for k, e in entries.items():
        if k not in new and group_of(e) in by_group and (overwrite or needs_english(e)):
            new[k] = by_group[group_of(e)]
    if not overwrite:
        for _, _, entries in docs():
            for e in entries:
                if entry_key(e) in new and e["en"] and e["en"] != new[entry_key(e)]:
                    sys.exit(f"{e['id']} would lose {e['en']!r}: pass --overwrite if that is meant")
    changed = 0
    for path, cols, entries in docs():
        touched = False
        for e in entries:
            if entry_key(e) in new and e["en"] != new[entry_key(e)]:
                e["en"] = new[entry_key(e)]
                touched = True
                changed += 1
        if touched:
            extract.write_tsv(path, cols, [[e[c] for c in cols] for e in entries])
    print(f"merged: {changed} entries changed")


def fit(text, form_name):
    text = re.sub(r"(?<!\\)\\(?!\\)", r"\\\\", text)  # shells often eat one of the two backslashes
    entry = {"id": "sol.0.0", "jp": text if "voiced" not in form_name else "e00000", "notes": ""}
    if m := re.fullmatch(r"ws(\d\d)(\d\d)", form_name):
        entry["jp"] = f"WS{m[1]}{m[2]}"
    elif form_name in ("status", "boss", "loadsave", "exe"):
        path = {v[0]: k for k, v in RAW_FORM.items()}[form_name]
        entry["id"] = f"{path}:0"
    for i, page in enumerate(lines_of(text, entry)):
        for line in page:
            print(f"page {i + 1}: {en.width(line):3d} px  {line}")
    for p in width_problems(entry, text):
        print("PROBLEM:", p)


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    if cmd == "split":
        return split(int(args[args.index("--size") + 1]) if "--size" in args else 3500)
    if cmd == "fit":
        return fit(args[0], args[1] if len(args) > 1 else "subtitle")
    overwrite = "--overwrite" in args
    names = [a for a in args if a != "--overwrite"]
    entries, terms = index(), glossary()
    if cmd == "check" and not names:
        bad = [f"{i}: {p}: {e['en']!r}" for i, e in entries.items() if e["en"] for p in problems(e, e["en"], terms)]
        warn = [f"{i}: {p}" for i, e in entries.items() if e["en"] for p in warnings(e, e["en"])]
        print(f"{len(entries)} entries, {sum(bool(e['en']) for e in entries.values())} with English, "
              f"{len(bad)} problems, {len(warn)} warnings")
        print("\n".join(bad[:200] + ["warning: " + w for w in warn]))
        return 1 if bad else 0
    if cmd not in ("check", "merge") or not names:
        sys.exit(__doc__)
    failed = 0
    for batch in names:
        bad, warn, rows = check_batch(batch, entries, terms)
        failed += bool(bad)
        print(f"{batch}: " + ("OK" if not bad else f"{len(bad)} problems") + (f", {len(warn)} warnings" if warn else ""))
        for line in bad + ["warning: " + w for w in warn]:
            print("  " + line)
        if cmd == "merge" and not bad:
            merge(rows, overwrite)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
