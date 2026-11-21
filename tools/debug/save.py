"""PS1 memory card helper for Blade Arts saves (layout: tools/debug/save_layout.md).

  python -X utf8 tools/debug/save.py blank OUT.mcd                 formatted empty 128 KB card
  python -X utf8 tools/debug/save.py list CARD.mcd                 directory: block, state, size, name, checksum ok
  python -X utf8 tools/debug/save.py show CARD.mcd [--slot N]      named fields of a Blade Arts save
  python -X utf8 tools/debug/save.py set CARD.mcd OUT.mcd FIELD=V.. [--slot N]   edit, fix the checksum, write OUT
      FIELD is a name from FIELDS below or a hex offset in the save block (0x274=5, one byte)

Start every edit from a game-written card (work/saves/), never from blank().
"""
import argparse, struct, sys

FRAME, BLOCK, CARD = 128, 8192, 131072
PRODUCT = 'BISLPM-86602'
SUM_LO, SUM_HI, SUM_AT = 0x100, 0x578, 0x578  # u16 = byte sum of block[0x100:0x578] (verified on game saves)
# name: (offset in the save block, struct format); meanings in tools/debug/save_layout.md
FIELDS = {
    'area': (0x108, '<B'), 'room': (0x109, '<B'), 'variant': (0x10A, '<B'),  # map the save loads into (verified)
    'hp': (0x110, '<H'), 'hp_max': (0x112, '<H'),  # verified: hp=50 shows a short red bar
}


def xor(b):
    x = 0
    for c in b:
        x ^= c
    return x


def frame(body):
    body = body.ljust(127, b'\0')
    return body + bytes([xor(body)])


def blank():
    out = bytearray(CARD)
    out[0:FRAME] = frame(b'MC')
    for i in range(1, 16):  # directory: free, no link
        out[i * FRAME:(i + 1) * FRAME] = frame(struct.pack('<IIH', 0xA0, 0, 0xFFFF))
    for i in range(16, 36):  # broken-sector list: none
        out[i * FRAME:(i + 1) * FRAME] = frame(struct.pack('<II', 0xFFFFFFFF, 0) + b'\xff\xff')
    out[63 * FRAME:64 * FRAME] = frame(b'MC')
    return bytes(out)


def entries(card):
    for i in range(1, 16):
        d = card[i * FRAME:(i + 1) * FRAME]
        state, size, nxt = struct.unpack_from('<IIH', d)
        name = d[10:30].split(b'\0')[0].decode('ascii', 'replace')
        yield i, state, size, nxt, name, d[127] == xor(d[:127])


def checksum(blk):
    return sum(blk[SUM_LO:SUM_HI]) & 0xFFFF


def game_blocks(card):
    return [i for i, state, _, _, name, _ in entries(card) if state == 0x51 and name.startswith(PRODUCT)]


def block(card, slot):
    blocks = game_blocks(card)
    assert blocks, 'no Blade Arts save on this card'
    i = blocks[slot]
    return i, bytearray(card[i * BLOCK:(i + 1) * BLOCK])


def edit(card, edits, slot=0):
    """card bytes + ['field=value', '0x14E=0x13', ...] -> new card bytes with the checksum fixed."""
    card = bytearray(card)
    i, blk = block(card, slot)
    for e in edits:
        k, v = e.split('=', 1)
        off, fmt = FIELDS[k] if k in FIELDS else (int(k, 16), '<B')
        assert SUM_LO <= off < SUM_HI, 'offset outside the checksummed save data: ' + e
        struct.pack_into(fmt, blk, off, int(v, 0))
    struct.pack_into('<H', blk, SUM_AT, checksum(blk))
    card[i * BLOCK:(i + 1) * BLOCK] = blk
    return bytes(card)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['blank', 'list', 'show', 'set'])
    ap.add_argument('card')
    ap.add_argument('rest', nargs='*')
    ap.add_argument('--slot', type=int, default=0, help='Nth Blade Arts save on the card (default 0)')
    a = ap.parse_args()
    if a.cmd == 'blank':
        open(a.card, 'wb').write(blank())
        return
    card = bytearray(open(a.card, 'rb').read())
    assert len(card) == CARD and card[:2] == b'MC', 'not a raw 128 KB card'
    if a.cmd == 'list':
        for i, state, size, nxt, name, ok in entries(card):
            if state != 0xA0:
                print('block %2d state %02X size %6d next %04X %s%s' % (i, state, size, nxt, name, '' if ok else ' BADSUM'))
        return
    i, blk = block(card, a.slot)
    if a.cmd == 'show':
        print('block %d title %s' % (i, bytes(blk[4:68]).decode('cp932', 'replace').strip('　 \0')))
        have = struct.unpack_from('<H', blk, SUM_AT)[0]
        print('checksum %04X (computed %04X)%s' % (have, checksum(blk), '' if have == checksum(blk) else ' BAD'))
        for k, (off, fmt) in FIELDS.items():
            print('%-10s 0x%03X = %s' % (k, off, struct.unpack_from(fmt, blk, off)[0]))
        return
    out, edits = a.rest[0], a.rest[1:]
    assert edits, 'nothing to set'
    open(out, 'wb').write(edit(card, edits, a.slot))
    print('wrote %s (block %d)' % (out, i))


if __name__ == '__main__':
    main()
