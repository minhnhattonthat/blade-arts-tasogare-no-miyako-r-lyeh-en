"""Read DATA/SOL.SRP: the script/message archive (recon helper; the phase-4 extractor builds on it).

Layout (docs/re/text.md):
  file header (sector 0): u32 1, u32 N, then N x (u32 block_id, u32 block_size); block_id = first sector of the block
    in the file (blocks of 2+ sectors skip ids), blocks are back to back from 0x800.
  every 0x800 sector of a block is a self-contained string page:
    sector 0 of a block: u32 hdr_size, u32 0, (hdr_size-8)/2 x u16 last global string index of each sector (0-padded)
    later sectors:       u32 8, u32 sector_no_in_block
    then u16 string offsets (from the sector start) for the sector's strings, padded to 4 bytes, then the strings.
  string: u32 flags (7 on disc; 5 at runtime once decoded), then Shift-JIS XOR 0x8C, then raw (un-XORed) 0A 0A,
    NUL-padded to 4.

usage: python -X utf8 tools/sol.py [SOL.SRP] > work/recon/sol.txt
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "work" / "disc" / "tree" / "DATA" / "SOL.SRP"
KEY = 0x8C
SECTOR = 0x800


def blocks(d):
    one, n = struct.unpack_from("<II", d, 0)
    pos = SECTOR
    for i in range(n):
        bid, size = struct.unpack_from("<II", d, 8 + 8 * i)
        yield bid, pos, d[pos:pos + size]
        pos += size


def sector_counts(blk):
    """Strings per sector, from the last-index table in sector 0."""
    hdr = struct.unpack_from("<I", blk, 0)[0]
    last = [v for v in struct.unpack_from(f"<{(hdr - 8) // 2}H", blk, 8)]
    nsec = len(blk) // SECTOR
    last = last[:nsec]
    return [last[0] + 1] + [last[i] - last[i - 1] for i in range(1, nsec)]


def text_end(raw, p):
    """Offset of the raw 0A 0A terminator, walking whole characters: 中 (92 86) XORs to 1E 0A, so a byte search for
    0A 0A can stop inside a character. Block 132 string 110 has its terminator and padding XORed too (86 86 8C 00)."""
    while raw[p:p + 2] not in (b"\n\n", b"\x86\x86"):
        c = raw[p] ^ KEY
        p += 2 if 0x81 <= c <= 0x9F or 0xE0 <= c <= 0xFC else 1
    return p


def strings(blk):
    """(global_index, sector, offset_in_sector, flags, text_bytes) per string; text ends before the 0A 0A terminator."""
    gi = 0
    for s, cnt in enumerate(sector_counts(blk)):
        sec = blk[s * SECTOR:(s + 1) * SECTOR]
        hdr = struct.unpack_from("<I", sec, 0)[0]
        for o in struct.unpack_from(f"<{cnt}H", sec, hdr):
            flags = struct.unpack_from("<I", sec, o)[0]
            end = text_end(sec, o + 4)
            yield gi, s, o, flags, bytes(b ^ KEY for b in sec[o + 4:end])
            gi += 1


# The original's one odd terminator (block 132 string 110: XORed 0A 0A + pad); kept only while the text is unchanged.
QUIRK_TAIL = {(132, 110): bytes.fromhex("86868c0000")}


def pack_sector(head, items):
    """One 0x800 string page: `head` (sector header bytes), items = [(flags, text_bytes, raw_tail or None)].
    Raises ValueError when the strings don't fit."""
    n = len(items)
    pos = len(head) + 2 * n + (-(len(head) + 2 * n) % 4)
    offs, body = [], bytearray()
    for flags, text, tail in items:
        offs.append(pos + len(body))
        s = struct.pack("<I", flags) + bytes(b ^ KEY for b in text)
        s += tail if tail is not None else b"\n\n\0\0" + bytes(-len(s) % 4)  # 0A 0A 00 00, then pad to 4
        body += s
    out = head + struct.pack(f"<{n}H", *offs)
    out += bytes(pos - len(out)) + body
    if len(out) > SECTOR:
        raise ValueError(f"sector overflow by {len(out) - SECTOR} bytes")
    return out + bytes(SECTOR - len(out))


def pack_block(bid, sectors, hdr_size):
    """Block bytes from sectors = [[(flags, text_bytes), ..] per sector]; hdr_size = sector 0 header size (kept)."""
    last, gi = [], 0
    for items in sectors:
        gi += len(items)
        last.append(gi - 1)
    out, gi = b"", 0
    for s, items in enumerate(sectors):
        if s == 0:
            head = struct.pack("<II", hdr_size, 0) + struct.pack(f"<{len(last)}H", *last)
            head += bytes(hdr_size - len(head))
        else:
            head = struct.pack("<II", 8, s)
        out += pack_sector(head, [(f, t, QUIRK_TAIL.get((bid, gi + k)) if t == orig else None)
                                  for k, (f, t, orig) in enumerate(items)])
        gi += len(items)
    return out


def string_size(text):
    return 4 + len(text) + 4 + (-(len(text) + 4) % 4)  # flags, text, 0A 0A 00 00, pad (as pack_sector)


def reflow(items, nsec, hdr_size):
    """Spread the block's strings (in order) over its nsec sectors greedily; the game finds a string's sector through
    the last-index table, so only the order matters. Raises ValueError when the block can't hold them."""
    secs, cur, used = [], [], 0
    for it in items:
        head = hdr_size if not secs else 8
        need = string_size(it[1]) + 2
        if cur and head + 2 * len(cur) + 3 + used + need > SECTOR:
            secs.append(cur)
            cur, used = [], 0
        cur.append(it)
        used += string_size(it[1])
    secs.append(cur)
    if len(secs) > nsec:
        raise ValueError(f"block needs {len(secs)} sectors, has {nsec}")
    return secs + [[] for _ in range(nsec - len(secs))]


def pack(orig, texts):
    """Rebuild SOL.SRP: orig = original file bytes, texts = {(block_id, global_index): text_bytes} (missing = original).
    Same sectors per block and same string order, so block ids and string indexes stay valid; a block whose strings
    no longer fit their original sectors is reflowed over its sectors."""
    out = bytearray(orig[:SECTOR])
    errors = []
    for bid, pos, blk in blocks(orig):
        secs = [[] for _ in sector_counts(blk)]
        for gi, s, o, flags, x in strings(blk):
            secs[s].append((flags, texts.get((bid, gi), x), x))
        hdr = struct.unpack_from("<I", blk, 0)[0]
        try:
            out += pack_block(bid, secs, hdr)
        except ValueError:
            try:
                out += pack_block(bid, reflow([it for s in secs for it in s], len(secs), hdr), hdr)
            except ValueError as e:
                errors.append(f"SOL block {bid}: {e}")
                out += blk  # keep later blocks at their sectors so every overflow gets reported
    if errors:
        raise ValueError("; ".join(errors))
    return bytes(out + orig[len(out):])


if __name__ == "__main__":
    d = Path(sys.argv[1] if len(sys.argv) > 1 else DEFAULT).read_bytes()
    for bid, pos, blk in blocks(d):
        print(f"# block {bid} @{pos:06X} sectors {len(blk) // SECTOR} strings {sector_counts(blk)}")
        for gi, s, o, flags, x in strings(blk):
            print(f"{bid}\t{gi}\t{s}:{o:03X}\t{flags}\t{x.decode('cp932', 'replace')}")
