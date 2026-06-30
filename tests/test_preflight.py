"""Preflight gate: each of the 4 blockers + a clean pass.

The gate reads `results/discovered/` and `results/trimmed/` via the paths
module, so we monkeypatch those module-level dirs at a tmp tree.
"""

from __future__ import annotations

import json

import pytest

import pipeline.extract.preflight as pf


@pytest.fixture
def tree(tmp_path, monkeypatch):
    """A throwaway results tree; returns helpers to plant schema/trimmed files."""
    discovered = tmp_path / "discovered"
    trimmed = tmp_path / "trimmed"
    discovered.mkdir()
    trimmed.mkdir()
    monkeypatch.setattr(pf, "DISCOVERED_DIR", discovered)
    monkeypatch.setattr(pf, "TRIMMED_DIR", trimmed)

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
