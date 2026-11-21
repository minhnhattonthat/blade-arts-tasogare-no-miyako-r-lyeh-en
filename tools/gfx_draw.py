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


def ramp_text(im, rect, text, f, align="right", bg=None, bold=False):
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
    bg = max(used, key=used.get) if bg is None else bg  # pass bg when ink can outnumber it (dense kanji)
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
    if bold and x1 - x0 + 1 > w:
        sys.exit(f"{text!r}: {x1 - x0 + 1} px bold > rect {w}")
    tx = {"right": w - x1 - bold, "left": -x0, "centre": (w - (x1 - x0) - bold) // 2 - x0}[align]
    for dx in range(1 + bold):  # bold: the text again 1 px right
        d.text((tx + dx, (h - (y1 - y0)) // 2 - y0), text, font=f, fill=255)
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


def sticon(im):
    # G2 STICON.BIN help labels, ink 0 on background 15 (CLUT row 0 preview). The sprite rects are unknown (no table;
    # not seen in game yet), so each English label stays inside its Japanese label's own extent (column gaps)
    f = font("lato_Lato-Regular.ttf", 12)
    labels = [((72, 0, 70, 13), "Cancel"), ((3, 13, 30, 14), "Yes"), ((35, 13, 41, 14), "No"),
              ((79, 13, 31, 14), "Select"), ((114, 13, 28, 14), "OK"), ((146, 13, 27, 14), "Use"),
              ((178, 13, 28, 14), "Drop")]
    rects = []
    for r, t in labels:
        rects += ramp_text(im, r, t, fit(f.path, f.size, t, r[2] - 2, r[3]), align="centre", bg=15, bold=True)
    return im, rects, []


# G3 ending staff roll (DATA/ENDINGP.BIN @74E8, 4bpp 1188x500, one texture page per 256 px column). The game draws
# each group as a sprite over u 0-159 of its column at screen x 160 (marker build, work/qa/g3_mark), so a line may run
# to u 158. CLUTs fitted from JP shots (tools/clutfit.py): the TIM's own for most groups, ROLL_B for the debugger
# group (column 3 y 383-496) and the Planning/Directors group (column 4 y 158-253), ROLL_C for the (c) line.
ROLL_B = [(0, 0, 0), (41, 41, 41), (24, 24, 24), (82, 90, 90), (49, 57, 57), (0, 0, 0), (189, 213, 222),
          (172, 197, 205), (148, 164, 172), (164, 180, 189), (131, 148, 156), (213, 238, 255), (123, 131, 139),
          (106, 115, 123), (8, 8, 16), (0, 0, 0)]  # index 5 never seen: kept black so it is never picked
ROLL_C = [(0, 0, 0), (41, 41, 41), (24, 24, 24), (82, 90, 90), (49, 57, 57), (90, 106, 106), (189, 213, 222),
          (164, 180, 189), (131, 148, 156), (106, 123, 131), (213, 238, 255), (123, 131, 139), (106, 115, 123),
          (205, 222, 238), (8, 8, 16), (0, 0, 0)]
ROLL_B_RECTS = [(768, 383, 256, 114), (1024, 158, 164, 96)]
H, N, A = 4, 60, 8  # x in column: heading, name (the JP names' column, also Paul Handelman / MBA), cast actor dots
# (column, JP line top y, x, text). Names in Western order (D1); official on-disc spellings where the intro credits
# texture (M0/M02_10_0.PAC) has them (Tuchida, Yuuki, Satuki, Syoutarou, Nishimatu ...; its "Isizka" typo fixed),
# else Hepburn readings of the kanji (glossary.md §Credits). Already English, left as drawn: Paul Handelman, MBA,
# STAFF / ENIX STAFF / CAST, Fin.
ROLL = [
    (0, 2, H, "Special Thanks"), (0, 15, N, "Katsunori Yamagishi"), (0, 28, N, "Yasuhito Watanabe"),
    (0, 41, N, "Yosuke Saito"), (0, 54, N, "Hiroki Fujimoto"), (0, 67, N, "Yukihiro Shibuya"),
    (0, 80, N, "Daisuke Kobayashi"), (0, 93, N, "Rie Narisawa"), (0, 106, N, "Wataru Higuchi"),
    (0, 119, N, "Tatsuki Watanabe"), (0, 132, N, "Takamasa Shiba"), (0, 145, N, "Naoyuki Masuda"),
    (0, 158, N, "Nobuhisa Hiroshige"), (0, 171, N, "Keisuke Moroki"), (0, 184, N, "Eriko Kobayashi"),
    (0, 223, N, "Takashi Torii"),
    (0, 257, H, "Map Design"), (0, 270, N, "Kenji Tuchida"), (0, 283, N, "Katsuhiko Shiono"),
    (0, 309, H, "Character Models"), (0, 322, N, "Kenji Tuchida"), (0, 335, N, "Tomoko Kamiyama"),
    (0, 361, H, "2D Graphics"), (0, 374, N, "Kenji Tuchida"), (0, 387, N, "Tomoko Kamiyama"),
    (1, 2, H, "Sales"), (1, 15, N, "Hajime Kanie"), (1, 28, N, "Koji Taguchi"), (1, 41, N, "Masaharu Katsuragi"),
    (1, 54, N, "Tomoyoshi Osaki"), (1, 67, N, "Yutaka Tani"), (1, 80, N, "Koji Takada"), (1, 93, N, "Ariyoshi Furo"),
    (1, 106, N, "Jun Toda"), (1, 119, N, "Hirotomo Kikumoto"), (1, 132, N, "Mari Shimada"),
    (1, 145, N, "Keiko Katsumata"), (1, 171, N, "Tsutomu Yamada"), (1, 184, N, "Kazuo Kusakawa"),
    (1, 197, N, "Tatsuhiko Tsubota"), (1, 210, N, "Mika Sakai"),
    (1, 257, H, "Promotion"), (1, 270, N, "Shinji Futami"), (1, 283, N, "Hideki Yamamoto"),
    (1, 296, N, "Munehiro Osawa"), (1, 309, N, "Rumi Yoshikawa"), (1, 322, N, "Hodaka Yamagishi"),
    (1, 335, N, "Yasunori Furuta"), (1, 361, H, "Artwork"), (1, 374, N, "Naoki Oishi"), (1, 387, N, "Takashi Kamimura"),
    (2, 2, H, "Music"), (2, 15, N, "Shinji Nukaga"), (2, 28, N, "Tsuyoshi Kaneko"), (2, 54, H, "Sound"),
    (2, 67, N, "Hiroyuki Sano"), (2, 93, H, "Technical Support"), (2, 106, N, "Yukinobu Wakata"),
    (2, 119, N, "Asako Miyashita"), (2, 145, H, "In Cooperation With"), (2, 158, N, "Usami Kikaku"),
    (2, 257, N, "Yu Miyake"), (2, 270, N, "Taichi Inuzuka"), (2, 283, N, "Hiroyoshi Shibahara"),
    (2, 296, N, "Jun Miyamoto"), (2, 309, N, "Ryutaro Ichimura"), (2, 356, H, "Producer"), (2, 369, N, "Shinji Wachi"),
    (2, 385, H, "Executive Producers"), (2, 398, N, "Yukinobu Chida"), (2, 411, N, "Keiji Honda"),
    (2, 450, H, "Publisher"), (2, 463, N, "Yasuhiro Fukushima"),
    (3, 3, H, "Walter Landers"), (3, 19, A, "Unshou Ishizuka"), (3, 43, H, "Patricia Millers"),
    (3, 58, A, "Satuki Yukino"), (3, 75, H, "Basetet"), (3, 88, A, "Satuki Yukino"), (3, 106, H, "Maya"),
    (3, 118, A, "Rika Fukami"), (3, 136, H, "Zagnus"), (3, 148, A, "Yoshikazu Nagano"),
    (3, 259, H, "Rei Shido"), (3, 271, A, "Syoutarou Morikubo"), (3, 286, H, "Nakamura"), (3, 298, A, "Norio Wakamoto"),
    (3, 316, H, "Ilum"), (3, 327, A, "Mariko Kouda"), (3, 351, H, "Bridget Landers"), (3, 366, A, "Mariko Kouda"),
    (3, 383, H, "Debuggers"), (3, 396, N, "Mika Endo"), (3, 409, N, "Kensuke Yokoyama"), (3, 422, N, "Teppei Kobayashi"),
    (3, 435, N, "Yasuhito Suzuki"), (3, 448, N, "Tadahiro Minamijima"), (3, 461, N, "Kiyoyoshi Hikima"),
    (3, 474, N, "Akiyuki Ichi"), (3, 487, N, "Kazuto Sekine"),
    (4, 2, H, "Programming"), (4, 15, N, "Seishiro Mizukami"), (4, 28, N, "Kenji Yoshino"),
    (4, 41, N, "Osamu Sugiyama"), (4, 54, N, "Jiro Hirano"), (4, 80, H, "Event Programming"),
    (4, 93, N, "Kazuhiro Nomura"), (4, 119, N, "Hiroki Ishikawa"), (4, 132, N, "Takanari Wakasugi"),
    (4, 145, N, "Ryo Misawa"), (4, 158, H, "Planning"), (4, 171, N, "Gentaro Mizukami"), (4, 192, H, "Directors"),
    (4, 205, N, "Kenji Tuchida"), (4, 218, N, "Osamu Sugiyama"), (4, 244, 36, "Yoshitaka Oura (Romantec)"),
    (4, 257, H, "Marion"), (4, 270, A, "Norihisa Mori"), (4, 289, H, "Tindalos"), (4, 303, A, "Yoshinobu Kaneko"),
    (4, 321, H, "Ranfa"), (4, 334, A, "Umi Tenjin"), (4, 353, H, "Dr. Harry Sanderson"),
    (4, 368, A, "Kazuhiko Nishimatu"), (4, 383, H, "Technical Support"), (4, 396, N, "Teruhiko Hanawa"),
    (4, 409, N, "Kenjiro Kano"), (4, 422, N, "Tomoyuki Iwai"), (4, 435, N, "Noriko Nakame"),
    (4, 461, N, "Hiroshi Sato"), (4, 474, N, "Hideki Yoneyama"),
]
ROLL_COPYRIGHT = (768, 241, 3, 240)  # column x, JP line top y, x in column, right limit (the Fin sprite is wider)


def roll_line(im, lum, levels, x, y, text, f, right, clear=10):
    """Clear the JP line (rows y..y+clear-1, non-transparent pixels of its column) and draw text with its baseline on
    the JP glyphs' bottom row, each pixel the level nearest its blend of black and the brightest level; a pixel only
    brightens, so descenders and the next line's ascenders may share rows."""
    px = im.load()
    col = x - x % 256
    for cy in range(y, y + clear):
        for cx in range(col, min(col + 256, im.width)):
            if px[cx, cy] != 0:
                px[cx, cy] = 15
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    x0, y0, x1, y1 = d.textbbox((x, y + 9), text, font=f, anchor="ls")
    if x1 > right:
        sys.exit(f"{text!r}: ends at u {x1 - col} > {right - col}")
    mask = Image.new("L", (x1 - x0 + 2, y1 - y0 + 2))
    ImageDraw.Draw(mask).text((x - x0, y + 9 - y0), text, font=f, fill=255, anchor="ls")
    ink = max(levels, key=lambda i: lum[i])
    for (cx, cy), v in zip(((i % mask.width, i // mask.width) for i in range(mask.width * mask.height)), mask.getdata()):
        if v:
            want = lum[ink] * v / 255
            best = min(levels, key=lambda i: abs(lum[i] - want))
            if lum[best] > lum[px[x0 + cx, y0 + cy]]:
                px[x0 + cx, y0 + cy] = best
    return (x0, y0, x1 - x0, y1 - y0)


def ending(im):
    def lums(colours):
        return [0.3 * r + 0.59 * g + 0.11 * b for r, g, b in colours]
    pal = im.getpalette()
    lum_a = lums([tuple(pal[3 * i:3 * i + 3]) for i in range(16)])
    lum_b, lum_c = lums(ROLL_B), lums(ROLL_C)
    f = font("crimsontext_CrimsonText-Regular.ttf", 11)  # same 8 px caps as 12, and every name fits at u 60
    dots ="· · · · ·"
    rects, boxes = [], []
    for c, y, u, text in ROLL:
        x = 256 * c
        in_b = any(bx <= x < bx + bw and by <= y < by + bh for bx, by, bw, bh in ROLL_B_RECTS)
        lum = lum_b if in_b else lum_a
        levels = [i for i in range(1, 16) if not (in_b and i == 5)]
        rects.append((x, y, min(256, im.width - x), 10))
        if u == A:  # cast actor: dots, then the name in the names' column like the JP line
            boxes.append(roll_line(im, lum, levels, x + A, y, dots, f, x + 158))
            boxes.append(roll_line(im, lum, levels, x + N, y, text, f, x + 158, clear=0))
        else:
            boxes.append(roll_line(im, lum, levels, x + u, y, text, f, x + 158))
    cx, cy, cu, cr = ROLL_COPYRIGHT
    rects.append((cx, cy, 256, 11))
    text = "© Ea Co.,Ltd / Nobuteru Yuki / ENIX 2000"
    w = ImageDraw.Draw(Image.new("L", (1, 1))).textlength(text, font=f)
    u = round((cu + cr) / 2 - w / 2)  # centred on the JP line, as "Fin" above it
    boxes.append(roll_line(im, lum_c, range(1, 16), cx + u, cy, text, f, cx + cr, clear=11))
    return im, rects, boxes


DRAWERS = {"flash": flash, "sticon": sticon, "title": title, "thanks": thanks, "prestage": prestage, "prestage2": prestage2,
           "ending": ending, **{"card%02d" % n: card(n) for n in range(14)}}


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
