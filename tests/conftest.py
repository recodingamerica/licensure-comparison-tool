"""Test setup: make `pipeline/` importable as `pipeline.<module>` and as the
individual sibling-import scripts use (sys.path-hacked at module top).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PIPELINE = REPO_ROOT / "pipeline"

# Make `pipeline.discover.x` style imports work
sys.path.insert(0, str(REPO_ROOT))
# Make `from _fetch import ...` style imports (used by some discover/* scripts) work
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "discover"))
