"""Draw the English graphics-text pictures into gfx/<name>.png (read by build.py through tools/gfx.py).

  python -X utf8 tools/gfx_draw.py [NAME..]     all rows of gfx/gfx.tsv that have a drawer, or the named ones

Each drawer starts from the original TIM (tools/gfx.py export), clears declared rects and letters the English with
OFL fonts from fonts/ofl (docs/fonts.md). Wording: glossary.md. Prints each clear rect for rectcover.py.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import gfx

ROOT = gfx.ROOT
OFL = ROOT / "fonts" / "ofl"


def font(name, size, weight=None):
    f = ImageFont.truetype(str(OFL / name), size)
    if weight:
        f.set_variation_by_axes([weight])
    return f


def clear_vertical(im, rect, pad=2):
    """Fill rect (x, y, w, h) by blending, per column, the rows just above and below it: keeps vertical structures
    (the sword behind the title subtitle) and dark gradients."""
    px = im.load()
    x, y, w, h = rect
    for cx in range(x, x + w):
        top = [px[cx, y - 1 - k] for k in range(pad)]
        bot = [px[cx, y + h + k] for k in range(pad)]
        a = tuple(sum(c[i] for c in top) // pad for i in range(4))
        b = tuple(sum(c[i] for c in bot) // pad for i in range(4))
        for cy in range(y, y + h):
            t = (cy - y + 1) / (h + 1)
            px[cx, cy] = tuple(round(a[i] * (1 - t) + b[i] * t) for i in range(4))


def glow_text(im, centre, text, f, fill=(240, 240, 240), glow=(150, 120, 200), radius=2):
    """White text with a soft coloured glow, centred on `centre` (x, y): the title's lettering style."""
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = d.textbbox((0, 0), text, font=f)
    pos = (centre[0] - (x1 - x0) // 2 - x0, centre[1] - (y1 - y0) // 2 - y0)
    halo = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(halo).text(pos, text, font=f, fill=glow + (255,))
    halo = halo.filter(ImageFilter.GaussianBlur(radius))
    out = Image.alpha_composite(im, halo)
    d = ImageDraw.Draw(out)
    d.text(pos, text, font=f, fill=fill + (255,))
    bbox = d.textbbox(pos, text, font=f)
    return out, bbox


def title(im):
    rects = [(74, 231, 170, 24), (68, 426, 188, 23)]
    for r in rects:
        clear_vertical(im, r)
    im, b1 = glow_text(im, (160, 242), "R'lyeh, City of Twilight", font("cinzel_Cinzel[wght].ttf", 17, 600))
    im, b2 = glow_text(im, (160, 437), "© Ea Co.,Ltd / Nobuteru Yuki / ENIX 2000",
                       font("lato_Lato-Regular.ttf", 11), glow=(40, 40, 60), radius=1)
    return im, rects, [b1, b2]


def ramp_text(im, rect, text, f, align="right"):
    """Indexed (P) picture: clear rect to its most common index and draw text antialiased with the indices the
    original text in the rect used, each pixel taking the index whose preview luminance is nearest the blend of
    background and ink (ink = the used index farthest from the background)."""
    x, y, w, h = rect
    px = im.load()
    pal = im.getpalette()
    lum = [0.3 * pal[3 * i] + 0.59 * pal[3 * i + 1] + 0.11 * pal[3 * i + 2] for i in range(len(pal) // 3)]
    used = {}
    for cy in range(y, y + h):
        for cx in range(x, x + w):
            used[px[cx, cy]] = used.get(px[cx, cy], 0) + 1
    bg = max(used, key=used.get)
    ink = max(used, key=lambda i: abs(lum[i] - lum[bg]))
    levels = sorted(used, key=lambda i: lum[i])
    for cy in range(y, y + h):
        for cx in range(x, x + w):
            px[cx, cy] = bg
    mask = Image.new("L", (w, h))
    d = ImageDraw.Draw(mask)
    x0, y0, x1, y1 = d.textbbox((0, 0), text, font=f)
    if x1 - x0 > w or y1 - y0 > h:
        sys.exit(f"{text!r}: {x1 - x0}x{y1 - y0} px > rect {w}x{h}")
    tx = {"right": w - x1, "left": -x0, "centre": (w - (x1 - x0)) // 2 - x0}[align]
    d.text((tx, (h - (y1 - y0)) // 2 - y0), text, font=f, fill=255)
    for (cx, cy), v in zip(((i % w, i // w) for i in range(w * h)), mask.getdata()):
        if v:
            want = lum[bg] + (lum[ink] - lum[bg]) * v / 255
            px[x + cx, y + cy] = min(levels, key=lambda i: abs(lum[i] - want))
    return [rect]


def thanks(im):
    # 4bpp, CLUT row 1: "2000年 夏 発売予定" ("on sale summer 2000")
    return im, ramp_text(im, (760, 0, 240, 24), "On Sale Summer 2000", font("cinzel_Cinzel[wght].ttf", 19, 400)), []


PRESTAGE = (lambda: font("crimsontext_CrimsonText-Regular.ttf", 15), "Prestage")  # G6: the other credit names are a plain serif


def prestage(im):
    # M02_10_0 intro credits texture: プレステージ (company) at 160,0 in the 96x16 cell; also alone in M03_01_0
    return im, ramp_text(im, (160, 0, 96, 16), PRESTAGE[1], PRESTAGE[0](), align="left"), []


def prestage2(im):
    return im, ramp_text(im, (0, 0, 96, 16), PRESTAGE[1], PRESTAGE[0](), align="left"), []


DRAWERS = {"title": title, "thanks": thanks, "prestage": prestage, "prestage2": prestage2}


def main():
    names = sys.argv[1:] or [r["name"] for r in gfx.rows() if r["name"] in DRAWERS]
    for row in gfx.rows():
        if row["name"] not in names:
            continue
        d = (gfx.TREE / row["file"]).read_bytes()
        orig = gfx.export(d, int(row["offset"], 16), int(row["clut"] or 0))
        im, rects, boxes = DRAWERS[row["name"]](orig.copy() if orig.mode == "P" else orig.convert("RGBA"))
        if orig.mode == "RGBA":
            # 16bpp: opaque everywhere the original was (the composite keeps alpha), transparent black stays 0
            im = Image.composite(im, orig, orig.getchannel("A"))
        out = ROOT / "gfx" / (row["name"] + ".png")
        im.save(out)
        print(out.name, "clear", " ".join("%d,%d,%d,%d" % r for r in rects), "text bboxes", boxes)


if __name__ == "__main__":
    main()
