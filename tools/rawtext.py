"""Raw Shift-JIS strings in the EXE and overlays (not SOL.SRP): find them and the code/data that points at them.

A string = a NUL-terminated run of ASCII (control bytes too), halfwidth kana and valid Shift-JIS pairs that starts
after a NUL (or anywhere something points at) and holds at least one Shift-JIS character. Code and pixel data also parse as such runs: real strings are the ones with a reference
or with kana-heavy text; the rest are listed in NOISE by hand (each checked in the listing, see docs/re/text.md).

References: u32 data words equal to the address; lui+addiu/ori pairs (same register, within 64 instructions); in the
EXE also addiu rX, gp, imm (gp = 0x800CAB68). `+k` marks a reference into the string (k bytes past its start).

usage: python -X utf8 tools/rawtext.py [FILE..]     list every string found (id, refs, text)
"""
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TREE = ROOT / "work" / "disc" / "tree"
GP = 0x800CAB68
# disc path -> (load address of file offset `hdr`, hdr). Overlays: RAM dumps of the running overlay (docs/re/text.md).
FILES = {
    "SLPM_866.02": (0x80010000, 0x800),
    "DATA/STATUS.BIN": (0x80149800, 0),
    "DATA/LOADSAVE.BIN": (0x80149800, 0),
    "DATA/BOSS0P.BIN": (0x80149800, 0),
    "DATA/BOSS3P.BIN": (0x80149800, 0),
    "DATA/GAME.BIN": (0x800EAB90, 0),
}
# Shift-JIS-looking runs in code/pixel data (checked by hand). Strings with a reference are kept unless listed here.
NOISE = {
    # B4047/B4417: tables of Shift-JIS codes (glyph data), not strings
    "SLPM_866.02": {0x0F458, 0x17B74, 0x3AD1A, 0x3AEBA, 0x5F7D2, 0xA046A, 0xB40D6, 0xB4047, 0xB4417},
    "DATA/STATUS.BIN": {0x104B1},
    "DATA/LOADSAVE.BIN": {0x0DE9C},
    "DATA/BOSS0P.BIN": {0x1DD3E, 0x01748, 0x049D8, 0x04E78, 0x158EE},
    "DATA/BOSS3P.BIN": {0x0F1A6},
    "DATA/GAME.BIN": {0x1564E},
}
# files whose scan hits are all pixel/code noise (no strings): checked by hand, see docs/re/text.md
NOISE_FILES = {"DATA/THANKSP.BIN", "DATA/TITLEP.BIN", "DATA/DATA1.PAC", "DATA/ENDING_P.DAT", "DATA/STATUS2.DAT"}


def covered(path):
    """[(start, end)] of every found string and NOISE run in the file (for the coverage test)."""
    b = (TREE / path).read_bytes()
    spans = [(i, i + len(x)) for i, a, room, rr, x in find(path)]
    return spans + [(i, b.index(0, i)) for i in NOISE.get(path, ())]


def is_sjis_lead(c):
    return 0x81 <= c <= 0x9F or 0xE0 <= c <= 0xEF


def cstr(b, i):
    """(end, n_sjis) of the C string at i, or None if a byte is not text."""
    j, n = i, 0
    while j < len(b) and b[j]:
        c = b[j]
        if c < 0x7F or 0xA1 <= c <= 0xDF:  # ASCII, control bytes (STATUS 0xE87 has a stray 0B), halfwidth kana
            j += 1
        elif is_sjis_lead(c) and j + 1 < len(b) and 0x40 <= b[j + 1] <= 0xFC and b[j + 1] != 0x7F:
            try:
                b[j:j + 2].decode("cp932")
            except UnicodeDecodeError:
                return None
            j += 2
            n += 1
        else:
            return None
    return (j, n) if j < len(b) else None


def refs(b, hdr, exe):
    """{address: [file offsets of the referencing word/instruction]}."""
    w = struct.unpack_from("<%dI" % ((len(b) - hdr) // 4), b, hdr)
    out = {}

    def add(a, k):
        out.setdefault(a & 0xFFFFFFFF, []).append(hdr + 4 * k)

    for k, x in enumerate(w):
        add(x, k)
        op = x >> 26
        if op == 0x0F:
            rt = (x >> 16) & 31
            for d, y in enumerate(w[k + 1:k + 65], 1):
                if y >> 26 in (9, 13) and (y >> 21) & 31 == rt:
                    lo = y & 0xFFFF
                    add(((x & 0xFFFF) << 16) + (((lo ^ 0x8000) - 0x8000) if y >> 26 == 9 else lo), k + d)
        elif exe and op == 9 and (x >> 21) & 31 == 28:
            add(GP + (((x & 0xFFFF) ^ 0x8000) - 0x8000), k)
    return out


def kana_text(t):
    """Looks like Japanese text on its own: 4+ full-width chars, 2+ kana, few control bytes / halfwidth kana."""
    full = [c for c in t if ord(c) > 0xFF and not "｡" <= c <= "ﾟ"]
    half = sum("｡" <= c <= "ﾟ" for c in t)
    ctrl = sum(ord(c) < 0x20 and c != "\n" for c in t)
    return len(full) >= 4 and sum("ぁ" <= c <= "ヾ" for c in full) >= 2 and ctrl <= 1 and half <= len(full)


def find(path):
    """[(offset, address, room, refs, text_bytes)]: room = bytes from the start to the next non-zero byte (the NUL and
    any zero padding after it; zero data words could hide in that padding, so phase 7 checks the refs before using it)."""
    base, hdr = FILES[path]
    b = (TREE / path).read_bytes()
    r = refs(b, hdr, path == "SLPM_866.02")
    out, done = [], hdr
    for i in range(hdr, len(b)):
        a = base + i - hdr
        # a string starts after a NUL, or right after other data when something points at it (STATUS 0x748)
        if b[i] == 0 or i > hdr and b[i - 1] != 0 and (i < done or a not in r) or i in NOISE.get(path, ()):
            continue
        p = cstr(b, i)
        if not p or not p[1]:
            continue
        end, _ = p
        rr = [f"{o:X}" for o in sorted(set(r.get(a, [])))]
        rr += [f"{o:X}+{k}" for k in range(1, end - i) for o in sorted(set(r.get(a + k, [])))]
        text = b[i:end]
        t = text.decode("cp932")
        # short or kana-less strings need a reference and plain characters (code words parse as odd bytes)
        if not kana_text(t) and not (rr and not re.search(r"[\x00-\x09\x0b-\x1f｡-ﾟ]", t)):
            continue
        room = end + 1
        while room < len(b) and b[room] == 0:
            room += 1
        out.append((i, a, room - i, rr, text))
        done = end
    return out


def decode(x):
    """Raw string bytes -> TSV text: 0A as {n}, other control bytes as {XX}."""
    return re.sub(r"[\x00-\x1f]", lambda m: "{n}" if m[0] == "\n" else "{%02X}" % ord(m[0]), x.decode("cp932"))


def encode(t):
    return re.sub(r"\{([0-9A-F]{2}|n)\}", lambda m: "\n" if m[1] == "n" else chr(int(m[1], 16)), t).encode("cp932")


if __name__ == "__main__":
    for f in sys.argv[1:] or FILES:
        for i, a, room, rr, x in find(f):
            print(f"{f}\t{i:05X}\t{a:08X}\t{room}\t{','.join(rr) or '-'}\t{decode(x)}")
