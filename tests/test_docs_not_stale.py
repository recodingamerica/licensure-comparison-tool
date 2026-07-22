"""Guard against doc-rot — the repo's main legibility failure mode.

A runbook keeps naming a module after it's been deleted or renamed, and a newcomer
following it hits a wall. This scans the docs a newcomer is actually sent to (README,
CLAUDE, ARCHITECTURE, and the surviving runbooks) and fails on any reference that no
longer resolves, so a stale pointer can't merge in the first place.

It checks only the two UNAMBIGUOUS, machine-checkable reference forms — it does not
police prose, and it does not look at dated/historical notes (those get deleted, not
maintained):
  * `-m pipeline.a.b.c`   — a runnable module (must have a .py or be a package)
  * `pipeline/a/b.py`     — an explicit source-file path (must exist)
"""

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _tracked_docs() -> list[Path]:
    """The HAND-MAINTAINED docs: git-tracked .md, minus the generated output dirs. We police
    docs a human edits (where a stale module ref rots silently) — NOT pipeline output
    (methodology field-dicts, the handoff doc, gap reports), which regenerate, nor the ~570
    untracked reports on disk. A generated doc's refs are guarded at their source (the
    generator module, covered by the import sweep), not on every output copy."""
    tops = ["README.md", "CLAUDE.md", "ARCHITECTURE.md", "SETUP.md", "pipeline/client/README.md"]
    generated = ("docs/methodology/", "docs/handoff/", "docs/reports/")
    try:
        out = subprocess.run(["git", "ls-files", "docs", *tops], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout.split()
        return [ROOT / p for p in out if p.endswith(".md") and not p.startswith(generated)]
    except Exception:  # not a git checkout — fall back to the known maintained docs
        return [ROOT / p for p in tops] + sorted((ROOT / "docs" / "runbooks").glob("*.md"))


DOCS = _tracked_docs()

# The docs a non-coder actually reads — these must never describe the retired CDP-Chrome
# fetch workflow (Scrapling is the sole fetcher since 2026-07-13). CLAUDE.md is excluded on
# purpose: it's the operator/history doc and legitimately records that CDP was retired.
CLIENT_FACING = [
    ROOT / "pipeline" / "client" / "README.md",
    ROOT / "docs" / "handoff" / "technical_documentation.md",
    *sorted((ROOT / "docs" / "runbooks").glob("client_*.md")),
]

RUN_RE = re.compile(r"-m (pipeline\.[a-zA-Z0-9_.]+)")   # python -m pipeline.x.y
PY_RE = re.compile(r"(pipeline/[a-zA-Z0-9_./]+\.py)")   # pipeline/x/y.py
# Retired-workflow markers (NOT bare "Chrome" — "no Chrome window to open" is fine).
RETIRED_RE = re.compile(r"remote-debugging|:9222|\bCDP\b|hand-started|hand-driven|start Chrome|debugging port", re.I)


def _module_exists(dotted: str) -> bool:
    base = ROOT / Path(dotted.rstrip(".").replace(".", "/"))
    return base.with_suffix(".py").exists() or (base / "__init__.py").exists()


def test_maintained_docs_reference_only_real_modules():
    dead = []
    for doc in DOCS:
        if not doc.exists():
            continue
        text = doc.read_text()
        for ref in RUN_RE.findall(text):
            if not _module_exists(ref):
                dead.append(f"{doc.relative_to(ROOT)}: -m {ref}")
        for ref in PY_RE.findall(text):
            if not (ROOT / ref).exists():
                dead.append(f"{doc.relative_to(ROOT)}: {ref}")
    assert not dead, (
        "maintained docs point at modules/files that no longer exist "
        "(fix the doc or delete it):\n  " + "\n  ".join(sorted(set(dead)))
    )


def test_client_facing_docs_have_no_retired_fetch_workflow():
    """The non-coder docs must not tell someone to start a debug Chrome / solve a CDP
    challenge — that workflow was retired (Scrapling clears the wall headless). Guards
    against the CDP language creeping back, including via the generated handoff doc."""
    hits = []
    for doc in CLIENT_FACING:
        if not doc.exists():
            continue
        for m in RETIRED_RE.finditer(doc.read_text()):
            hits.append(f"{doc.relative_to(ROOT)}: '{m.group(0)}'")
    assert not hits, (
        "client-facing docs describe the retired CDP-Chrome fetch workflow "
        "(Scrapling is the sole fetcher now):\n  " + "\n  ".join(hits)
    )
