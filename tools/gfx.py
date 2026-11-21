"""Graphics text (docs/re/graphics.md): TIM <-> PNG and the build's image writes.

  python -X utf8 tools/gfx.py export FILE HEXOFF OUT.png [--clut N]   4/8bpp -> indexed PNG (palette = CLUT row N),
                                                                      16bpp -> RGBA PNG
  python -X utf8 tools/gfx.py orig NAME                               export gfx.tsv row NAME to work/gfx/orig/NAME.png

`gfx/gfx.tsv` (name, file, offset, copies, clut, note): the English picture `gfx/<name>.png` replaces the pixel block
of the TIM at file@offset and at every copy (`FILE@HEX,...`, same size and depth; checked against the first one's
original pixels). Indexed PNGs keep their palette indices as is: draw with the TIM's own indices (the PNG palette is
only the preview colours of CLUT row `clut`).
"""
import csv
import struct
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TREE = ROOT / "work" / "disc" / "tree"
TSV = ROOT / "gfx" / "gfx.tsv"
COLS = ["name", "file", "offset", "copies", "clut", "note"]


def tim(d, o):
    """(mode 0/1/2, clut rows, pixel offset, pixel byte count, width px, height)."""
    magic, flags = struct.unpack_from("<II", d, o)
    if magic != 0x10 or (flags & 7) > 2:
        raise ValueError(f"no 4/8/16bpp TIM at {o:#x}")
    p, rows = o + 8, []
    if flags & 8:
        blen, _, _, cw, ch = struct.unpack_from("<IHHHH", d, p)
        rows = [struct.unpack_from(f"<{cw}H", d, p + 12 + r * cw * 2) for r in range(ch)]
        p += blen
    blen, _, _, iw, ih = struct.unpack_from("<IHHHH", d, p)
    mode = flags & 7
    return mode, rows, p + 12, iw * ih * 2, iw * (4, 2, 1)[mode], ih


def rgb(c):
    return (c & 31) * 255 // 31, (c >> 5 & 31) * 255 // 31, (c >> 10 & 31) * 255 // 31


def export(d, o, clut=0):
    mode, rows, p, n, w, h = tim(d, o)
    pix = d[p:p + n]
    if mode == 2:
        im = Image.new("RGBA", (w, h))
        im.putdata([rgb(c) + (255 if c else 0,) for c in struct.unpack_from(f"<{n // 2}H", pix)])
        return im
    idx = [v for b in pix for v in (b & 15, b >> 4)] if mode == 0 else list(pix)
    im = Image.new("P", (w, h))
    im.putdata(idx)
    pal = [v for c in rows[clut] for v in rgb(c)] if rows else [v for i in range(256) for v in (i, i, i)]
    im.putpalette(pal + [0] * (768 - len(pal)))
    return im


def pixels(d, o, im):
    """The TIM's new pixel bytes from an edited PNG (export's format; 16bpp keeps the original halfword, STP bit
    included, wherever the colour is unchanged)."""
    mode, rows, p, n, w, h = tim(d, o)
    if im.size != (w, h):
        raise ValueError(f"PNG is {im.size}, TIM is {w}x{h}")
    if mode == 2:
        old = struct.unpack_from(f"<{n // 2}H", d, p)
        out = []
        for c, (r, g, b, a) in zip(old, im.convert("RGBA").getdata()):
            new = 0 if a < 128 else (r >> 3 | g >> 3 << 5 | b >> 3 << 10) or 0x8000  # opaque black needs STP
            out.append(c if rgb(c) + (255 if c else 0,) == (r, g, b, a) else new)
        return struct.pack(f"<{len(out)}H", *out)
    if im.mode != "P":
        raise ValueError("indexed TIM needs an indexed (P mode) PNG")
    idx = list(im.getdata())
    if max(idx) >= (16 if mode == 0 else 256):
        raise ValueError(f"palette index {max(idx)} out of range")
    if mode == 1:
        return bytes(idx)
    return bytes(idx[i] | idx[i + 1] << 4 for i in range(0, len(idx), 2))


def rows():
    if not TSV.exists():
        return []
    with TSV.open(encoding="utf-8", newline="") as f:
        out = [r for r in csv.reader(f, delimiter="\t") if r and not r[0].startswith("#")]
    assert out[0] == COLS, out[0]
    for r in out[1:]:
        assert len(r) == len(COLS), r
    return [dict(zip(COLS, r)) for r in out[1:]]


def targets(row):
    t = [(row["file"], int(row["offset"], 16))]
    for c in filter(None, row["copies"].split(",")):
        f, o = c.split("@")
        t.append((f, int(o, 16)))
    return t


def patch(files, writes, original):
    """Write every gfx/<name>.png that exists into `files` ({disc path: bytearray}) through `writes`."""
    for row in rows():
        png = ROOT / "gfx" / (row["name"] + ".png")
        if not png.exists():
            continue
        f0, o0 = targets(row)[0]
        new = pixels(original(f0), o0, Image.open(png))
        _, _, p0, n0, _, _ = tim(original(f0), o0)
        for f, o in targets(row):
            d = original(f)
            _, _, p, n, _, _ = tim(d, o)
            if d[p:p + n] != original(f0)[p0:p0 + n0]:
                sys.exit(f"gfx {row['name']}: copy {f}@{o:X} differs from {f0}@{o0:X}")
            buf = files.setdefault(f, bytearray(d))
            writes.put(buf, f, p, new, "gfx " + row["name"])


def main():
    a = [x for x in sys.argv[1:]]
    clut = int(a[a.index("--clut") + 1]) if "--clut" in a else 0
    if a[0] == "export":
        export((TREE / a[1]).read_bytes() if not Path(a[1]).exists() else Path(a[1]).read_bytes(),
               int(a[2], 16), clut).save(a[3])
    elif a[0] == "orig":
        row = next(r for r in rows() if r["name"] == a[1])
        out = ROOT / "work" / "gfx" / "orig" / (a[1] + ".png")
        out.parent.mkdir(parents=True, exist_ok=True)
        export((TREE / row["file"]).read_bytes(), int(row["offset"], 16), int(row["clut"] or 0)).save(out)
        print(out)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
