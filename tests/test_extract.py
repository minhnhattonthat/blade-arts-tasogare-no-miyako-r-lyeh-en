"""Phase 4: script/*.tsv re-encodes to the original bytes, and the text ranges are fully covered."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import extract  # noqa: E402
import rawtext  # noqa: E402
import sjisscan  # noqa: E402
import sol  # noqa: E402

pytestmark = pytest.mark.skipif(not sol.DEFAULT.is_file(), reason="disc not dumped (work/disc)")


def sol_tsv():
    return [r for p in sorted((ROOT / "script/sol").glob("*.tsv")) for r in extract.read_tsv(p, extract.SOL_COLS)]


def test_sol_tsv_reencodes_and_repacks_identical():
    orig = sol.DEFAULT.read_bytes()
    want = {(bid, gi): x for bid, pos, blk in sol.blocks(orig) for gi, s, o, f, x in sol.strings(blk)}
    rows = sol_tsv()
    texts = {}
    for r in rows:
        _, bid, gi = r["id"].split(".")
        texts[int(bid), int(gi)] = r["jp"].encode("cp932")
    assert len(rows) == len(texts) == len(want) == 3351
    assert texts == want
    assert sol.pack(orig, texts) == orig


def test_sol_pack_moves_text():
    orig = sol.DEFAULT.read_bytes()
    new = sol.pack(orig, {(1, 1): b"t3Hello"})
    texts = {(bid, gi): x for bid, pos, blk in sol.blocks(new) for gi, s, o, f, x in sol.strings(blk)}
    assert texts[1, 1] == b"t3Hello" and texts[1, 2] and len(new) == len(orig)


def test_raw_tsv_reencodes_and_matches_scan():
    for path in rawtext.FILES:
        b = (rawtext.TREE / path).read_bytes()
        rows = extract.read_tsv(ROOT / "script/raw" / extract.raw_name(path), extract.RAW_COLS)
        assert [r["id"] for r in rows] == [f"{path}:{i:05X}" for i, *_ in rawtext.find(path)]
        for r in rows:
            off = int(r["id"].rsplit(":", 1)[1], 16)
            x = rawtext.encode(r["jp"])
            assert b[off:off + len(x) + 1] == x + b"\0", r["id"]


def test_every_japanese_run_is_extracted():
    """Coverage on the original disc: every kana run in the EXE and DATA/ is inside an extracted string (or a
    hand-checked NOISE run / NOISE_FILES file of pixel data)."""
    tree = rawtext.TREE
    files = ["SLPM_866.02"] + [f"DATA/{p.name}" for p in sorted((tree / "DATA").iterdir())
                               if p.name != "SOL.SRP" and p.suffix in (".BIN", ".DAT", ".PAC")]
    missed = []
    for path in files:
        if path in rawtext.NOISE_FILES:
            continue
        spans = rawtext.covered(path) if path in rawtext.FILES else []
        for off, t in sjisscan.runs((tree / path).read_bytes(), 2):
            if not any(s <= off < e for s, e in spans):
                missed.append((path, hex(off), t))
    assert not missed


def test_extract_never_clobbers(tmp_path, monkeypatch):
    monkeypatch.setattr(extract, "SCRIPT", tmp_path)
    extract.main()
    p = tmp_path / "sol" / "001.tsv"
    p.write_text("keep", encoding="utf-8")
    extract.main()
    assert p.read_text(encoding="utf-8") == "keep"
