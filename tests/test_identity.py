"""Phase 3 identity build: unpack + repack with no edits gives the original disc byte for byte. Keep it green forever."""
import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

ORIG_SHA1 = "c266b85e1af7fa57605814e0c47fd68f002998c8"


def sha1(p):
    with open(p, "rb") as f:
        return hashlib.file_digest(f, "sha1").hexdigest()


@pytest.mark.skipif(not build.CUE.is_file() or not (ROOT / "tools/mkpsxiso/mkpsxiso.exe").is_file(),
                    reason="no original disc or mkpsxiso")
def test_identity_rebuild(tmp_path):
    # Override one file with its own bytes: proves the build's file-swap path keeps the disc identical too.
    sol = (build.TREE / "DATA" / "SOL.SRP")
    out = build.build(tmp_path, files={"DATA/SOL.SRP": sol.read_bytes()} if sol.is_file() else {})
    assert sha1(out) == ORIG_SHA1
    assert (tmp_path / f"{build.NAME}.cue").is_file()
