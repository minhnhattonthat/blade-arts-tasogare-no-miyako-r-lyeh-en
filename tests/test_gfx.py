"""tools/gfx.py: every gfx.tsv TIM round-trips through its PNG export, and the build writes only pixel blocks."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import gfx  # noqa: E402

pytestmark = pytest.mark.skipif(not (build.TREE / "SLPM_866.02").is_file(), reason="no unpacked disc (work/disc/tree)")


@pytest.mark.parametrize("row", gfx.rows(), ids=lambda r: r["name"])
def test_roundtrip_and_copies(row):
    for f, o in gfx.targets(row):
        d = build.original(f)
        _, _, p, n, _, _ = gfx.tim(d, o)
        assert gfx.pixels(d, o, gfx.export(d, o, int(row["clut"] or 0))) == d[p:p + n], (f, hex(o))


def test_writes_only_pixel_blocks():
    files, w = {}, build.Writes()
    gfx.patch(files, w, build.original)
    blocks = {}
    for row in gfx.rows():
        for f, o in gfx.targets(row):
            _, _, p, n, _, _ = gfx.tim(build.original(f), o)
            blocks.setdefault(f, []).append((p, p + n))
    for f, rows in w.log.items():
        for off, a, b, by in rows:
            assert any(lo <= off and off + len(b) <= hi for lo, hi in blocks[f]), (f, hex(off), by)
