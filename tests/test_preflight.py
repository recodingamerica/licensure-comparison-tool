"""Preflight gate: each of the 4 blockers + a clean pass.

The gate reads `results/discovered/` and `results/trimmed/` via the paths
module, so we monkeypatch those module-level dirs at a tmp tree.
"""

from __future__ import annotations

import json

import pytest

import pipeline.extract.preflight as pf

# Captured before any fixture monkeypatches pf.schema_dirty — the real (lru_cached)
# function, for the test that exercises its git parsing directly.
_REAL_SCHEMA_DIRTY = pf.schema_dirty


@pytest.fixture
def tree(tmp_path, monkeypatch):
    """A throwaway results tree; returns helpers to plant schema/trimmed files.
    provenance + git are stubbed to their benign answers so these tests never couple
    to the real repo's data state (override per-test to exercise the new blockers)."""
    discovered = tmp_path / "discovered"
    trimmed = tmp_path / "trimmed"
    discovered.mkdir()
    trimmed.mkdir()
    monkeypatch.setattr(pf, "DISCOVERED_DIR", discovered)
    monkeypatch.setattr(pf, "TRIMMED_DIR", trimmed)
    monkeypatch.setattr(pf.provenance, "check", lambda stage, p, s: "unstamped")
    clean = lambda prof: False  # noqa: E731
    clean.cache_clear = lambda: None
    monkeypatch.setattr(pf, "schema_dirty", clean)

    def schema(prof: str) -> None:
        (discovered / f"{prof}.json").write_text(json.dumps({"discovered_fields": []}))

    def trim(prof: str, state: str, record: dict) -> None:
        d = trimmed / prof
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{state}.json").write_text(json.dumps(record))

    return schema, trim


def test_no_schema(tree):
    schema, trim = tree
    # No discovered/<prof>.json at all.
    assert pf.check_pair("ghost", "UT") == "NO_SCHEMA"


def test_no_trimmed(tree):
    schema, trim = tree
    schema("dietetics")
    # schema present but no trimmed file
    assert pf.check_pair("dietetics", "IA") == "NO_TRIMMED"


def test_empty_trimmed(tree):
    schema, trim = tree
    schema("dietetics")
    trim("dietetics", "IA", {"sections": []})
    assert pf.check_pair("dietetics", "IA") == "EMPTY_TRIMMED"


def test_poisoned_legacy(tree):
    schema, trim = tree
    schema("dietetics")
    trim("dietetics", "IA", {
        "sections": [{"text": "x"}],
        "skipped": [{"citation": "1-1", "reason": "llm_failed_kept_by_default"}],
    })
    assert pf.check_pair("dietetics", "IA") == "POISONED"


def test_poisoned_flag(tree):
    schema, trim = tree
    schema("dietetics")
    trim("dietetics", "IA", {"sections": [{"text": "x"}], "trim_degraded": True})
    assert pf.check_pair("dietetics", "IA") == "POISONED"


def test_clean_pass(tree):
    schema, trim = tree
    schema("dietetics")
    trim("dietetics", "IA", {"sections": [{"text": "real"}], "skipped": []})
    assert pf.check_pair("dietetics", "IA") is None


def test_partial_skipped_not_poisoned(tree):
    schema, trim = tree
    schema("dietetics")
    # Some skipped are a real "no decision" default-keep, not the LLM-fail
    # fallback — not poisoned.
    trim("dietetics", "IA", {
        "sections": [{"text": "x"}],
        "skipped": [{"citation": "1-1"}, {"citation": "1-2", "reason": "llm_failed_kept_by_default"}],
    })
    assert pf.check_pair("dietetics", "IA") is None


def test_run_preflight_aggregates(tree):
    schema, trim = tree
    schema("dietetics")
    trim("dietetics", "IA", {"sections": [{"text": "real"}]})
    trim("dietetics", "OH", {"sections": []})
    queue = {"dietetics": ["IA", "OH"], "ghost": ["UT"]}
    report = pf.run_preflight(queue)
    assert report["ok"] is False
    assert report["ready"] == [("dietetics", "IA")]
    assert report["blocked"]["EMPTY_TRIMMED"] == [("dietetics", "OH")]
    assert report["blocked"]["NO_SCHEMA"] == [("ghost", "UT")]
    # report formats without error
    assert "PREFLIGHT: FAIL" in pf.format_report(report)


def test_run_preflight_all_clean(tree):
    schema, trim = tree
    schema("dietetics")
    trim("dietetics", "IA", {"sections": [{"text": "real"}]})
    report = pf.run_preflight({"dietetics": ["IA"]})
    assert report["ok"] is True
    assert "PREFLIGHT: PASS" in pf.format_report(report)


# --- the two 2026-07-29 blockers: existence isn't freshness -----------------------
# Two batches in one day passed the old preflight and were garbage anyway: one built
# on trims a revert had restored to pre-de-pollution copies (STALE_UPSTREAM), one on
# an uncommitted re-derived schema that was reverted minutes later (SCHEMA_DIRTY).

def test_stale_trim_blocks(tree, monkeypatch):
    schema, trim = tree
    schema("dietetics")
    trim("dietetics", "IA", {"sections": [{"text": "real"}]})
    monkeypatch.setattr(pf.provenance, "check",
                        lambda stage, p, s: "stale" if stage == "trim" else "current")
    assert pf.check_pair("dietetics", "IA") == "STALE_UPSTREAM"


def test_stale_clean_blocks(tree, monkeypatch):
    schema, trim = tree
    schema("dietetics")
    trim("dietetics", "IA", {"sections": [{"text": "real"}]})
    monkeypatch.setattr(pf.provenance, "check",
                        lambda stage, p, s: "stale" if stage == "clean" else "current")
    assert pf.check_pair("dietetics", "IA") == "STALE_UPSTREAM"


def test_unstamped_upstream_does_not_block(tree):
    # Pre-provenance history: no stamp at all must stay extractable (the fixture's
    # provenance stub answers "unstamped" for everything).
    schema, trim = tree
    schema("dietetics")
    trim("dietetics", "IA", {"sections": [{"text": "real"}]})
    assert pf.check_pair("dietetics", "IA") is None


def test_dirty_schema_blocks(tree, monkeypatch):
    schema, trim = tree
    schema("dietetics")
    trim("dietetics", "IA", {"sections": [{"text": "real"}]})
    dirty = lambda prof: True  # noqa: E731
    dirty.cache_clear = lambda: None
    monkeypatch.setattr(pf, "schema_dirty", dirty)
    assert pf.check_pair("dietetics", "IA") == "SCHEMA_DIRTY"
    report = pf.run_preflight({"dietetics": ["IA"]})
    assert report["ok"] is False
    assert report["blocked"]["SCHEMA_DIRTY"] == [("dietetics", "IA")]


def test_schema_dirty_reads_git_porcelain(tree, monkeypatch):
    # The real predicate: tracked+modified (" M") is dirty; untracked ("??") — a brand
    # new profession's first schema — is not. Calls the unwrapped function (no lru_cache)
    # against a stubbed `git status --porcelain`.
    real = _REAL_SCHEMA_DIRTY.__wrapped__
    lines = {"v": ""}
    fake = type("S", (), {"run": staticmethod(
        lambda *a, **k: type("R", (), {"stdout": lines["v"]})())})
    monkeypatch.setattr(pf, "subprocess", fake)
    lines["v"] = " M pipeline/results/discovered/dietetics.json\n"
    assert real("dietetics") is True
    lines["v"] = "?? pipeline/results/discovered/newprof.json\n"
    assert real("newprof") is False
    lines["v"] = ""
    assert real("dietetics") is False
