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


# G7 stage-clear cards M50_00..13 (card n: stage name, next stage name), names = LOADSAVE location names
CARDS = [("Underground Channel", "Gravity Elevator Lower"), ("Prestage", "Jungle"), ("Jungle", "Ruins"),
         ("Ruins", "Gravity Elevator Upper"), ("Gravity Elevator Upper", "Gravity Elevator Lower"),
         ("Gravity Elevator Lower", "Underground City"), ("Underground City", "Waterway"),
         ("Waterway", "Research Ruins"), ("Research Ruins", "Cave of Illusions"),
         ("Cave of Illusions", "Temple of the Sword"), ("Temple of the Sword", "Basetet"), ("Basetet", "R'lyeh"),
         ("R'lyeh", "Primordial One"), ("Primordial One", "Primordial One")]


def fit(name, size, text, w, h, weight=None):
    """Largest font size <= size whose text box fits w x h."""
    while size > 6:
        f = font(name, size, weight)
        x0, y0, x1, y1 = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), text, font=f)
        if x1 - x0 <= w and y1 - y0 <= h:
            return f
        size -= 1
    sys.exit(f"{text!r} does not fit {w}x{h}")


# The cards' TIM CLUT is all 0x8000; the game builds the real one. Fitted from JP shots (tools/clutfit.py): card 00
# is a plain ramp 0 white .. 15 black; cards 01-13 use a shuffled ramp (card 09 shot; index 0 never used, 15 black).
RAMP_00 = [(255 - 17 * i,) * 3 for i in range(16)]
RAMP_SHUFFLED = [(0, 0, 0), (8, 8, 8), (213, 213, 164), (74, 74, 57), (106, 106, 82), (246, 246, 189),
                 (156, 156, 115), (123, 123, 90), (90, 90, 65), (57, 57, 41), (139, 139, 98), (24, 24, 16),
                 (197, 205, 148), (180, 189, 139), (164, 172, 123), (0, 0, 0)]
# the NEXT STAGE row is drawn with another CLUT: card 00 (blue) and cards 01-13 (teal; cards 04 and 09 fitted)
NEXT_00 = [(0, 0, 0), (8, 8, 8), (16, 24, 24), (57, 65, 74), (90, 106, 123), (148, 172, 197), (131, 156, 180),
           (41, 49, 57), (74, 90, 106), (172, 197, 230), (115, 131, 156), (156, 180, 213), (98, 115, 139),
           (65, 74, 90), (32, 32, 41), (0, 0, 0)]
NEXT_SHUFFLED = [(0, 0, 0), (8, 8, 8), (41, 57, 49), (57, 74, 65), (90, 123, 106), (123, 164, 148), (139, 180, 164),
                 (148, 197, 180), (65, 90, 82), (164, 213, 197), (180, 238, 222), (98, 131, 123), (115, 148, 139),
                 (32, 41, 41), (16, 24, 24), (0, 0, 0)]


def putpal(im, colours):
    im.putpalette([v for c in colours for v in c])


def smear(im, rect, text, f, gauss, levels):
    """The card's blurred copy of the name above the sharp one (shown as it slides in): gaussian for M50_00, a
    horizontal streak over a faint copy for the others. Background 15, each pixel the level nearest its brightness."""
    x, y, w, h = rect
    mask = Image.new("L", (w, h))
    d = ImageDraw.Draw(mask)
    x0, y0, x1, y1 = d.textbbox((0, 0), text, font=f)
    d.text(((w - (x1 - x0)) // 2 - x0, (h - (y1 - y0)) // 2 - y0), text, font=f, fill=255)
    if gauss:
        out = mask.filter(ImageFilter.GaussianBlur(3)).point(lambda v: min(255, v * 2))
    else:
        streak = mask.resize((max(1, w // 8), h), Image.BILINEAR).resize((w, h), Image.BILINEAR)
        out = Image.blend(streak.point(lambda v: min(255, v * 3)), mask, 0.4)
    pal = im.getpalette()
    lum = {i: 0.3 * pal[3 * i] + 0.59 * pal[3 * i + 1] + 0.11 * pal[3 * i + 2] for i in levels}
    top = max(lum.values())
    px = im.load()
    for (cx, cy), v in zip(((i % w, i // w) for i in range(w * h)), out.getdata()):
        px[x + cx, y + cy] = min(levels, key=lambda i: abs(lum[i] - top * v / 255))
    return [rect]


def card(n):
    def draw(im):
        name, nxt = CARDS[n]
        putpal(im, NEXT_00 if n == 0 else NEXT_SHUFFLED)  # ramp_text and smear pick indices by these colours
        serif = "crimsontext_CrimsonText-Regular.ttf"
        top = (101, 1, 131, 15) if n == 0 else (110, 1, 122, 15)  # card 0's NEXT STAGE starts at x 0
        # bold small caps like the NEXT STAGE label: the game draws this row dim, thin strokes vanish
        # one size on every card: the one the longest name fits at
        small = min((fit("cinzel_Cinzel[wght].ttf", 13, t, 122, 15, 800) for _, t in CARDS), key=lambda f: f.size)
        rects = ramp_text(im, top, nxt, small, align="left")
        putpal(im, RAMP_00 if n == 0 else RAMP_SHUFFLED)
        big = fit(serif, 19, name, 190, 20)
        rects += smear(im, (2, 16, 196, 24), name, big, n == 0, range(16) if n == 0 else range(1, 16))
        rects += ramp_text(im, (2, 41, 196, 22), name, big, align="centre")
        return im, rects, []
    return draw


def flash(im):
    # G5 M05_02_0 flashback stills, baked subtitles on the black band (not in SOL.SRP): still 1 at x 52-250 (one
    # line, tpage x < 256), still 3 two lines at x 605-745; the lone "・・・" at x 770 is still 1's line end (drawn
    # right of it in game): cleared, the English line carries its own
    f = font("crimsontext_CrimsonText-Regular.ttf", 14)
    dots = (768, 198, 32, 9)
    box = (dots[0], dots[1], dots[0] + dots[2], dots[1] + dots[3])
    im.paste(max(im.crop(box).getcolors())[1], box)  # the band's own (dark brown) index
    rects = [dots] + ramp_text(im, (50, 195, 202, 16), "The Majesty... So it was here...", f, align="centre")
    rects += ramp_text(im, (600, 196, 150, 14), "I must move it somewhere", f, align="centre")
    rects += ramp_text(im, (600, 211, 150, 15), "and hide it...", f, align="centre")
    return im, rects, []


DRAWERS = {"flash": flash, "title": title, "thanks": thanks, "prestage": prestage, "prestage2": prestage2,
           **{"card%02d" % n: card(n) for n in range(14)}}


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
