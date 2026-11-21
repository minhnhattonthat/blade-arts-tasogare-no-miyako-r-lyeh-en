"""Raw-string viewer: show EXE/overlay strings in a real text window, for text coverage and visual QA (phase 8).

  python -X utf8 tools/rawview.py [ID-PREFIX ...] [--host status_item] [--host-at HEX] [--jobs 4] [--out work/qa/rawview]

Item names/descriptions, Sphere texts and memory-card messages need inventory or card states the debug tool can't
set, so like solview.py this loads a host state (a warp scene, a few frames before a text window opens) once per
string and points the window's text at the string (tools/lua/rawview.lua). The window keeps the host's geometry:
status_item = the 21x3 status help box (the box item descriptions and Sphere texts draw in). Strings must be in RAM in
the host: EXE strings and those the build relocated to the EXE always are; STATUS strings with the status overlay
(status_item host), LOADSAVE strings left in place only with a LOADSAVE host.
IDs come from build/strings.tsv (RAM address from build/textcover_tbl.lua); a prefix selects many
("DATA/STATUS.BIN", "SLPM"). Per job: <out>/<host>/jNN/<id>_NN.png and log.txt ("TEXT <key>" for textcover.py).
"""
import argparse, concurrent.futures as cf, math, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "debug"))
from skill import SKILL  # noqa: E402
import warp_all  # noqa: E402

LUA = ROOT / "tools" / "lua" / "rawview.lua"
EMU = Path(SKILL) / "scripts" / "emu.py"


def lua_path(p):
    return "[[%s]]" % str(Path(p).resolve()).replace("\\", "/")


def emu(cue, out, extra, timeout):
    cmd = [sys.executable, "-X", "utf8", str(EMU), cue, "--out", str(out), "--debugger", "--timeout", str(timeout)]
    return subprocess.run(cmd + extra, capture_output=True, text=True)


def targets(build):
    """[(id, RAM address, key)] for every raw string of the build."""
    ram = {int(k, 16): int(a, 16) for a, k in re.findall(r"\{0x([0-9A-F]+),0x([0-9A-F]+),", (build / "textcover_tbl.lua").read_text())}
    rows = [ln.split("\t") for ln in (build / "strings.tsv").read_text(encoding="utf-8").splitlines()]
    return [(i, ram[int(k, 16)], int(k, 16)) for i, k in rows if not i.startswith("sol.") and int(k, 16) in ram]


def host_state(cue, out, scene, at, frame, press=None):
    """(state, text address): the scene's host run (remade when the cue is newer) stopped a few frames before the
    first window start with text `at` (default: any) at or after `frame`; with `press` (a route the Lua plays after
    each load, for windows that open on input), the state at `frame` itself."""
    d = out / "host"
    log = d / "log.txt"
    if not (log.exists() and log.stat().st_mtime > os.path.getmtime(cue)):
        sc = next(s for s in warp_all.scenes() if s["name"] == scene)
        emu(cue, d, ["--script", str(ROOT / "tools/debug/warp.lua"), "--var", f"SCENE='{scene}'",
                     "--var", "REPO=" + lua_path(ROOT), "--script", str(LUA), "--var", "RVHOST=true",
                     "--sav", warp_all.card_in(sc, str(d)), "--state-every", "10", "--frames", "30000"], 900)
    wins = [(int(f), int(x, 16)) for f, x in re.findall(r"RV win f(\d+) at=([0-9A-F]+)", log.read_text(encoding="utf-8"))]
    hit = next(((f, x) for f, x in wins if at in (None, x) and f >= frame), None)
    assert hit, f"no window {at and hex(at)} from frame {frame} in the host run: {log}"
    return d / f"s{(frame if press else hit[0] - 3) // 10 * 10:06d}.sstate", hit[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--cue", default="build/blade_arts_en.cue")
    ap.add_argument("--build", default="build", help="dir with strings.tsv + textcover_tbl.lua of that cue")
    ap.add_argument("--host", default="status_item", help="warp scene (tools/debug/scenes.tsv)")
    ap.add_argument("--host-at", type=lambda s: int(s, 16), help="text address of the host window to take over")
    ap.add_argument("--host-frame", type=int, default=0, help="take the first host window at or after this frame")
    ap.add_argument("--host-press", help='route played after each state load, e.g. "10 -;6 triangle" (state = '
                    "--host-frame's): for host windows that open on input")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--quiet", type=int, default=40)
    ap.add_argument("--out", default="work/qa/rawview")
    a = ap.parse_args()
    ts = targets(Path(a.build))
    if a.ids:
        ts = [t for t in ts if any(t[0].startswith(p) for p in a.ids)]
    assert ts, "no such ids"
    out = Path(a.out) / a.host
    out.mkdir(parents=True, exist_ok=True)
    st, at = host_state(a.cue, out, a.host, a.host_at, a.host_frame, a.host_press)
    n = math.ceil(len(ts) / a.jobs)
    chunks = [ts[i:i + n] for i in range(0, len(ts), n)]

    def job(k, chunk):
        d = out / f"j{k:02d}"
        d.mkdir(exist_ok=True)
        tbl = d / "targets.lua"
        tbl.write_text("return {\n" + "".join(f'{{id="{i}",at=0x{x:08X},key=0x{key:08X}}},\n' for i, x, key in chunk)
                       + "}\n", encoding="utf-8")
        r = emu(a.cue, d, ["--script", str(LUA), "--var", "RVTBL=" + lua_path(tbl), "--var", "RVSTATE=" + lua_path(st),
                           "--var", f"RVAT=0x{at:08X}", "--var", f"RVQUIET={a.quiet}", "--frames", "100000000",
                           "--sav", str(out / "host" / "card_in.mcd")]
                + (["--var", f'RVPRESS="{a.host_press}"'] if a.host_press else []),
                120 + len(chunk) * 40)
        return k, r.returncode, len(chunk)

    bad = 0
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for k, rc, cnt in ex.map(lambda x: job(*x), enumerate(chunks)):
            print(f"j{k:02d}: {cnt} strings, exit {rc}")
            bad += rc != 0
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
