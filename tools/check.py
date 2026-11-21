"""One-command check (the pre-commit hook runs this): every test under tests/ plus the text lint once it exists."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# no:faulthandler: unicorn's mem_map raises a handled access violation on Windows that faulthandler prints as a crash
sys.exit(subprocess.call([sys.executable, "-X", "utf8", "-m", "pytest", "-q", "-p", "no:faulthandler",
                          str(ROOT / "tests")], cwd=ROOT))
