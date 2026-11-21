"""Graphics-text static sweep: find every PS1 TIM in the given files, render each with its first CLUT, and write
numbered contact sheets plus an index (sheet, cell, file, offset, bpp, size) for a reviewer to list Japanese cells.

usage: python -X utf8 tools/timsweep.py OUTDIR FILE.. [--min 16]
Skipped candidates are printed with the reason (never dropped silently).
"""
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw

CELL = 256


def parse_tim(d, o):
    """Return (bpp, w, h, pixels_rgba Image, end) or raise ValueError."""
    magic, flags = struct.unpack_from("<II", d, o)
    if magic != 0x10 or flags & ~0xF or (flags & 7) > 3:
        raise ValueError("not a TIM")
    mode, has_clut = flags & 7, flags & 8
    p = o + 8
    clut = None
    if has_clut:
        blen, cx, cy, cw, ch = struct.unpack_from("<IHHHH", d, p)
        if blen != 12 + cw * ch * 2 or cw == 0 or ch == 0 or blen > 0x20000:
            raise ValueError("bad clut")
        clut = struct.unpack_from(f"<{cw}H", d, p + 12)
        p += blen
    blen, ix, iy, iw, ih = struct.unpack_from("<IHHHH", d, p)
    if blen != 12 + iw * ih * 2 or iw == 0 or ih == 0 or ix >= 1024 or iy >= 512:
        raise ValueError("bad image block")
    pix = d[p + 12:p + blen]
    if len(pix) < iw * ih * 2:
        raise ValueError("truncated")
    if mode in (0, 1) and not clut:
        raise ValueError("indexed without clut")

    def rgb(c):
        return ((c & 31) * 255 // 31, (c >> 5 & 31) * 255 // 31, (c >> 10 & 31) * 255 // 31, 255 if c else 0)

    if mode == 0:
        w, out = iw * 4, []
        for b in pix:
            out += [rgb(clut[b & 15]), rgb(clut[b >> 4 & 15])] if len(clut) >= 16 else [(b & 15) * 17] * 2
    elif mode == 1:
        w, out = iw * 2, [rgb(clut[b]) if b < len(clut) else (255, 0, 255, 255) for b in pix]
    elif mode == 2:
        w, out = iw, [rgb(c) for c in struct.unpack_from(f"<{iw * ih}H", pix)]
    else:
        w = iw * 2 // 3
        out = [tuple(pix[i:i + 3]) + (255,) for i in range(0, w * 3 * ih, 3)]
    im = Image.new("RGBA", (w, ih))
    im.putdata([c if isinstance(c, tuple) else (c, c, c, 255) for c in out])
    return 4 if mode == 0 else 8 if mode == 1 else 16 if mode == 2 else 24, w, ih, im, p + blen


def find_tims(d):
    o = 0
    while True:
        o = d.find(b"\x10\x00\x00\x00", o)
        if o < 0 or o + 20 > len(d):
            return
        try:
            yield (o,) + parse_tim(d, o)
        except (ValueError, struct.error) as e:
            if str(e) not in ("not a TIM",):
                pass
        o += 4


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = Path(args[0])
    out.mkdir(parents=True, exist_ok=True)
    cells, index = [], []
    for f in args[1:]:
        d = Path(f).read_bytes()
        n = 0
        for o, bpp, w, h, im, end in find_tims(d):
            if w < 16 or h < 8:
                print(f"skip {f} @{o:X}: {w}x{h} too small")
                continue
            cells.append((f, o, bpp, w, h, im))
            n += 1
        print(f"{f}: {n} TIMs")
    per = 12
    for s in range(0, len(cells), per):
        sheet = Image.new("RGB", (CELL * 4, (CELL + 12) * 3), (60, 0, 60))
        dr = ImageDraw.Draw(sheet)
        for k, (f, o, bpp, w, h, im) in enumerate(cells[s:s + per]):
            x, y = (k % 4) * CELL, (k // 4) * (CELL + 12)
            t = im.copy()
            t.thumbnail((CELL - 2, CELL - 2), Image.NEAREST if max(w, h) <= CELL else Image.LANCZOS)
            bg = Image.new("RGB", t.size, (0, 0, 0))
            bg.paste(t, (0, 0), t)
            sheet.paste(bg, (x + 1, y + 12))
            dr.text((x + 2, y), f"{s + k}", fill=(255, 255, 0))
            index.append(f"{s // per:04d}\t{s + k}\t{Path(f).as_posix()}\t{o:X}\t{bpp}\t{w}x{h}")
        sheet.save(out / f"sheet_{s // per:04d}.png")
    (out / "index.tsv").write_text("sheet\tcell\tfile\toffset\tbpp\tsize\n" + "\n".join(index) + "\n", encoding="utf-8")
    print(f"{len(cells)} TIMs, {(len(cells) + per - 1) // per} sheets -> {out}")


if __name__ == "__main__":
    main()
