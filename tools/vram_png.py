"""Render a 4bpp region of a PS1 VRAM dump (tools/lua/vramdump.lua) as grey palette indices.

  python -X utf8 tools/vram_png.py DUMP.vram.bin X Y W H OUT.png [--zoom N]
  X, W in 16-bit VRAM words (4 pixels each); Y, H in lines. G2 labels: 832 0 105 224.
"""
import argparse

from PIL import Image


def render(vram, x, y, w, h):
    img = Image.new("L", (w * 4, h))
    px = img.load()
    for j in range(h):
        row = vram[((y + j) * 1024 + x) * 2:((y + j) * 1024 + x + w) * 2]
        for i, b in enumerate(row):
            px[2 * i, j], px[2 * i + 1, j] = (b & 15) * 17, (b >> 4) * 17
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dump")
    ap.add_argument("x", type=int)
    ap.add_argument("y", type=int)
    ap.add_argument("w", type=int)
    ap.add_argument("h", type=int)
    ap.add_argument("out")
    ap.add_argument("--zoom", type=int, default=1)
    a = ap.parse_args()
    img = render(open(a.dump, "rb").read(), a.x, a.y, a.w, a.h)
    img.resize((img.width * a.zoom, img.height * a.zoom), Image.NEAREST).save(a.out)


if __name__ == "__main__":
    main()
