"""SOL message viewer: show SOL.SRP messages in the game's own renderer, for text coverage and visual QA (phase 8).

  python -X utf8 tools/solview.py [ID|BLOCK ...] [--cue build/blade_arts_en.cue] [--jobs 4] [--out work/qa/solview]

ID = sol.4.0, BLOCK = 4 (every message of old block 4); none = every message. Map events need story state the debug
tool can't set, so instead of playing them this loads a host state (the intro, just before its first message lookup)
once per message and swaps the message in at the lookup (tools/lua/solview.lua). Geometry (subtitle / WS window /
choice box) is coded in the string itself, so the host scene doesn't change the layout.
Per job: <out>/jNN/<id>_NN.png (one shot per page, before each circle press) and log.txt ("TEXT <key>" for
textcover.py, "SV end|timeout <id> pages N"). Host state: <out>/host.sstate, remade when the cue is newer.
"""
import argparse, concurrent.futures as cf, math, os, re, struct, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import sol  # noqa: E402
from skill import SKILL  # noqa: E402

LUA = ROOT / "tools" / "lua" / "solview.lua"
EMU = Path(SKILL) / "scripts" / "emu.py"


def targets(orig, new):
    """[(id, key, old block id, n, file offset of n's sector, last-index table)] in file order."""
    out = []
    for (old, _), (bid, pos, blk) in zip(sol.header(orig), sol.blocks(new)):
        nsec = len(blk) // sol.SECTOR
        hdr = struct.unpack_from("<I", blk, 0)[0]
        tbl = list(struct.unpack_from(f"<{(hdr - 8) // 2}H", blk, 8))[:nsec]
        for gi, s, *_ in sol.strings(blk):
            out.append((f"sol.{old}.{gi}", 0x50000000 | old << 16 | gi, old, gi, pos + s * sol.SECTOR, tbl))
    return out


def lua_path(p):
    return "[[%s]]" % str(Path(p).resolve()).replace("\\", "/")


def emu(cue, out, extra, timeout):
    cmd = [sys.executable, "-X", "utf8", str(EMU), cue, "--out", str(out), "--debugger", "--timeout", str(timeout)]
    return subprocess.run(cmd + extra, capture_output=True, text=True)


def host_state(cue, out):
    """The intro, stopped a few frames before its first message lookup."""
    st = out / "host.sstate"
    if st.exists() and st.stat().st_mtime > os.path.getmtime(cue):
        return st
    d = out / "host"
    r = emu(cue, d, ["--script", str(ROOT / "tools/debug/warp.lua"), "--var", "SCENE='intro'",
                     "--var", "REPO=" + lua_path(ROOT), "--script", str(LUA), "--var", "SVHOST=true",
                     "--state-every", "50", "--frames", "4000"], 900)
    log = (d / "log.txt").read_text(encoding="utf-8")
    f = next((int(ln.split("f")[-1]) for ln in log.splitlines() if ln.startswith("SV lookup")), None)
    assert f, f"no lookup in the host run (exit {r.returncode}): {d}"
    src = d / f"s{(f - 5) // 50 * 50:06d}.sstate"
    st.write_bytes(src.read_bytes())
    return st


CROP = "0,192,320,46"   # subtitle window rows (2 lines at y 200-225) incl. inline choices


def screen_text(e, k):
    """Expected lines of screen k (1-based) of a message, " / " between lines; "" past the last screen."""
    import batches
    n = batches.form(e)[2]
    scr = [p[j:j + n] for p in batches.pages_of(e["en"] or e["jp"], e) for j in range(0, max(len(p), 1), n)]
    return " / ".join(batches.plain(x) for x in scr[k - 1]) if k <= len(scr) else ""


def report(out):
    """Check every message's page count against the screens the build lint expects (batches.screens), then write
    per-block contact sheets to <out>/sheets: subtitle/choice pages cropped to the subtitle rows (60 per sheet),
    WS-window pages whole (12 per sheet). Each sheet gets a .txt beside it: tile order and the expected text, for the visual-QA reviewer."""
    import batches, extract
    entries = {}
    for p in sorted((ROOT / "script" / "sol").glob("*.tsv")):
        for r in extract.read_tsv(p, extract.SOL_COLS):
            entries[r["id"]] = r
    runs, cut = {}, set()
    for log in sorted(out.glob("j*/log.txt")):   # j00.. then re-runs (jf00..): a later run of an id wins
        moved = None
        for ln in log.read_text(encoding="utf-8").splitlines():
            if m := re.match(r"SV host moved on (\S+)", ln):
                moved = m[1]
            elif m := re.match(r"SV (end|timeout) (\S+) pages (\d+)", ln):
                runs[m[2]] = (m[1], int(m[3]), log.parent)
                (cut.add if moved == m[2] else cut.discard)(m[2])
                moved = None
    bad = []
    for i, e in entries.items():
        if i not in runs:
            bad.append(f"not run  {i}")
            continue
        how, pages, _ = runs[i]
        want = batches.screens(e["en"] or e["jp"], e)
        if i in cut:
            how, pages = "cut", pages - 1   # the host's next lookup came first: the last shot is after the cut
        last = batches.lines_of(e["en"] or e["jp"], e)[-1]
        if pages == want + 1 and len(last) > batches.form(e)[2] and re.fullmatch(r"(\{[^}]*\}|[ 　])*", last[-1]):
            want += 1   # `\\` on the box's last line waits, then a blank page with only codes (as in the JP)
        if how != "end" or pages != want:
            bad.append(f"{how:8} {i} pages {pages}, lint expects {want}")
    sheets = out / "sheets"
    sheets.mkdir(exist_ok=True)
    groups = {}
    for i, e in entries.items():
        if i in runs:
            kind = "ws" if batches.form(e)[0].startswith("ws") else "sub"
            shots = sorted(runs[i][2].glob(f"{i}_*.png"))
            groups.setdefault((int(i.split(".")[1]), kind), []).extend((i, s, e) for s in shots)
    nsheets = 0
    for (blk, kind), tiles in sorted(groups.items()):
        size = 60 if kind == "sub" else 12
        for k in range(0, len(tiles), size):
            part = tiles[k:k + size]
            name = sheets / f"b{blk:03d}_{kind}_{k // size + 1:02d}_sheet.png"
            opts = ["--cols", "3", "--crop", CROP, "--div", "1"] if kind == "sub" else ["--cols", "3", "--div", "1"]
            subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "sheet.py"),
                            *[str(s) for _, s, _ in part], *opts, "--max", str(size), "--out", str(name)],
                           check=True, capture_output=True)
            name.with_suffix(".txt").write_text("".join(
                f"{t + 1}\t{s.stem}\t{screen_text(e, int(s.stem.rsplit('_', 1)[1]))}\n"
                for t, (i, s, e) in enumerate(part)), encoding="utf-8")
            nsheets += 1
    print("\n".join(bad))
    print(f"{len(runs)}/{len(entries)} messages shown, {len(bad)} page-count problems, {nsheets} sheets in {sheets}")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--report", action="store_true", help="no run: check page counts and write sheets for --out")
    ap.add_argument("--cue", default="build/blade_arts_en.cue")
    ap.add_argument("--sol", default="build/files/DATA/SOL.SRP", help="the SOL.SRP inside that cue")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--quiet", type=int, default=30, help="frames into a page wait before its shot (window fade-in)")
    ap.add_argument("--max", type=int, default=1800, help="frames per message before giving up")
    ap.add_argument("--out", default="work/qa/solview")
    ap.add_argument("--debug", action="store_true", help="log every page-state change")
    ap.add_argument("--var", action="append", default=[], help="extra Lua global for solview.lua (NAME=LUA)")
    a = ap.parse_args()
    out = Path(a.out)
    if a.report:
        return report(out)
    out.mkdir(parents=True, exist_ok=True)
    ts = targets(sol.DEFAULT.read_bytes(), Path(a.sol).read_bytes())
    if a.ids:
        want = set(a.ids)
        ts = [t for t in ts if t[0] in want or str(t[2]) in want]
    assert ts, "no such ids"
    st = host_state(a.cue, out)
    n = math.ceil(len(ts) / a.jobs)
    chunks = [ts[i:i + n] for i in range(0, len(ts), n)]

    def job(k, chunk):
        d = out / f"j{k:02d}"
        d.mkdir(exist_ok=True)
        tbl = d / "targets.lua"
        tbl.write_text("return {\n" + "".join(
            f'{{id="{i}",key=0x{key:08X},blk={b},n={gi},off={off},tbl={{{",".join(map(str, t))}}}}},\n'
            for i, key, b, gi, off, t in chunk) + "}\n", encoding="utf-8")
        r = emu(a.cue, d, ["--script", str(LUA), "--var", "SVTBL=" + lua_path(tbl), "--var", "SVSOL=" + lua_path(a.sol),
                           "--var", "SVSTATE=" + lua_path(st), "--var", f"SVQUIET={a.quiet}", "--var", f"SVMAX={a.max}",
                           "--frames", "100000000"] + (["--var", "SVDEBUG=true"] if a.debug else [])
                + [x for v in a.var for x in ("--var", v)], 120 + len(chunk) * (a.max + 200) // 30)
        return k, r.returncode, len(chunk)

    bad = 0
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for k, rc, cnt in ex.map(lambda x: job(*x), enumerate(chunks)):
            print(f"j{k:02d}: {cnt} messages, exit {rc}")
            bad += rc != 0
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
