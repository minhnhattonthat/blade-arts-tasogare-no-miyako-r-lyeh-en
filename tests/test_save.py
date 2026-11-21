"""tools/debug/save.py: card format, checksum and field edits (synthetic card; the real one is gitignored)."""
import os
import struct
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'debug'))
import save  # noqa: E402


def fake_card():
    card = bytearray(save.blank())
    d = save.frame(struct.pack('<IIH', 0x51, 8192, 0xFFFF) + b'BISLPM-86602-00')
    card[save.FRAME:2 * save.FRAME] = d
    blk = bytearray(save.BLOCK)
    blk[0:4] = b'SC\x11\x01'
    blk[0x100:0x578] = bytes(range(256)) * 4 + bytes(0x478 - 1024)
    struct.pack_into('<H', blk, save.SUM_AT, save.checksum(blk))
    card[save.BLOCK:2 * save.BLOCK] = blk
    return bytes(card)


def test_blank_is_formatted():
    c = save.blank()
    assert len(c) == save.CARD and c[:2] == b'MC'
    assert all(state == 0xA0 and ok for _, state, _, _, _, ok in save.entries(c))


def test_edit_fixes_checksum():
    c = save.edit(fake_card(), ['area=5', 'room=1', 'variant=0xA', 'hp=50'])
    i, blk = save.block(c, 0)
    assert i == 1 and (blk[0x108], blk[0x109], blk[0x10A]) == (5, 1, 10)
    assert struct.unpack_from('<H', blk, 0x110)[0] == 50
    assert struct.unpack_from('<H', blk, save.SUM_AT)[0] == save.checksum(blk)


def test_edit_refuses_unchecksummed_bytes():
    with pytest.raises(AssertionError):
        save.edit(fake_card(), ['0x80=1'])


def test_real_save_checksum():
    p = os.path.join(ROOT, 'work', 'saves', 'save_first.mcd')
    if not os.path.exists(p):
        pytest.skip('no game-written card (run tools/debug/warp_all.py save_first)')
    _, blk = save.block(open(p, 'rb').read(), 0)
    assert struct.unpack_from('<H', blk, save.SUM_AT)[0] == save.checksum(blk)
