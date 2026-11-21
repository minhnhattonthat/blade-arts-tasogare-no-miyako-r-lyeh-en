"""Phase-7 build check on the shipped English: every write is logged with the right original bytes and no overlap
(romdiff.py --writes), whole-file rewrites stay in their allowed regions, and the built SOL.SRP holds exactly the en
column, with moved blocks reached through the EXE's sol_map."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import romdiff  # noqa: E402
import sol  # noqa: E402

pytestmark = pytest.mark.skipif(not (build.TREE / "SLPM_866.02").is_file(), reason="no unpacked disc (work/disc/tree)")

HOOKS = {0x800B7DB0: 4, 0x800167F8: 8, 0x8001602C: 8, 0x8003796C: 4}  # asm/vwf.asm .org sites outside the free area


@pytest.fixture(scope="module")
def built():
    w = build.Writes()
    return build.patches(writes=w), w.log


def test_writes_match_romdiff(built):
    files, log = built
    for disc, new in files.items():
        errs, _ = romdiff.check(build.original(disc), new, [], log[disc])
        assert not errs, (disc, errs[:5])


def test_exe_writes_in_free_area_or_hooks(built):
    _, log = built
    for off, a, b, by in log["SLPM_866.02"]:
        addr = off - build.EXE_HDR + build.EXE_BASE
        if by == "vwf.asm" or by.startswith("reloc"):
            hook = any(h <= addr and addr + len(b) <= h + n for h, n in HOOKS.items())
            assert hook or 0x800B8128 <= addr and addr + len(b) <= build.FREE_END, (hex(addr), by)


def test_font_writes_in_font_entries(built):
    _, log = built
    pac = build.original("DATA/DATA1.PAC")
    spans = [(s * 0x800, s * 0x800 + n) for s, n in (struct.unpack_from("<II", pac, 8 + 8 * e) for e in (118, 119))]
    for off, a, b, by in log["DATA/DATA1.PAC"]:
        assert any(lo <= off and off + len(b) <= hi for lo, hi in spans), hex(off)


def test_sol_holds_en_and_map_reaches_moved_blocks(built):
    files, _ = built
    orig, new = build.original("DATA/SOL.SRP"), files["DATA/SOL.SRP"]
    moved = sol.remap(orig, new)
    assert all(n * sol.SECTOR >= len(orig) for n in moved.values())  # appended; every other block keeps its id
    back = {n: o for o, n in moved.items()}
    got = {(back.get(b, b), gi): x for b, _, blk in sol.blocks(new) for gi, s, o, f, x in sol.strings(blk)}
    want = {(b, gi): x for b, _, blk in sol.blocks(orig) for gi, s, o, f, x in sol.strings(blk)}
    want.update(build.sol_texts())
    assert got == want
    if moved:
        sym = {ln.split()[1]: int(ln.split()[0], 16) for ln in (build.OUT / "asm/vwf.sym").read_text().splitlines()
               if len(ln.split()) == 2}
        exe, base = files["SLPM_866.02"], build.exe_off(sym["sol_map"])
        n = max(b for b, _ in sol.header(orig)) + 1
        assert list(struct.unpack_from(f"<{n}H", exe, base)) == [moved.get(i, i) for i in range(n)]


def test_sol_pack_appends_a_block_that_outgrows_its_sectors():
    orig = build.original("DATA/SOL.SRP")
    bid, _, blk = next(b for b in sol.blocks(orig) if len(b[2]) == sol.SECTOR)
    texts = {(bid, gi): x + b"\xe1" * 600 for gi, s, o, f, x in sol.strings(blk)}
    new = sol.pack(orig, texts)
    moved = sol.remap(orig, new)
    assert list(moved) == [bid] and moved[bid] == len(orig) // sol.SECTOR
    got = {gi: x for b, _, k in sol.blocks(new) if b == moved[bid] for gi, s, o, f, x in sol.strings(k)}
    assert got == {gi: t for (b, gi), t in texts.items()}
    assert new[sol.SECTOR:len(orig)] == orig[sol.SECTOR:]  # only the header changes before the end
