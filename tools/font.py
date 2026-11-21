"""Write the English glyphs (fonts/en11.txt) into the free cells of the game font (DATA/DATA1.PAC entry 119).

The font TIM is 4bpp 256x165 with four 1bpp planes (nibble bit k = plane k, shown through CLUT k); glyph index i sits
at u = (i % 92 >> 2) * 11, v = i // 92 * 11, plane i & 3 (EXE 0x8008DD20 / 0x8008DD34). Indexes 1297-1379 (row 14
after the last JP glyph) are empty in the original; en.SLOT assigns them.

    python -X utf8 tools/font.py OUT.png   render the patched font sheet (plane-coloured) for a look
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import en  # noqa: E402

ENTRY = 119
W, H = 256, 165


def tim_pixels(pac):
    """Offset of the TIM's pixel data inside DATA1.PAC (checked against the known header)."""
    sec, size = struct.unpack_from("<II", pac, 8 + 8 * ENTRY)
    o = sec * 0x800
    assert pac[o:o + 8] == bytes.fromhex("1000000008000000"), "font TIM header"
    clut = struct.unpack_from("<I", pac, o + 8)[0]
    img = o + 8 + clut
    assert struct.unpack_from("<I4H", pac, img)[1:] == (960, 0, 64, H), "font TIM image block"
    return img + 12


def cell(pix, data, i):
    """11 rows of 11 bools for glyph index i."""
    q, r = divmod(i, 92)
    u0, v0, bit = (r >> 2) * 11, q * 11, 1 << (r & 3)
    rows = []
    for y in range(11):
        row = []
        for x in range(11):
            b = data[pix + (v0 + y) * (W // 2) + (u0 + x) // 2]
            nib = b >> 4 if (u0 + x) & 1 else b & 15
            row.append(bool(nib & bit))
        rows.append(row)
    return rows


def patch(pac):
    """DATA1.PAC bytes with the English glyphs drawn into their slots."""
    out = bytearray(pac)
    pix = tim_pixels(out)
    filler = cell(pix, pac, en.LAST_SLOT)  # cells past the last JP glyph all hold one filler pattern
    for c, i in en.SLOT.items():
        if cell(pix, pac, i) != filler:
            raise ValueError(f"glyph slot {i} for {c!r} is not a free (filler) cell in the original font")
        q, r = divmod(i, 92)
        u0, v0, bit = (r >> 2) * 11, q * 11, 1 << (r & 3)
        for y in range(11):  # clear the filler
            for x in range(11):
                a = pix + (v0 + y) * (W // 2) + (u0 + x) // 2
                out[a] &= ~(bit << 4 if (u0 + x) & 1 else bit) & 0xFF
        q, r = divmod(i, 92)
        u0, v0, bit = (r >> 2) * 11, q * 11, 1 << (r & 3)
        for y, line in enumerate(en._FONT[c]):
            for x, p in enumerate(line[:11]):
                if p == "#":
                    a = pix + (v0 + y) * (W // 2) + (u0 + x) // 2
                    out[a] |= bit << 4 if (u0 + x) & 1 else bit
    for c, i in en.SLOT.items():  # read back
        assert [["#" if p else "." for p in r] for r in cell(pix, out, i)] == \
            [list(line[:11].ljust(11, ".")) for line in en._FONT[c]], c
    return bytes(out)


if __name__ == "__main__":
    from PIL import Image
    root = Path(__file__).resolve().parents[1]
    d = patch((root / "work/disc/tree/DATA/DATA1.PAC").read_bytes())
    pix = tim_pixels(d)
    im = Image.new("RGB", (W, H))
    cols = [(255, 80, 80), (80, 255, 80), (80, 120, 255), (255, 255, 80)]
    for y in range(H):
        for x in range(W):
            b = d[pix + y * (W // 2) + x // 2]
            nib = b >> 4 if x & 1 else b & 15
            px = [cols[k] for k in range(4) if nib >> k & 1]
            if px:
                im.putpixel((x, y), tuple(sum(p[j] for p in px) // len(px) for j in range(3)))
    im.resize((W * 3, H * 3), Image.NEAREST).save(sys.argv[1])
