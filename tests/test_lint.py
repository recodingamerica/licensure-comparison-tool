"""Lint gate — keeps the correctness ruleset (pyflakes `F`) clean so unused imports,
undefined names, dead locals, and duplicate dict keys can't creep back in.

Only the `F` rules run (configured in pyproject `[tool.ruff.lint]`) — the point is to catch
bugs, not to police the codebase's deliberate lazy-import / terse style. Skips if ruff isn't
installed (it's an optional `dev` dependency), so a minimal runtime install still passes.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def test_ruff_correctness_clean():
    ruff = shutil.which("ruff") or str(ROOT / "pipeline" / ".venv" / "bin" / "ruff")
    if not Path(ruff).exists() and not shutil.which("ruff"):
        pytest.skip("ruff not installed (pip install -e '.[dev]' to enable the lint gate)")
    # No --select: use the pyproject [tool.ruff.lint] config (select F, ignore F401/F541),
    # so the gate matches the documented ruleset instead of overriding it on the CLI.
    r = subprocess.run([ruff, "check", "pipeline", "tests"],
                       cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, f"ruff found correctness issues:\n{r.stdout}\n{r.stderr}"
