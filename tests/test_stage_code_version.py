"""Changing a stage's logic must be a conscious decision about its stored outputs.

Freshness compares a stage's INPUTS and its RECIPE (prompt + model + CODE_VERSION). It
cannot see the stage's own code, so output written by a superseded implementation keeps
reporting "current" until someone remembers to bump `CODE_VERSION[stage]` by hand.

Nobody does. Every entry is still 1 except publish. Meanwhile trim's accounting was
fixed at some point and 63 cells kept their pre-fix output — NV/HVAC holding 1 section
of a 162-section chapter — while provenance called them current and extraction read a
fraction of the statute (#118).

Hashing the module into the recipe automatically would be worse: a comment edit would
invalidate every cell and trigger a re-run costing thousands. So this is DETECTION, not
automation. Edit a stage engine and this test fails with two options:

  1. The change alters what the stage PRODUCES → bump CODE_VERSION[stage] in
     provenance.py. Existing outputs correctly go stale and get re-run.
  2. The change is a refactor/comment/log tweak that cannot alter output → update the
     pinned hash below, saying so.

Either way somebody answered the question, which is the part that was missing.

Full-line comments and blank lines are stripped before hashing, so ordinary commenting
doesn't cause churn. Docstrings are NOT stripped — verify_negatives keeps its prompt in
one, and a prompt change is exactly what must be caught.
"""
import hashlib

import pytest

from pipeline.paths import PIPELINE_ROOT
from pipeline.provenance import CODE_VERSION

# Stage -> the modules whose logic decides that stage's output. Not every file it
# imports: the engine, the thing whose behaviour change should invalidate stored work.
STAGE_MODULES = {
    "clean":   ["ingest/clean_text.py"],
    "trim":    ["ingest/trim_state.py"],
    "extract": ["extract/extract_state.py", "extract/extract_state_batch.py"],
    "schema":  ["extract/discover_schema.py"],
    "verify":  ["extract/verify_negatives.py"],
    "mapprep": ["map_prep/run.py", "map_prep/bucket_text.py"],
    "publish": ["publish/build_frontend.py"],
}

# sha256(stripped source)[:16] per stage, recorded deliberately. Update ONLY together
# with the judgement described in the module docstring.
PINNED = {
    "clean":   "646739b0fdf57776",
    "trim":    "95942b5c84784332",
    # 2026-07-31: added drop_skipped() at both gate sites — verified-absence cells are
    # removed from the queue before submit. Changes WHICH cells extract runs on, never
    # what a run produces for a cell, so no stored output was made by superseded logic
    # and CODE_VERSION stays at 2 (bumped this morning for the two-pass scope rule).
    "extract": "17c2fbcd5ff9046a",
    "schema":  "ce3a4fff44437a13",
    "verify":  "023b289280b002a8",
    "mapprep": "9d15d2bb31cc0e10",
    "publish": "e8c2b08549bfc23e",
}


def _stage_hash(stage: str) -> str:
    """Hash a stage's engine source, ignoring blank lines and full-line comments."""
    parts = []
    for rel in STAGE_MODULES[stage]:
        src = (PIPELINE_ROOT / rel).read_text()
        kept = [
            ln.rstrip() for ln in src.splitlines()
            if ln.strip() and not ln.lstrip().startswith("#")
        ]
        parts.append(f"--- {rel}\n" + "\n".join(kept))
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()[:16]


@pytest.mark.parametrize("stage", sorted(STAGE_MODULES))
def test_stage_logic_change_was_answered_for(stage):
    actual = _stage_hash(stage)
    assert actual == PINNED[stage], (
        f"the `{stage}` stage's logic changed ({', '.join(STAGE_MODULES[stage])}).\n\n"
        f"Existing {stage} outputs on disk were produced by the OLD code and still report "
        f"'current' — freshness can't see this (it compares inputs and recipe, not the "
        f"stage's own source). That is how 63 trims kept pre-fix output while extraction "
        f"read a fraction of the statute (#118).\n\n"
        f"Pick one:\n"
        f"  1. It changes what {stage} PRODUCES -> bump CODE_VERSION['{stage}'] "
        f"(currently {CODE_VERSION.get(stage)}) in pipeline/provenance.py, so stored "
        f"outputs go stale and get re-run.\n"
        f"  2. It cannot change output (refactor, logging, comments) -> set "
        f"PINNED['{stage}'] = '{actual}' here.\n"
    )


def test_every_stage_with_a_code_version_is_pinned():
    """A stage that gains a CODE_VERSION but no pin would be silently unguarded."""
    missing = sorted(set(CODE_VERSION) - set(STAGE_MODULES) - {"pull"})
    assert not missing, (
        f"these stages have a CODE_VERSION but no pinned source hash, so a logic change "
        f"to them is undetectable: {missing}. Add their engine module(s) to "
        f"STAGE_MODULES and record a pin. ('pull' is exempt — its output is the fetched "
        f"corpus, whose freshness is the fetch itself.)"
    )
