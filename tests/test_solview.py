import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import sol  # noqa: E402
import solview  # noqa: E402

BUILT = ROOT / "build" / "files" / "DATA" / "SOL.SRP"


@pytest.mark.skipif(not (sol.DEFAULT.is_file() and BUILT.is_file()), reason="needs work/disc and a build")
def test_targets_cover_every_message_with_its_old_id_and_sector():
    orig, new = sol.DEFAULT.read_bytes(), BUILT.read_bytes()
    ts = solview.targets(orig, new)
    ids = [r[0] for p in sorted((ROOT / "script" / "sol").glob("*.tsv"))
           for r in (ln.split("\t") for ln in p.read_text(encoding="utf-8").splitlines()[1:]) if r[0]]
    assert sorted(t[0] for t in ts) == sorted(ids)
    moved = sol.remap(orig, new)
    assert moved, "the build moves blocks: the old ids must still be used"
    for i, key, old, n, off, tbl in ts:
        assert i == f"sol.{old}.{n}" and key == 0x50000000 | old << 16 | n
        sec = new[off:off + sol.SECTOR]
        k = struct.unpack_from("<I", sec, 4)[0] if struct.unpack_from("<I", sec, 0)[0] == 8 else 0
        first = tbl[k - 1] + 1 if k else 0
        assert first <= n <= tbl[k], (i, k)   # the copied sector holds message n (what 0x800786A8 looks up)
