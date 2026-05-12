"""Single source of truth for loading project env vars.

Loads the project-local `.env` (utah/.env) via python-dotenv. Maps
`CLAUDE_API_KEY` → `ANTHROPIC_API_KEY` so litellm picks it up. Idempotent;
safe to call from every entry-point script.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parent.parent
_PROJECT_ENV = _REPO_ROOT / ".env"


def load_env() -> None:
    load_dotenv(_PROJECT_ENV, override=False)
    if not os.environ.get("ANTHROPIC_API_KEY") and os.environ.get("CLAUDE_API_KEY"):
        os.environ["ANTHROPIC_API_KEY"] = os.environ["CLAUDE_API_KEY"]
