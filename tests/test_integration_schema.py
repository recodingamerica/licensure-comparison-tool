"""Smoke tests: real extracted JSON validates against the Pydantic model.

If any of these fail, the schema and the on-disk data have drifted —
re-run extraction or fix the model. Skips quietly if no data is present.
"""

import json
from pathlib import Path

import pytest

from pipeline.extract.standard_model import LicensureRequirements, ScopeOfPractice

STRUCTURED_DIR = Path(__file__).resolve().parent.parent / "pipeline" / "results" / "structured"


def _structured_files(profession: str) -> list[Path]:
    p = STRUCTURED_DIR / profession
    if not p.exists():
        return []
    return sorted(f for f in p.glob("*.json") if not f.name.startswith("_"))


@pytest.mark.parametrize("profession", ["podiatry", "public_accountancy"])
def test_licensure_validates(profession):
    files = _structured_files(profession)
    if not files:
        pytest.skip(f"no {profession} structured files")
    errors = []
    for f in files:
        rec = json.loads(f.read_text())
        lic = rec.get("licensure")
        if not lic:
            continue
        try:
            LicensureRequirements.model_validate(lic)
        except Exception as e:
            errors.append((f.name, str(e)[:200]))
    if errors:
        pytest.fail(f"{len(errors)} {profession} files failed licensure validation: {errors[:3]}")


@pytest.mark.parametrize("profession", ["podiatry", "public_accountancy"])
def test_scope_validates(profession):
    files = _structured_files(profession)
    if not files:
        pytest.skip(f"no {profession} structured files")
    errors = []
    for f in files:
        rec = json.loads(f.read_text())
        scope = rec.get("scope")
        if not scope:
            continue
        try:
            ScopeOfPractice.model_validate(scope)
        except Exception as e:
            errors.append((f.name, str(e)[:200]))
    if errors:
        pytest.fail(f"{len(errors)} {profession} files failed scope validation: {errors[:3]}")


@pytest.mark.parametrize("profession", ["podiatry", "public_accountancy"])
def test_record_has_required_top_level_keys(profession):
    """Every extracted record should have state + profession + licensure + scope."""
    files = _structured_files(profession)
    if not files:
        pytest.skip(f"no {profession} structured files")
    REQUIRED = {"state", "profession", "licensure", "scope", "profession_specific"}
    bad = []
    for f in files:
        rec = json.loads(f.read_text())
        missing = REQUIRED - set(rec.keys())
        if missing:
            bad.append((f.name, sorted(missing)))
    if bad:
        pytest.fail(f"{len(bad)} files missing required keys: {bad[:3]}")
