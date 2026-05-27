"""Load the canonical MERGED umbrella scope for a state.

The deterministic walker (`assign_umbrella_scope`) writes
`umbrella_scope/<ST>.json`; the LLM fallback (`llm_scope_fallback`, Pass 3)
writes its decisions for walker-undetermined sections to
`umbrella_scope_llm/<ST>.json`. The merged view is the walker output with the
LLM decisions overlaid (undetermined-only), each section tagged with
`scope_method` ("walker" | "llm").

Every consumer — the web build, the DB load, the coverage report — should load
scope through here, so they all see the same walker+LLM picture and nobody
re-implements the overlay.
"""

from __future__ import annotations

import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import RESULTS_DIR  # noqa: E402
from scope_sources import overlay_llm_decisions  # noqa: E402

UMBRELLA_SCOPE_DIR = RESULTS_DIR / "umbrella_scope"
UMBRELLA_SCOPE_LLM_DIR = RESULTS_DIR / "umbrella_scope_llm"


def load_merged_scope(state: str) -> dict | None:
    """Return the walker scope dict with Pass-3 LLM decisions overlaid onto the
    sections the walker left undetermined. Each section carries `scope_method`.
    None if the state has no walker output."""
    scope_path = UMBRELLA_SCOPE_DIR / f"{state}.json"
    if not scope_path.exists():
        return None
    data = json.loads(scope_path.read_text())
    llm_path = UMBRELLA_SCOPE_LLM_DIR / f"{state}.json"
    llm_by_url: dict[str, dict] = {}
    if llm_path.exists():
        llm_by_url = {d["url"]: d for d in json.loads(llm_path.read_text()).get("decisions", [])}
    data["sections"] = overlay_llm_decisions(data.get("sections", []), llm_by_url)
    return data


def merged_scope_by_url(state: str) -> dict[str, dict]:
    """{url -> merged section} — for consumers that look sections up by url."""
    data = load_merged_scope(state)
    if data is None:
        return {}
    return {s["url"]: s for s in data.get("sections", []) if s.get("url")}
