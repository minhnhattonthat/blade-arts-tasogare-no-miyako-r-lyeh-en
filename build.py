"""build.py: rebuild the disc from work/disc/tree with patched files -> build/blade_arts_en.bin/.cue.

Patched files are written to build/files/<disc path> and swapped in through a generated layout (mkpsxiso `source=`),
so the dumped tree stays pristine. With no patches the output is byte-identical to the original (tests/test_identity.py).
"""
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import check_rom  # noqa: E402

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


def patches():
    """{disc path ('DATA/SOL.SRP'): new bytes}. Empty until insertion exists (phase 7)."""
    return {}


def build(out=OUT, files=None):
    """Write <out>/<NAME>.bin/.cue; `files` overrides disc files ({path: bytes}). Returns the .bin path."""
    check_rom.check()
    unpack()
    files = patches() if files is None else files
    out = Path(out)
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
    print(build())
