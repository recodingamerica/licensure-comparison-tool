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
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DOCS = [
    ROOT / "README.md",
    ROOT / "CLAUDE.md",
    ROOT / "ARCHITECTURE.md",
    *sorted((ROOT / "docs" / "runbooks").glob("*.md")),
]

RUN_RE = re.compile(r"-m (pipeline\.[a-zA-Z0-9_.]+)")   # python -m pipeline.x.y
PY_RE = re.compile(r"(pipeline/[a-zA-Z0-9_./]+\.py)")   # pipeline/x/y.py


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
