"""Search disc files for Japanese words encoded as indexes into the DATA1.PAC font table.

usage: python -X utf8 tools/fontsearch.py WORD [WORD..]  (searches work/disc/tree)
Tries u16 LE, u16 BE and u8 index forms with offsets 0..2 added to the index.
"""
import os, struct, sys

ROOT = os.path.join(os.path.dirname(__file__), '..', 'work', 'disc', 'tree')


def font_table():
    d = open(os.path.join(ROOT, 'DATA', 'DATA1.PAC'), 'rb').read()
    st = d.find(bytes.fromhex('40814181428144814581'))
    codes, i = [], st
    while struct.unpack_from('<H', d, i)[0] >= 0x8140:
        codes.append(struct.pack('>H', struct.unpack_from('<H', d, i)[0]).decode('cp932'))
        i += 2
    return codes


if __name__ == '__main__':
    tbl = font_table()
    idx = {c: i for i, c in enumerate(tbl)}
    files = [os.path.join(dp, f) for dp, _, fs in os.walk(ROOT) for f in fs if not f.endswith(('.XA', '.DMY', '.STR'))]
    blobs = {f: open(f, 'rb').read() for f in files}
    for w in sys.argv[1:]:
        ids = [idx[c] for c in w]
        for base in (0, 1, 2):
            for name, pat in (('u16le', b''.join(struct.pack('<H', i + base) for i in ids)),
                              ('u16be', b''.join(struct.pack('>H', i + base) for i in ids)),
                              ('u8', bytes(i + base for i in ids) if max(ids) + base < 256 else None)):
                if not pat:
                    continue
                for f, b in blobs.items():
                    n = b.count(pat)
                    if n:
                        print(w, base, name, os.path.relpath(f, ROOT), n, hex(b.find(pat)))
