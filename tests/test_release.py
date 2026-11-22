import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import release  # noqa: E402


def test_sol_japanese_flags_kana_not_english_or_symbols(monkeypatch):
    # English pair "He", fullwidth ★ + ASCII control pair, kana あ
    msgs = [b"\xc8\xe5", "★".encode("shift_jis") + b"b3", "あ".encode("shift_jis")]
    monkeypatch.setattr(release.sol, "blocks", lambda d: [(7, 0, b"")])
    monkeypatch.setattr(release.sol, "strings", lambda blk: [(i, 0, 0, 7, t) for i, t in enumerate(msgs)])
    assert release.sol_japanese(b"") == [(7, 2, "あ")]
