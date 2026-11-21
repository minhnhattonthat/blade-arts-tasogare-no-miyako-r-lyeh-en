"""List the EXE item table (docs/re/debug.md §Items): id, type, flags, dev label, JP name, built English name.

  python -X utf8 tools/items.py [--exe build/files/SLPM_866.02]

Used to pick stress-save items (longest English names) for tools/debug/save.py.
"""
import argparse
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABLE = 0x800B50F0


def cstr(d, base, addr):
    o = addr - base
    if not 0 <= o < len(d):
        return "?"
    return d[o:d.index(b"\0", o)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", default=str(ROOT / "work/disc/tree/SLPM_866.02"))
    a = ap.parse_args()
    d = Path(a.exe).read_bytes()
    t_addr = struct.unpack_from("<I", d, 0x18)[0]
    base = t_addr - 0x800  # file offset 0x800 = t_addr
    o = TABLE - base
    while d[o] != 0xFF:
        iid, typ = d[o], d[o + 1]
        flags, en, jp = struct.unpack_from("<III", d, o + 4)
        label = cstr(d, base, en)
        name = cstr(d, base, jp)
        name = name.decode("shift_jis", "replace") if isinstance(name, bytes) else name
        label = label.decode("ascii", "replace") if isinstance(label, bytes) else label
        print(f"{iid:02X}\t{typ:02X}\t{flags:08X}\t{label}\t{name}\t{jp:08X}")
        o += 16


if __name__ == "__main__":
    main()
