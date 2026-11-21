"""Shift-JIS text scan that keeps only runs with real kana (skips TIM pixel noise).

usage: python -X utf8 tools/sjisscan.py FILE [min_chars=4] [--count]
Prints offset<TAB>text for runs of >= min_chars full-width chars with >= 2 kana and >= 40% kana/kanji.
"""
import sys


def runs(data, min_chars=4):
    i, n = 0, len(data)
    while i < n:
        j, chars = i, []
        while j + 1 < n:
            b = data[j]
            if (0x81 <= b <= 0x9F or 0xE0 <= b <= 0xEA) and 0x40 <= data[j + 1] <= 0xFC and data[j + 1] != 0x7F:
                try:
                    chars.append(data[j:j + 2].decode('cp932'))
                except UnicodeDecodeError:
                    break
                j += 2
            else:
                break
        if len(chars) >= min_chars:
            kana = sum(1 for c in chars if 'ぁ' <= c <= 'ヾ')
            jp = sum(1 for c in chars if 'ぁ' <= c <= 'ヾ' or '一' <= c <= '鿿')
            if kana >= 2 and jp >= 0.6 * len(chars):
                yield i, ''.join(chars)
            i = j
        else:
            i += 1


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    data = open(args[0], 'rb').read()
    hits = list(runs(data, int(args[1]) if len(args) > 1 else 4))
    if '--count' in sys.argv:
        print(len(hits))
    else:
        for off, t in hits:
            print(f'{off:08X}\t{t}')
