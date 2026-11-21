"""Unpack the disc before collection when the ROM is present, so a fresh clone runs the tree-based tests (build,
engine, extract) instead of skipping them; they skip only when rom/ itself is missing."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

if build.CUE.is_file() and (ROOT / "tools/mkpsxiso/dumpsxiso.exe").is_file():
    build.unpack()
