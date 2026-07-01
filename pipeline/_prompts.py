"""Load LLM system prompts from config/prompts.yaml by name.

Single import point so any stage that needs a prompt does:
    from pipeline._prompts import load_prompt
    SYSTEM_PROMPT = load_prompt("extract_state")
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml


_PROMPTS_PATH = Path(__file__).resolve().parent / "config" / "prompts.yaml"


@lru_cache(maxsize=1)
def _all_prompts() -> dict:
    return yaml.safe_load(_PROMPTS_PATH.read_text()) or {}


def load_prompt(stage: str, role: str = "system") -> str:
    """Return the prompt text for a given stage + role. Raises KeyError if missing."""
    data = _all_prompts()
    if stage not in data:
        raise KeyError(f"prompts.yaml has no entry for stage {stage!r}")
    section = data[stage]
    if role not in section:
        raise KeyError(f"prompts.yaml has no role {role!r} for stage {stage!r}")
    return section[role]
