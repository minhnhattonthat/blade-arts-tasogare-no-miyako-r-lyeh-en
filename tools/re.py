"""MIPS recon helper for the EXE (or an overlay / RAM dump): disassemble a range, find lui+addiu/ori/lw/sw xrefs.

  python -X utf8 tools/re.py dis  ADDR [N]            disassemble N instrs from ADDR
  python -X utf8 tools/re.py xref ADDR [ADDR..]       code that builds ADDR with lui + lo16 (any reg, within 64 instrs)
  python -X utf8 tools/re.py jal  ADDR                callers (jal ADDR)
  python -X utf8 tools/re.py refs LO HI               every lui-built address in [LO, HI) (free-space check)
  --file F --base B   another image (overlay or RAM dump: --file ram.bin --base 0x80000000); default the EXE
"""
import argparse, struct
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_LITTLE_ENDIAN

EXE = 'work/disc/tree/SLPM_866.02'


def load(path, base):
    b = open(path, 'rb').read()
    if b[:8] == b'PS-X EXE':
        base = struct.unpack_from('<I', b, 0x18)[0]
        b = b[0x800:]
    return b, base


def words(b):
    return struct.unpack_from('<%dI' % (len(b) // 4), b)


def xrefs(b, base, targets, span=False):
    w = words(b)
    out = []
    for i, x in enumerate(w):
        if x >> 26 != 0x0F:  # lui
            continue
        rt, hi = (x >> 16) & 31, x & 0xFFFF
        for j in range(i + 1, min(i + 64, len(w))):
            y = w[j]
            op = y >> 26
            if (y >> 21) & 31 != rt:
                if op == 0x0F and (y >> 16) & 31 == rt:
                    break  # rt reloaded
                continue
            lo = y & 0xFFFF
            if op == 0x0D:  # ori
                a = (hi << 16) | lo
            elif op in (0x09, 0x20, 0x21, 0x23, 0x24, 0x25, 0x28, 0x29, 0x2B):  # addiu, loads, stores
                a = ((hi << 16) + (lo - 0x10000 if lo & 0x8000 else lo)) & 0xFFFFFFFF
            else:
                continue
            if span:
                if targets[0] <= a < targets[1]:
                    out.append((base + 4 * i, base + 4 * j, a))
                continue
            for t in targets:
                if a == t or (op != 0x09 and op != 0x0D and 0 <= t - a < 4):
                    out.append((base + 4 * i, base + 4 * j, t))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd')
    ap.add_argument('addr', nargs='+')
    ap.add_argument('--file', default=EXE)
    ap.add_argument('--base', default='0x80000000')
    a = ap.parse_args()
    b, base = load(a.file, int(a.base, 0))
    args = [int(x, 0) for x in a.addr]
    if a.cmd == 'dis':
        md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 | CS_MODE_LITTLE_ENDIAN)
        n = args[1] if len(args) > 1 else 40
        off = args[0] - base
        for ins in md.disasm(b[off:off + 4 * n], args[0]):
            print('%08X  %-8s %s' % (ins.address, ins.mnemonic, ins.op_str))
    elif a.cmd == 'xref':
        for lui, use, t in xrefs(b, base, args):
            print('%08X lui .. %08X use -> %08X' % (lui, use, t))
    elif a.cmd == 'refs':
        for lui, use, t in sorted(xrefs(b, base, args[:2], span=True), key=lambda r: r[2]):
            print('%08X lui .. %08X use -> %08X' % (lui, use, t))
    elif a.cmd == 'jal':
        t = (args[0] >> 2) & 0x3FFFFFF
        for i, x in enumerate(words(b)):
            if x == (0x03 << 26) | t:
                print('%08X jal %08X' % (base + 4 * i, args[0]))


if __name__ == '__main__':
    main()
