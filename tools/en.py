"""English text codec for the patched renderer (asm/vwf.asm, docs/re/text.md §English).

In RAM (after the XOR decode) the game reads text as 2-byte units. A unit whose first byte is >= 0xA0 is an English
pair: each byte is ASCII | 0x80 (0xA0 = space), 0x80 = no letter (pads an odd run). Control codes stay ASCII and
Shift-JIS stays 2-byte, so every code still starts on an even offset (the game reads them with lh).

`en` column syntax: plain English; `{...}` = raw control code bytes (even length, e.g. {CSA0t0e01151}, {b3}, {i060});
`\\\\` (two backslashes) = line break and `@@` = page break, written bare (neither \\ nor @ is in the charset);
any other non-ASCII character is written as Shift-JIS (fullwidth symbols such as ★). Raw (EXE/overlay) strings
also use {n} = byte 0A and {0B}-style single control bytes, as in their jp column; printf fields go in braces ({%s}).

    python -X utf8 tools/en.py "Some text"     width in px and encoded bytes
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / "fonts" / "en11.txt"
# Printable ASCII the font slots hold (83 free slots after the 1297 JP glyphs); dropped: # $ < > @ \ ^ _ ` { | }
CHARSET = "!\"%&'()*+,-./0123456789:;=?ABCDEFGHIJKLMNOPQRSTUVWXYZ[]abcdefghijklmnopqrstuvwxyz~"
FIRST_SLOT = 1297          # first free glyph index in the font table (DATA1.PAC 118 has 1297 codes)
LAST_SLOT = 14 * 92 + 91   # last cell of the TIM's last glyph row
PAD = 0x80
SPACE_W = 4
JP_PITCH = 12              # fullwidth advance in the text windows measured so far (struct +0xF)
assert FIRST_SLOT + len(CHARSET) - 1 <= LAST_SLOT


def load_font():
    """{char: [11 rows of '#'/'.']} from the 13-row art (rows 1-11 hold ink)."""
    g, cur = {}, None
    for line in FONT.read_text(encoding="utf-8").splitlines():
        if line.startswith("char "):
            cur = line[5:]
            cur = " " if cur == "space" else cur
            g[cur] = []
        elif cur is not None and line.strip():
            g[cur].append(line)
    out = {}
    for c, rows in g.items():
        assert len(rows) == 13 and "#" not in rows[0] + rows[12], c
        out[c] = rows[1:12]
    return out


_FONT = load_font()


def advance(c):
    if c == " ":
        return SPACE_W
    cols = [x for r in _FONT[c] for x, p in enumerate(r) if p == "#"]
    return max(cols) + 2


WIDTH = {c: advance(c) for c in CHARSET + " "}
SLOT = {c: FIRST_SLOT + i for i, c in enumerate(CHARSET)}

TOKEN = re.compile(r"\{([^}]*)\}|(\\\\|@@)|(.)", re.S)


def tokens(text):
    """('code', bytes) | ('ch', letter) | ('sjis', bytes)."""
    for m in TOKEN.finditer(text):
        if m.group(1) is not None:
            g = m.group(1)
            if g == "n" or re.fullmatch(r"[01][0-9A-F]", g):  # raw-string control byte ({n} = 0A), as in rawtext.py
                yield "byte", b"\n" if g == "n" else bytes([int(g, 16)])
            else:
                yield "code", g.encode("ascii")
        elif m.group(2):
            yield "code", m.group(2).encode("ascii")
        else:
            c = m.group(3)
            if c in WIDTH:
                yield "ch", c
            elif ord(c) < 0x80:
                raise ValueError(f"character {c!r} is not in the English font: {text!r}")
            else:
                yield "sjis", c.encode("cp932")


def encode(text):
    """en column text -> game bytes (even length)."""
    out, run = bytearray(), []

    def flush():
        if len(run) % 2:
            run.append(PAD)
        out.extend(run)
        run.clear()

    for kind, v in tokens(text):
        if kind == "ch":
            run.append(ord(v) | 0x80)
        else:
            flush()
            if kind == "code" and len(v) % 2:
                raise ValueError(f"odd-length code {v!r} in {text!r}")
            out += v
    flush()
    return bytes(out)


def width(line):
    """Pixel width of one line of en text (codes are zero width, Shift-JIS chars take the JP pitch)."""
    w = 0
    for kind, v in tokens(line):
        w += WIDTH[v] if kind == "ch" else JP_PITCH if kind == "sjis" else 0
    return w


def wrap(text, limit):
    """Greedy word wrap of a page (no codes inside words) to `limit` px; returns lines."""
    lines, cur = [], ""
    for word in text.split(" "):
        cand = word if not cur else cur + " " + word
        if width(cand) <= limit or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def tables():
    """(glyph words, widths) indexed by byte & 0x7F: glyph word = plane << 16 | v << 8 | u of the 11x11 cell
    (the game adds its CLUT base << 16), 0 = no ink; width 0 for 0x00 (the pad byte)."""
    glyph, wid = [0] * 128, [0] * 128
    for c in CHARSET + " ":
        wid[ord(c)] = WIDTH[c]
    for c, i in SLOT.items():
        q, r = divmod(i, 92)
        glyph[ord(c)] = (r & 3) << 16 | (q * 11) << 8 | (r >> 2) * 11
    return glyph, wid


def _selftest():
    assert encode("Hi") == bytes([0xC8, 0xE9])
    assert encode("Hi!{b3}A") == bytes([0xC8, 0xE9, 0xA1, PAD]) + b"b3" + bytes([0xC1, PAD])
    assert encode("A\\\\B@@") == bytes([0xC1, PAD]) + b"\\\\" + bytes([0xC2, PAD]) + b"@@"
    assert len(encode("abc")) % 2 == 0
    assert all(1 <= WIDTH[c] <= 7 for c in CHARSET), "letter wider than the 11 px cell allows for VWF overlap"
    g, w = tables()
    assert g[ord("!")] == (1297 % 92 & 3) << 16 | (1297 // 92 * 11) << 8 | (1297 % 92 >> 2) * 11
    try:
        encode("{b}")
    except ValueError:
        pass
    else:
        raise AssertionError("odd code accepted")


_selftest()

if __name__ == "__main__":
    for t in sys.argv[1:]:
        print(width(t), encode(t).hex(" "))
