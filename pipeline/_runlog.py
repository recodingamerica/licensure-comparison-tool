"""Cross-stage run-log — each pipeline stage records when it last ran.

Operational metadata (NOT a committed artifact; gitignored at results/.run_log.json):

    { "<stage>": {"last_run": "<iso>", "git_sha": "<short>", ...extra} }

`record_run(stage, **meta)` is best-effort — it never raises into a stage, so adding
it can't break a pull/extract. View with `python -m pipeline._runlog`. Answers
"when did X last run / is its output current?" — pair last_run with the data it made.
Unlike the field-dictionary's deterministic `data_as_of`, this is wall-clock on purpose.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

_PIPELINE_DIR = Path(__file__).resolve().parent
RUNLOG_PATH = _PIPELINE_DIR / "results" / ".run_log.json"


def _git_sha() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                             cwd=_PIPELINE_DIR.parent, capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or None
    except Exception:
        return None


def record_run(stage: str, **meta) -> None:
    """Update this stage's last-run entry. Best-effort; swallows all errors."""
    try:
        log = json.loads(RUNLOG_PATH.read_text()) if RUNLOG_PATH.exists() else {}
        log[stage] = {"last_run": datetime.now().isoformat(timespec="seconds"),
                      "git_sha": _git_sha(), **meta}
        RUNLOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        RUNLOG_PATH.write_text(json.dumps(log, indent=2, sort_keys=True))
    except Exception:
        pass


def load_runlog() -> dict:
    try:
        return json.loads(RUNLOG_PATH.read_text()) if RUNLOG_PATH.exists() else {}
    except Exception:
        return {}


def main() -> None:
    log = load_runlog()
    if not log:
        print("no runs recorded yet")
        return
    print(f"{'stage':26s} {'last run':20s} {'sha':9s} detail")
    print("-" * 70)
    for stage in sorted(log, key=lambda s: log[s].get("last_run", ""), reverse=True):
        e = log[stage]
        detail = " ".join(f"{k}={v}" for k, v in e.items() if k not in ("last_run", "git_sha"))
        print(f"{stage:26s} {e.get('last_run', '?'):20s} {(e.get('git_sha') or '-'):9s} {detail}")


if __name__ == "__main__":
    main()
