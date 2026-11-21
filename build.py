"""build.py: rebuild the disc from work/disc/tree with patched files -> build/blade_arts_en.bin/.cue.

Patched files are written to build/files/<disc path> and swapped in through a generated layout (mkpsxiso `source=`),
so the dumped tree stays pristine. With no patches the output is byte-identical to the original (tests/test_identity.py).
"""
import re
import shutil
import struct
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
EXE_BASE, EXE_HDR = 0x80010000, 0x800
FREE_END = 0x800BA1FC  # asm/vwf.asm FREE_END


def unpack():
    """Dump the original disc into work/disc once (tree + layout.xml)."""
    if LAYOUT.is_file() and TREE.is_dir():
        return
    DISC.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(ROOT / "tools/mkpsxiso/dumpsxiso.exe"), "-x", str(TREE), "-s", str(LAYOUT), str(CUE)],
                   check=True, stdout=subprocess.DEVNULL)


def exe(sol_map=()):
    """SLPM_866.02 with asm/vwf.asm applied (armips); the glyph/width tables are generated from tools/en.py,
    sol_map (old SOL block id -> sector; empty = no remap) from sol.remap()."""
    gen = OUT / "asm"
    gen.mkdir(parents=True, exist_ok=True)
    glyph, wid = en.tables()
    tables = gen / "en_tables.asm"
    tables.write_text("en_glyph:\n" + "".join(f"    .word 0x{x:08X}\n" for x in glyph)
                      + "en_width:\n" + "".join(f"    .byte {x}\n" for x in wid)
                      + ".align 2\nsol_map:\n" + "".join(f"    .halfword {x}\n" for x in sol_map), encoding="ascii")
    out = gen / "SLPM_866.02"
    sym = gen / "vwf.sym"
    r = subprocess.run([str(ROOT / "tools/armips/armips.exe"), str(ROOT / "asm/vwf.asm"), "-sym", str(sym),
                        "-strequ", "EXE_IN", str(TREE / "SLPM_866.02"), "-strequ", "EXE_OUT", str(out),
                        "-strequ", "EN_TABLES", str(tables), "-equ", "SOL_MAP_N", str(len(sol_map))],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"armips failed:\n{r.stdout}\n{r.stderr}")
    labels = {ln.split()[1].lower(): int(ln.split()[0], 16) for ln in sym.read_text().splitlines() if len(ln.split()) == 2}
    return out.read_bytes(), labels["vwf_end"]


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


_ORIG = {}


def original(disc):
    """The dumped (clean) bytes of a disc file: what every write is checked against."""
    if disc not in _ORIG:
        _ORIG[disc] = (TREE / disc).read_bytes()
    return _ORIG[disc]


class Writes:
    """Every byte the build changes, logged as `OFFSET ORIG_HEX NEW_HEX by` per disc file (romdiff.py --writes)."""

    def __init__(self):
        self.log = {}

    def put(self, buf, disc, off, data, by):
        self.log.setdefault(disc, []).append((off, original(disc)[off:off + len(data)], bytes(data), by))
        buf[off:off + len(data)] = data

    def runs(self, disc, new, by):
        """Log whole-file rewrites (armips, font) as their differing runs."""
        old = original(disc)
        i, n = 0, min(len(old), len(new))
        while i < n:
            if old[i] != new[i]:
                j = i
                while j < n and old[j] != new[j]:
                    j += 1
                self.log.setdefault(disc, []).append((i, old[i:j], bytes(new[i:j]), by))
                i = j
            i += 1
        if len(new) > n:  # appended bytes: romdiff.py reads past the original's end as FF
            self.log.setdefault(disc, []).append((n, b"\xff" * (len(new) - n), bytes(new[n:]), by + " (appended)"))

    def save(self, out):
        for disc, rows in self.log.items():
            p = out / "writes" / (disc.replace("/", "_") + ".txt")
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("".join(f"{o:X} {a.hex()} {b.hex()} {by}\n" for o, a, b, by in rows), encoding="utf-8")


class Free:
    """EXE free area after the VWF code (vwf_end .. FREE_END): relocated raw strings, 4-aligned (the parser reads
    halfwords)."""

    def __init__(self, lo, hi):
        self.lo, self.hi = (lo + 3) & ~3, hi

    def alloc(self, n):
        a = self.lo
        if a + n > self.hi:
            sys.exit(f"EXE free area full: {n} bytes at 0x{a:08X}, ends 0x{self.hi:08X}")
        self.lo = (a + n + 3) & ~3
        return a


def exe_off(addr):
    return addr - EXE_BASE + EXE_HDR


# Memory-card title (docs/re/text.md §Card title): prefix ブレイドアーツ／ (16) + save no. placeholder (6) + location
# + tail (LOADSAVE:00240) + time placeholder (10) must stay within 63 bytes + NUL.
TITLE_FIXED = 16 + 6 + 10
LOCATION_TABLE_END = 0x22C  # LOADSAVE strings before the title prefix are the location names


def raw_texts(files, writes, free, qa=None, marker=None):
    """Write the en column of script/raw/*.tsv into `files` ({disc path: bytearray}): in place when the new bytes plus
    NUL fit up to the next 4-byte boundary (strings are 4-aligned, so that is padding), else into the EXE free area
    with every data-word pointer to the string repointed and the old bytes zeroed."""
    rows = [r for p in sorted((ROOT / "script" / "raw").glob("*.tsv")) for r in extract.read_tsv(p, extract.RAW_COLS)]
    texts = {r["id"]: (qa or {}).get(r["id"]) or (marker(r) if marker else None) or r["en"] for r in rows}
    tail = texts["DATA/LOADSAVE.BIN:00240"] or "／ＴＩＭＥ"
    title_room = 63 - TITLE_FIXED - len(en.encode(tail) if texts["DATA/LOADSAVE.BIN:00240"] else rawtext.encode(tail))
    for row in rows:
        text = texts[row["id"]]
        if not text:
            continue
        disc, off = row["id"].rsplit(":", 1)
        off = int(off, 16)
        orig = rawtext.encode(row["jp"])
        try:
            new = en.encode(text)
        except ValueError as e:
            sys.exit(f"{row['id']}: {e}")
        if disc == "DATA/LOADSAVE.BIN" and 0x34 <= off < LOCATION_TABLE_END and len(new) > title_room and not marker:
            sys.exit(f"{row['id']}: location name {len(new)} bytes > {title_room} left in the memory-card title")
        buf = files.setdefault(disc, bytearray(original(disc)))
        assert original(disc)[off:off + len(orig) + 1] == orig + b"\0", row["id"]
        base, hdr = rawtext.FILES[disc]
        room = min(int(row["room"]), ((off - hdr + len(orig) + 1 + 3) & ~3) + hdr - off)
        if len(new) + 1 <= room:
            writes.put(buf, disc, off, new + bytes(max(len(orig), len(new)) + 1 - len(new)), "text " + row["id"])
            continue
        addr = int(row["addr"], 16)
        ptrs = [int(r, 16) for r in row["refs"].split(",") if r not in ("", "-") and "+" not in r]
        bad = [p for p in ptrs if struct.unpack_from("<I", original(disc), p)[0] != addr]
        if not ptrs or bad:
            sys.exit(f"{row['id']}: {len(new)} bytes > {room - 1} in place and no data-word pointer to move it "
                     f"(refs {row['refs']}): shorten it")
        new_addr = free.alloc(len(new) + 1)
        writes.put(files["SLPM_866.02"], "SLPM_866.02", exe_off(new_addr), new + b"\0", "reloc " + row["id"])
        for p in ptrs:
            writes.put(buf, disc, p, struct.pack("<I", new_addr), "ptr " + row["id"])
        writes.put(buf, disc, off, bytes(len(orig) + 1), "vacate " + row["id"])


def patches(qa=None, marker=False, writes=None):
    """{disc path: new bytes}: VWF code, English glyphs, SOL.SRP and raw text. `marker`: the phase-5 marker script.
    `writes` (a Writes) collects the write log for romdiff."""
    writes = writes or Writes()
    sol_orig = (TREE / "DATA" / "SOL.SRP").read_bytes()
    files = {}
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
    writes.runs("DATA/SOL.SRP", files["DATA/SOL.SRP"], "sol")
    moved = sol.remap(sol_orig, files["DATA/SOL.SRP"])
    if moved:
        print(f"SOL.SRP repacked: {len(moved)} block ids remapped in the EXE")
    code, vwf_end = exe([moved.get(i, i) for i in range(max(b for b, _ in sol.header(sol_orig)) + 1)] if moved else [])
    writes.runs("SLPM_866.02", code, "vwf.asm")
    files["SLPM_866.02"] = bytearray(code)
    raw_texts(files, writes, Free(vwf_end, FREE_END), qa, markers.raw_marker if marker else None)
    files["DATA/DATA1.PAC"] = font.patch((TREE / "DATA" / "DATA1.PAC").read_bytes())
    writes.runs("DATA/DATA1.PAC", files["DATA/DATA1.PAC"], "font")
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
    w = Writes()
    files = patches(qa, a.marker, w)
    w.save(Path(a.out))
    print(build(a.out, files))
