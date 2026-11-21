"""Dump the game text to script/*.tsv (phase 4). Never overwrites an existing file unless --force (English lives there).

  script/sol/<block>.tsv      DATA/SOL.SRP: id (sol.<block>.<index>), sector, jp, en, notes
  script/raw/<file>.tsv       raw Shift-JIS in the EXE/overlays (tools/rawtext.py): id (<file>:<offset>), addr, room,
                              refs, jp, en, notes. room = bytes up to the next non-zero byte; refs = referencing words
                              (file offsets, `+k` = into the string, `-` = none found)

Text is Shift-JIS decoded as is; the game's control codes stay inline as ASCII (docs/re/text.md). Raw strings write
byte 0A as {n}. Tests: tests/test_extract.py (re-encoding every jp gives the original bytes; SOL.SRP repacks identical).

usage: python -X utf8 tools/extract.py [--force]
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import rawtext  # noqa: E402
import sol  # noqa: E402

SCRIPT = ROOT / "script"
SOL_COLS = ["id", "sector", "jp", "en", "notes"]
RAW_COLS = ["id", "addr", "room", "refs", "jp", "en", "notes"]
# raw strings that are data or dev leftovers, not player text (checked by hand)
RAW_NOTES = {
    "DATA/STATUS.BIN:0FA98": "data: digit glyph table (indexed by digit); keep 10 two-byte glyphs",
    "DATA/STATUS.BIN:00200": "fullwidth space (padding glyph)",
    "DATA/STATUS.BIN:00204": "printf format: %s%s: %s pieces",
    "DATA/LOADSAVE.BIN:00004": "dev: location-table terminator ('Terminator (needed at the end of the table)')",
    "DATA/LOADSAVE.BIN:001C8": "dev: test-play location name",
    "DATA/GAME.BIN:00594": "debug error message",
    "DATA/GAME.BIN:005B0": "debug error message",
    "SLPM_866.02:02664": "debug message",
    "SLPM_866.02:02EC4": "debug message (memory allocation failed)",
    "DATA/STATUS.BIN:00E70": "the original has a stray 0B byte mid-line",
}


def raw_name(path):
    return path.replace("/", "_") + ".tsv"


def read_tsv(path, cols):
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    assert rows[0] == cols, (path, rows[0])
    for r in rows[1:]:
        assert len(r) == len(cols), (path, r)
    return [dict(zip(cols, r)) for r in rows[1:]]


def write_tsv(path, cols, rows):
    for r in rows:
        assert not any(c in str(v) for v in r for c in "\t\r\n"), r
        assert len(r) == len(cols), r
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")


def sol_rows():
    """{block_id: rows} from the original SOL.SRP."""
    out = {}
    for bid, pos, blk in sol.blocks(sol.DEFAULT.read_bytes()):
        out[bid] = [[f"sol.{bid}.{gi}", s, x.decode("cp932"), "", "" if x else "empty in the original; leave empty"]
                    for gi, s, o, flags, x in sol.strings(blk)]
    return out


def raw_rows():
    """{disc path: rows} from the original EXE/overlays."""
    out = {}
    for path in rawtext.FILES:
        rows = []
        for i, a, room, refs, x in rawtext.find(path):
            rid = f"{path}:{i:05X}"
            note = RAW_NOTES.get(rid, "" if refs else "no reference found (reached another way)")
            rows.append([rid, f"{a:08X}", room, ",".join(refs) or "-", rawtext.decode(x), "", note])
        out[path] = rows
    return out


def main(force=False):
    jobs = [(SCRIPT / "sol" / f"{bid:03d}.tsv", SOL_COLS, rows) for bid, rows in sol_rows().items()]
    jobs += [(SCRIPT / "raw" / raw_name(p), RAW_COLS, rows) for p, rows in raw_rows().items()]
    wrote = kept = 0
    for path, cols, rows in jobs:
        if path.exists() and not force:
            kept += 1
            continue
        write_tsv(path, cols, rows)
        wrote += 1
    print(f"wrote {wrote} files, kept {kept} existing (--force to overwrite)")


if __name__ == "__main__":
    main("--force" in sys.argv)
