"""Render one TIM at full size (every CLUT row stacked, or palette indices as grey).

usage: python -X utf8 tools/timshow.py FILE HEXOFFSET OUT.png [--gray] [--zoom N]
"""
import struct
import sys
from pathlib import Path

from PIL import Image

from timsweep import parse_tim


def clut_rows(d, o):
    """All CLUT rows of the TIM at o (parse_tim draws only the first)."""
    if not struct.unpack_from("<I", d, o + 4)[0] & 8:
        return []
    _, _, _, cw, ch = struct.unpack_from("<IHHHH", d, o + 8)
    return [struct.unpack_from(f"<{cw}H", d, o + 20 + r * cw * 2) for r in range(ch)]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    f, off, out = args[0], int(args[1], 16), Path(args[2])
    zoom = int(sys.argv[sys.argv.index("--zoom") + 1]) if "--zoom" in sys.argv else 1
    if "--zoom" in sys.argv:
        args.remove(str(zoom))
    d = bytearray(Path(f).read_bytes())
    gray = "--gray" in sys.argv
    rows = [None] if gray else clut_rows(d, off) or [None]
    ims = []
    for r in rows:
        if r is not None:  # swap row r into the first CLUT slot so parse_tim draws with it
            struct.pack_into(f"<{len(r)}H", d, off + 20, *r)
        ims.append(parse_tim(bytes(d), off, gray)[3])
    w, h = ims[0].size
    sheet = Image.new("RGB", (w, h * len(ims)), (60, 0, 60))
    for k, im in enumerate(ims):
        bg = Image.new("RGB", im.size, (0, 0, 0))
        bg.paste(im, (0, 0), im)
        sheet.paste(bg, (0, k * h))
    if zoom > 1:
        sheet = sheet.resize((sheet.width * zoom, sheet.height * zoom), Image.NEAREST)
    sheet.save(out)
    print(f"{f} @{off:X}: {w}x{h}, {len(ims)} CLUT row(s) -> {out}")


if __name__ == "__main__":
    main()
