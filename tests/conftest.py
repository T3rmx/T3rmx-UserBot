import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
paths = [str(ROOT), str(ROOT / "T3rmx-UserBot")]
for p in paths:
    if p not in sys.path:
        sys.path.insert(0, p)
