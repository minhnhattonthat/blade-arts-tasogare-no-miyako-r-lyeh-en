"""release.py: gate, build and package one release -> release/Blade_Arts_EN_v<ver>.zip (xdelta patch + README.txt).

    python -X utf8 tools/release.py [--version 1.0] [--force]

Stops at the first failure: plain build (never --marker/--qa-file) -> tests (tools/check.py) -> smoke boot ->
jp_left on every raw-text file (known runs in docs/jp_known/) + a Shift-JIS scan of every built SOL.SRP message ->
qa_gate check on every work/qa/**/manifest.tsv -> textcover -> no unticked docs/polish.md line -> no template
placeholder in README.md -> debug tool off -> xdelta3 patch -> re-apply to the clean .bin and compare -> zip
(ZIP_STORED). Refuses to overwrite an existing version without --force. Never publishes.

Debug tool off: the debug tool is Lua run by the emulator (tools/debug/warp.lua), never written into the disc; the
check is that no Lua, memory card or savestate is among the patched files.
"""
import argparse
import hashlib
import re
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import sol  # noqa: E402
from skill import SKILL  # noqa: E402

PY = [sys.executable, "-X", "utf8"]
ORIG = ROOT / "rom/Blade Arts - Tasogare no Miyako R'lyeh (Japan).bin"
BUILT = ROOT / "build/blade_arts_en.bin"
FILES = ROOT / "build/files"
TREE = ROOT / "work/disc/tree"
RAW_FILES = ["SLPM_866.02", "DATA/STATUS.BIN", "DATA/LOADSAVE.BIN", "DATA/BOSS0P.BIN", "DATA/BOSS3P.BIN",
             "DATA/GAME.BIN"]
JP = re.compile(r"[぀-ヿ㐀-鿿]")


def step(name, cmd):
    print(f"== {name}", flush=True)
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode:
        sys.exit(f"FAILED: {name} (exit {r.returncode})")


def digest(path, algo):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def crc32(path):
    c = 0
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            c = zlib.crc32(b, c)
    return f"{c:08X}"


def sol_japanese(data):
    """[(block, index, text)] of SOL messages still holding kana/kanji. The game reads text in 2-byte units
    (tools/en.py): English pairs start >= 0xA0, control codes are ASCII, Shift-JIS pairs start 0x81-0x9F."""
    left = []
    for bid, _, blk in sol.blocks(data):
        for gi, _, _, _, t in sol.strings(blk):
            s = "".join(t[i:i + 2].decode("shift_jis", "replace") for i in range(0, len(t) - 1, 2)
                        if 0x81 <= t[i] <= 0x9F)
            if JP.search(s):
                left.append((bid, gi, s))
    return left


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--force", action="store_true", help="overwrite this version's existing release files")
    a = ap.parse_args()

    out = ROOT / "release"
    stem = f"Blade_Arts_EN_v{a.version}"
    patch, zpath = out / f"{stem}.xdelta", out / f"{stem}.zip"
    if (patch.exists() or zpath.exists()) and not a.force:
        sys.exit(f"{zpath.name} or {patch.name} exists; pass --force to overwrite")

    step("rom check", PY + ["tools/check_rom.py"])
    step("build", PY + ["build.py"])  # plain build: no --marker, no --qa-file
    step("tests", PY + ["tools/check.py"])
    step("smoke", PY + [f"{SKILL}/scripts/emu.py", "build/blade_arts_en.cue", "--out", "work/qa/smoke", "--route",
                        "tools/routes/boot.txt", "--smoke"])
    for f in RAW_FILES:
        built = FILES / f if (FILES / f).exists() else TREE / f  # an unchanged file is not staged
        known = ROOT / "docs/jp_known" / (f.replace("/", "_") + ".txt")
        step(f"jp_left {f}", PY + [f"{SKILL}/scripts/jp_left.py", str(built), "--orig", str(TREE / f), "--sjis"]
             + (["--known", str(known)] if known.exists() else []))
    print("== jp_left DATA/SOL.SRP", flush=True)
    left = sol_japanese((FILES / "DATA/SOL.SRP").read_bytes())
    for bid, gi, s in left[:20]:
        print(f"  block {bid} #{gi}: {s[:60]}")
    if left:
        sys.exit(f"FAILED: {len(left)} SOL message(s) still hold Japanese")
    manifests = sorted((ROOT / "work/qa").rglob("manifest.tsv"))
    if not manifests:
        sys.exit("FAILED: no work/qa/**/manifest.tsv")
    for m in manifests:
        step(f"qa_gate {m.parent.relative_to(ROOT)}", PY + [f"{SKILL}/scripts/qa_gate.py", "check", str(m),
                                                            str(m.parent / "verdicts")])
    step("textcover", PY + [f"{SKILL}/scripts/textcover.py", "work/qa", "build/strings.tsv"])

    print("== polish / README / debug", flush=True)
    open_lines = [ln for ln in (ROOT / "docs/polish.md").read_text(encoding="utf-8").splitlines()
                  if ln.startswith("- [ ]")]
    if open_lines:
        sys.exit(f"FAILED: {len(open_lines)} unticked line(s) in docs/polish.md")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    holes = re.findall(r"<(?:Game title|platform|publisher|year|repo|file|size|sha1|game)>|<[A-Z][a-z]+ /", readme)
    if holes:
        sys.exit(f"FAILED: template placeholders in README.md: {holes}")
    sha1 = digest(ORIG, "sha1")
    zip_readme = (ROOT / "docs/release-README.txt").read_text(encoding="utf-8")
    for doc, name in ((readme, "README.md"), (zip_readme, "docs/release-README.txt")):
        if sha1 not in doc:
            sys.exit(f"FAILED: {name} lacks the base image SHA-1 {sha1}")
    debug = [p for p in FILES.rglob("*") if p.suffix.lower() in (".lua", ".mcd", ".sstate")]
    if debug:
        sys.exit(f"FAILED: debug files in the build: {debug}")

    out.mkdir(exist_ok=True)
    size = str(ORIG.stat().st_size)  # -B: match across the whole image (default window is 64 MB)
    patch.unlink(missing_ok=True)
    step(f"xdelta3 encode -> {patch.name}", ["xdelta3", "-e", "-9", "-B", size, "-s", str(ORIG), str(BUILT),
                                             str(patch)])
    check = out / "reapplied.bin"
    check.unlink(missing_ok=True)
    step("xdelta3 re-apply", ["xdelta3", "-d", "-B", size, "-s", str(ORIG), str(patch), str(check)])
    built_sha1 = digest(BUILT, "sha1")
    if digest(check, "sha1") != built_sha1:
        sys.exit(f"FAILED: re-applied patch differs from {BUILT.relative_to(ROOT)}")
    check.unlink()

    text = (zip_readme.replace("{VERSION}", a.version).replace("{PATCH}", patch.name)
            .replace("{PATCHED_SHA1}", built_sha1).replace("{PATCHED_CRC32}", crc32(BUILT)))
    if re.search(r"\{[A-Z_0-9]+\}", text):
        sys.exit("FAILED: unfilled {FIELD} in docs/release-README.txt")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_STORED) as z:
        z.write(patch, patch.name)
        z.writestr("README.txt", text.replace("\n", "\r\n"))
    print(f"OK {zpath.relative_to(ROOT)}: {patch.name} ({patch.stat().st_size:,} B) + README.txt; "
          f"patched sha1 {built_sha1}")


if __name__ == "__main__":
    main()
