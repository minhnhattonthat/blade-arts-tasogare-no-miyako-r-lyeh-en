"""Recover the colours a runtime-built CLUT gives each index: align a 4/8bpp TIM region with a screenshot that shows
it drawn 1:1, then average the screen colour per index.

  python -X utf8 tools/clutfit.py SHOT.png FILE HEXOFF x,y,w,h [--search X0,Y0,X1,Y1]

x,y,w,h = the TIM region (pixels) to match; --search = screen box for its top-left corner (default whole screen).
Prints the best offset, its error, and per index: count and mean RGB (an index never seen prints '-').
Used for the G7 stage cards, whose TIM CLUT is all 0x8000 and whose real CLUT is built at run time.
"""
import sys

from PIL import Image

import gfx


def fit(shot, idx, rect, search):
    x, y, w, h = rect
    sp, ip = shot.load(), idx.load()
    pts = [(i, j, ip[x + i, y + j]) for j in range(h) for i in range(w)]
    best = None
    for oy in range(search[1], search[3] + 1):
        for ox in range(search[0], search[2] + 1):
            if ox + w > shot.width or oy + h > shot.height:
                continue
            sums = {}
            for i, j, v in pts:
                c = sp[ox + i, oy + j]
                s = sums.setdefault(v, [0, 0, 0, 0, 0])
                s[0] += 1
                for k in range(3):
                    s[1 + k] += c[k]
                s[4] += c[0] * c[0] + c[1] * c[1] + c[2] * c[2]
            # within-index variance over total variance: one colour per index when the offset is right; a flat
            # (black) screen area would also score 0 within, so it is skipped
            n = len(pts)
            tot = sum(s[4] for s in sums.values()) - sum(sum(s[1 + k] for s in sums.values()) ** 2 for k in range(3)) / n
            if tot < n:
                continue
            err = sum(s[4] - (s[1] ** 2 + s[2] ** 2 + s[3] ** 2) / s[0] for s in sums.values()) / tot
            if best is None or err < best[0]:
                best = (err, ox, oy, sums)
    return best


def main():
    a = sys.argv[1:]
    if len(a) < 4:
        sys.exit(__doc__)
    shot = Image.open(a[0]).convert("RGB")
    d = open(a[1], "rb").read() if not (gfx.TREE / a[1]).exists() else (gfx.TREE / a[1]).read_bytes()
    idx = gfx.export(d, int(a[2], 16))
    rect = tuple(int(v) for v in a[3].split(","))
    search = (0, 0, shot.width - 1, shot.height - 1)
    if "--search" in a:
        search = tuple(int(v) for v in a[a.index("--search") + 1].split(","))
    err, ox, oy, sums = fit(shot, idx, rect, search)
    print(f"offset {ox},{oy} err {err:.3f} (share of variance)")
    for v in range(16 if idx.getextrema()[1] < 16 else 256):
        s = sums.get(v)
        print(v, "-" if not s else f"{s[0]} {tuple(round(s[1 + k] / s[0]) for k in range(3))}")


if __name__ == "__main__":
    main()
