import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import sjisscan  # noqa: E402

SOL = ROOT / "work" / "disc" / "tree" / "DATA" / "SOL.SRP"


def test_sjisscan_keeps_kana_runs_only():
    data = b"\x00\x01" + "剣を納めよ".encode("cp932") + b"\x00" + "ＡＢＣＤＥ".encode("cp932")
    assert [t for _, t in sjisscan.runs(data)] == ["剣を納めよ"]


@pytest.mark.skipif(not SOL.is_file(), reason="disc not dumped (work/disc)")
def test_sol_srp_text_is_xor_8c():
    x = bytes(b ^ 0x8C for b in SOL.read_bytes()[0x800:0x900])
    assert "剣を納めよ".encode("cp932") in x
