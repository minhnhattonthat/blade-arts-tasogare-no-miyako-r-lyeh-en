"""timsweep/timshow: grey mode shows pixels behind an all-black CLUT; clut_rows returns every CLUT row."""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from timsweep import parse_tim  # noqa: E402
from timshow import clut_rows  # noqa: E402


def tim4(rows):
    """4bpp TIM, 8x2 pixels, len(rows) CLUT rows of 16 colours."""
    clut = b"".join(struct.pack("<16H", *r) for r in rows)
    pix = bytes([0x21, 0x43, 0x65, 0x87] * 2)
    return (struct.pack("<II", 0x10, 8) + struct.pack("<IHHHH", 12 + len(clut), 0, 480, 16, len(rows)) + clut
            + struct.pack("<IHHHH", 12 + len(pix), 0, 0, 2, 2) + pix)


def test_gray_reveals_black_clut():
    d = tim4([[0] * 16])
    _, w, h, im, _ = parse_tim(d, 0)
    assert (w, h) == (8, 2) and max(im.convert("L").getdata()) == 0
    _, w, _, im, _ = parse_tim(d, 0, gray=True)
    assert w == 8 and list(im.convert("L").getdata())[:8] == [17, 34, 51, 68, 85, 102, 119, 136]


def test_clut_rows():
    rows = [[k] * 16 for k in (1, 2, 3)]
    assert [r[0] for r in clut_rows(tim4(rows), 0)] == [1, 2, 3]
