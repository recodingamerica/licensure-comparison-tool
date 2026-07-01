"""Test setup: make the repo root importable so `pipeline.<pkg>.<module>`
absolute imports resolve without an editable install."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
