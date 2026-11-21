"""build.py: rebuild the disc from work/disc/tree with patched files -> build/blade_arts_en.bin/.cue.

Patched files are written to build/files/<disc path> and swapped in through a generated layout (mkpsxiso `source=`),
so the dumped tree stays pristine. With no patches the output is byte-identical to the original (tests/test_identity.py).
"""
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import check_rom  # noqa: E402
import en  # noqa: E402
import extract  # noqa: E402
import font  # noqa: E402
import marker as markers  # noqa: E402
import rawtext  # noqa: E402
import sol  # noqa: E402

CUE = ROOT / "rom" / "Blade Arts - Tasogare no Miyako R'lyeh (Japan).cue"
DISC = ROOT / "work" / "disc"
TREE = DISC / "tree"
LAYOUT = DISC / "layout.xml"
OUT = ROOT / "build"
NAME = "blade_arts_en"


def unpack():
    """Dump the original disc into work/disc once (tree + layout.xml)."""
    if LAYOUT.is_file() and TREE.is_dir():
        return
    DISC.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(ROOT / "tools/mkpsxiso/dumpsxiso.exe"), "-x", str(TREE), "-s", str(LAYOUT), str(CUE)],
                   check=True, stdout=subprocess.DEVNULL)


def exe():
    """SLPM_866.02 with asm/vwf.asm applied (armips); the glyph/width tables are generated from tools/en.py."""
    gen = OUT / "asm"
    gen.mkdir(parents=True, exist_ok=True)
    glyph, wid = en.tables()
    tables = gen / "en_tables.asm"
    tables.write_text("en_glyph:\n" + "".join(f"    .word 0x{x:08X}\n" for x in glyph)
                      + "en_width:\n" + "".join(f"    .byte {x}\n" for x in wid), encoding="ascii")
    out = gen / "SLPM_866.02"
    r = subprocess.run([str(ROOT / "tools/armips/armips.exe"), str(ROOT / "asm/vwf.asm"),
                        "-strequ", "EXE_IN", str(TREE / "SLPM_866.02"), "-strequ", "EXE_OUT", str(out),
                        "-strequ", "EN_TABLES", str(tables)], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"armips failed:\n{r.stdout}\n{r.stderr}")
    return out.read_bytes()


def sol_texts(qa=None, marker=None):
    """{(block, index): game bytes} from the en column of script/sol/*.tsv; `qa` = {id: en text} overrides;
    `marker(row) -> en text or None` builds the marker script instead."""
    out = {}
    for path in sorted((ROOT / "script" / "sol").glob("*.tsv")):
        for row in extract.read_tsv(path, extract.SOL_COLS):
            _, bid, gi = row["id"].split(".")
            text = (qa or {}).get(row["id"]) or (marker(row) if marker else None) or row["en"]
            if text:
                try:
                    out[int(bid), int(gi)] = en.encode(text)
                except ValueError as e:
                    sys.exit(f"{row['id']}: {e}")
    return out


def raw_texts(files, qa=None, marker=None):
    """Write the en column of script/raw/*.tsv into `files` ({disc path: bytearray}) in place: the new bytes plus NUL
    must fit the original string's bytes plus its NUL (relocation into `room` is phase 7 work)."""
    for path in sorted((ROOT / "script" / "raw").glob("*.tsv")):
        for row in extract.read_tsv(path, extract.RAW_COLS):
            text = (qa or {}).get(row["id"]) or (marker(row) if marker else None) or row["en"]
            if not text:
                continue
            disc, off = row["id"].rsplit(":", 1)
            off = int(off, 16)
            orig = rawtext.encode(row["jp"])
            try:
                new = en.encode(text)
            except ValueError as e:
                sys.exit(f"{row['id']}: {e}")
            if len(new) > len(orig):
                sys.exit(f"{row['id']}: {len(new)} bytes > {len(orig)} in place")
            buf = files.setdefault(disc, bytearray((TREE / disc).read_bytes()))
            assert buf[off:off + len(orig) + 1] == orig + b"\0", row["id"]
            buf[off:off + len(orig) + 1] = new + bytes(len(orig) + 1 - len(new))


def patches(qa=None, marker=False):
    """{disc path: new bytes}: VWF code, English glyphs, SOL.SRP and raw text. `marker`: the phase-5 marker script."""
    sol_orig = (TREE / "DATA" / "SOL.SRP").read_bytes()
    files = {"SLPM_866.02": bytearray(exe())}
    raw_texts(files, qa, markers.raw_marker if marker else None)
    files["DATA/DATA1.PAC"] = font.patch((TREE / "DATA" / "DATA1.PAC").read_bytes())
    while True:
        try:
            files["DATA/SOL.SRP"] = sol.pack(sol_orig, sol_texts(qa, markers.sol_marker if marker else None))
            break
        except ValueError as e:
            m = re.match(r"SOL block (\d+):", str(e))
            if not (marker and m) or markers.SOL_SCALE.get(int(m[1]), 1.0) <= 0.3:
                sys.exit(str(e))
            markers.SOL_SCALE[int(m[1])] = markers.SOL_SCALE.get(int(m[1]), 1.0) - 0.1
    if markers.SOL_SCALE:
        print("marker filler scaled down to fit:", {k: round(v, 1) for k, v in markers.SOL_SCALE.items()})
    return {k: bytes(v) for k, v in files.items()}


def build(out=OUT, files=None):
    """Write <out>/<NAME>.bin/.cue; `files` overrides disc files ({path: bytes}). Returns the .bin path."""
    check_rom.check()
    unpack()
    files = patches() if files is None else files
    out = Path(out).resolve()
    stage = out / "files"
    shutil.rmtree(stage, ignore_errors=True)
    tree = ET.parse(LAYOUT)
    proj = tree.getroot()
    proj.set("image_name", f"{NAME}.bin")
    proj.set("cue_sheet", f"{NAME}.cue")
    lic = proj.find("track/license")
    lic.set("file", str((DISC / lic.get("file")).resolve()))
    top = proj.find("track/directory_tree")
    top.set("source", str((DISC / top.get("source")).resolve()))
    seen = set()

    def walk(node, path):
        for el in node:
            name = el.get("name")
            if el.tag == "dir":
                walk(el, f"{path}{name}/")
            elif el.tag == "file" and f"{path}{name}" in files:
                p = f"{path}{name}"
                dst = stage / p
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(files[p])
                el.set("source", str(dst.resolve()))
                seen.add(p)

    walk(top, "")
    if missing := set(files) - seen:
        sys.exit(f"patched files not on the disc: {sorted(missing)}")
    out.mkdir(parents=True, exist_ok=True)
    xml = out / "layout.xml"
    tree.write(xml, encoding="utf-8")
    r = subprocess.run([str(ROOT / "tools/mkpsxiso/mkpsxiso.exe"), "-y", "-q", str(xml)], cwd=out,
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"mkpsxiso failed:\n{r.stdout}\n{r.stderr}")
    return out / f"{NAME}.bin"


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--qa", action="append", default=[], metavar="ID=TEXT", help="override one line (en syntax)")
    ap.add_argument("--qa-file", help="ID<TAB>TEXT lines (shells mangle backslashes in --qa)")
    ap.add_argument("--marker", action="store_true", help="marker build: every line -> [id] + filler (phase 5)")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    qa = dict(x.split("=", 1) for x in a.qa)
    if a.qa_file:
        qa.update(ln.split("\t", 1) for ln in Path(a.qa_file).read_text(encoding="utf-8").splitlines() if "\t" in ln)
    print(build(a.out, patches(qa, a.marker)))
