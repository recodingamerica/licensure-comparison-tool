"""Tests for the umbrella coverage / residual summary.

coverage_summary is the "how much is still unresolved" detector: it counts
every section by scope_source so the undetermined tail stays visible.
"""

from __future__ import annotations

import json

import pytest


@pytest.fixture
def fake_scope_dir(tmp_path, monkeypatch):
    from pipeline.discover import umbrella_coverage_matrix as m
    monkeypatch.setattr(m, "UMBRELLA_SCOPE_DIR", tmp_path)
    return tmp_path


def _write(scope_dir, state, sources):
    sections = [{"scope_source": s, "url": f"u{i}"} for i, s in enumerate(sources)]
    (scope_dir / f"{state}.json").write_text(json.dumps({"state": state, "sections": sections}))


def test_summary_none_when_missing(fake_scope_dir):
    from pipeline.discover.umbrella_coverage_matrix import coverage_summary
    assert coverage_summary("ZZ") is None


def test_summary_counts_classified_vs_undetermined(fake_scope_dir):
    from pipeline.discover.umbrella_coverage_matrix import coverage_summary
    _write(fake_scope_dir, "XX", [
        "universal", "anchor_universal", "anchor_enumeration",
        "inherited_enumeration", "undetermined", "undetermined",
    ])
    s = coverage_summary("XX")
    assert s["total_sections"] == 6
    assert s["classified"] == 4
    assert s["undetermined"] == 2
    assert s["pct_classified"] == round(100 * 4 / 6, 1)


def test_summary_treats_missing_source_as_undetermined(fake_scope_dir):
    from pipeline.discover.umbrella_coverage_matrix import coverage_summary
    # scope_source None/absent must count as undetermined, not vanish.
    (fake_scope_dir / "YY.json").write_text(json.dumps({
        "state": "YY",
        "sections": [{"scope_source": None, "url": "a"}, {"url": "b"}],
    }))
    s = coverage_summary("YY")
    assert s["total_sections"] == 2
    assert s["undetermined"] == 2
    assert s["classified"] == 0
