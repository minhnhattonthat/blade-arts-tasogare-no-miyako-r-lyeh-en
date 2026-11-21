"""Phase 5 engine: English codec, font glyphs, VWF hooks (run under unicorn with exact-PC stops), SOL reflow."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import en  # noqa: E402
import font  # noqa: E402
import sol  # noqa: E402

HAVE_TREE = (build.TREE / "SLPM_866.02").is_file()
need_tree = pytest.mark.skipif(not HAVE_TREE, reason="no unpacked disc (work/disc/tree)")


def test_encode_pairs_and_codes():
    assert en.encode("{CSA0t0}Ab c") == b"CSA0t0" + bytes([0xC1, 0xE2, 0xA0, 0xE3])
    assert en.encode("A\\\\B") == bytes([0xC1, 0x80]) + b"\\\\" + bytes([0xC2, 0x80])
    assert en.encode("{%s}: x") == b"%s" + bytes([0xBA, 0xA0, 0xF8, 0x80])
    assert en.width("AB") == en.WIDTH["A"] + en.WIDTH["B"]
    with pytest.raises(ValueError):
        en.encode("{abc}")
    with pytest.raises(ValueError):
        en.encode("a_b")  # not in the font


@need_tree
def test_font_patch_keeps_japanese_glyphs():
    orig = (build.TREE / "DATA" / "DATA1.PAC").read_bytes()
    new = font.patch(orig)
    pix = font.tim_pixels(orig)
    assert all(font.cell(pix, orig, i) == font.cell(pix, new, i) for i in range(en.FIRST_SLOT))
    assert len(new) == len(orig) and new[:pix] == orig[:pix]


@pytest.fixture(scope="module")
def emu():
    unicorn = pytest.importorskip("unicorn")
    from unicorn import mips_const as m
    if not HAVE_TREE:
        pytest.skip("no unpacked disc")
    exe = build.exe()

    class Kseg0:  # unicorn runs kseg0 code but maps memory physically: strip the 0x80000000
        def __init__(self, uc):
            self.uc = uc

        def mem_write(self, a, d):
            self.uc.mem_write(a & 0x1FFFFFFF, d)

        def mem_read(self, a, n):
            return self.uc.mem_read(a & 0x1FFFFFFF, n)

        def __getattr__(self, name):
            return getattr(self.uc, name)

    u = Kseg0(unicorn.Uc(unicorn.UC_ARCH_MIPS, unicorn.UC_MODE_MIPS32 | unicorn.UC_MODE_LITTLE_ENDIAN))
    u.mem_map(0, 0x200000)
    u.mem_write(0x80010000, exe[0x800:])
    return u, m


def run(u, m, pc, stop, regs):
    for r, v in regs.items():
        u.reg_write(getattr(m, "UC_MIPS_REG_" + r.upper()), v)
    u.emu_start(pc, stop, count=2000)
    assert u.reg_read(m.UC_MIPS_REG_PC) == stop


WIN, TEXT, REC = 0x80100000, 0x80101000, 0x80102000


def window(u, x=10, y=20):
    w = bytearray(0xD4)
    struct.pack_into("<hh", w, 0x2E, 0, 200)          # records used / max
    struct.pack_into("<H", w, 0x22, 0x1234)
    struct.pack_into("<I", w, 0x18, 0xCAFE0000)
    struct.pack_into("<hh", w, 0x4C, x, y)
    u.mem_write(WIN, bytes(w))
    u.mem_write(0x800E66B4, struct.pack("<h", 0x3F00))  # font CLUT base


def test_vwf_english_pair_makes_two_records(emu):
    u, m = emu
    window(u)
    u.mem_write(TEXT, en.encode("Hi"))
    run(u, m, 0x800167F8, 0x800169B8, {"s0": WIN, "s1": TEXT, "s2": REC, "s3": 1})
    g, _ = en.tables()
    recs = [struct.unpack_from("<hhhHIII", u.mem_read(REC + 20 * k, 20)) for k in range(2)]
    assert [r[6] for r in recs] == [g[ord("H")] + (0x3F00 << 16), g[ord("i")] + (0x3F00 << 16)]
    assert recs[0][5] == 10 | 20 << 16 and recs[1][5] == 10 + en.WIDTH["H"] | 20 << 16
    assert recs[0][3] == 0x1234 and recs[0][4] == 0xCAFE0000
    assert struct.unpack("<hh", u.mem_read(WIN + 0x4C, 4)) == (10 + en.WIDTH["H"] + en.WIDTH["i"], 20)
    assert struct.unpack("<h", u.mem_read(WIN + 0x2E, 2))[0] == 2
    assert u.reg_read(m.UC_MIPS_REG_S2) == REC + 40


def test_vwf_space_and_pad_draw_nothing(emu):
    u, m = emu
    window(u)
    u.mem_write(TEXT, en.encode(" "))  # space + pad
    run(u, m, 0x800167F8, 0x800169B8, {"s0": WIN, "s1": TEXT, "s2": REC, "s3": 1})
    assert struct.unpack("<h", u.mem_read(WIN + 0x2E, 2))[0] == 0
    assert struct.unpack("<h", u.mem_read(WIN + 0x4C, 2))[0] == 10 + en.SPACE_W


def test_vwf_japanese_takes_original_path(emu):
    u, m = emu
    window(u)
    u.mem_write(TEXT, "あ".encode("cp932"))
    run(u, m, 0x800167F8, 0x80016800, {"s0": WIN, "s1": TEXT, "s2": REC})
    assert u.reg_read(m.UC_MIPS_REG_V1) == 0xFFFFA082 and u.reg_read(m.UC_MIPS_REG_V0) == 0x4081


def test_measure_counts_letter_widths(emu):
    u, m = emu
    u.mem_write(TEXT, en.encode("Hi"))
    run(u, m, 0x8001602C, 0x8001604C, {"s1": WIN, "a1": TEXT, "s2": 100})
    assert u.reg_read(m.UC_MIPS_REG_S2) == 100 + en.WIDTH["H"] + en.WIDTH["i"]


@need_tree
def test_sol_reflow_keeps_order_and_sectors():
    orig = (build.TREE / "DATA" / "SOL.SRP").read_bytes()
    # the multi-sector block with the most free bytes: grow its first string past its sector, within the block
    def free(blk):
        return len(blk) - sum(sol.string_size(x) + 2 for *_, x in sol.strings(blk))
    bid, blk = max(((b, k) for b, _, k in sol.blocks(orig) if len(k) > sol.SECTOR), key=lambda t: free(t[1]))
    gi, s, o, flags, x = next(sol.strings(blk))
    texts = {(bid, gi): x + en.encode("x" * (sol.SECTOR // 2))}
    assert free(blk) > sol.SECTOR // 2 + 64
    new = sol.pack(orig, texts)
    assert len(new) == len(orig)
    for (bid, pos, blk), (_, _, nblk) in zip(sol.blocks(orig), sol.blocks(new)):
        assert len(blk) == len(nblk)
        got = [(gi, x) for gi, s, o, f, x in sol.strings(nblk)]
        want = [(gi, texts.get((bid, gi), x)) for gi, s, o, f, x in sol.strings(blk)]
        assert got == want, bid
