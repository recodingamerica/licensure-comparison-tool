"""Tests for pipeline.eval.source_purity — the config-independent Justia-purity
check. Uses a synthetic corpus dir (never the real repo data) so it stays fast
and doesn't depend on what's currently pulled.
"""
import json

import pipeline.eval.source_purity as sp


def _write_corpus(tmp_path, prof, state, urls):
    d = tmp_path / prof
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{state}.json").write_text(json.dumps(
        {"sections": [{"url": u} for u in urls]}))


def test_all_justia_is_clean(tmp_path, monkeypatch):
    monkeypatch.setattr(sp, "TEXT_DIR", tmp_path)
    _write_corpus(tmp_path, "medicine", "CA",
                  ["https://law.justia.com/codes/california/x/"])
    assert sp.scan() == {}


def test_allowlisted_pa_host_is_not_a_violation(tmp_path, monkeypatch):
    monkeypatch.setattr(sp, "TEXT_DIR", tmp_path)
    _write_corpus(tmp_path, "podiatry", "PA",
                  ["https://www.legis.state.pa.us/WU01/x.HTM"])
    assert sp.scan() == {}


def test_pa_allowlist_does_not_cover_other_states(tmp_path, monkeypatch):
    # the allowlist is per-state — PA's exception must not leak to e.g. CT
    monkeypatch.setattr(sp, "TEXT_DIR", tmp_path)
    _write_corpus(tmp_path, "medicine", "CT",
                  ["https://www.legis.state.pa.us/WU01/x.HTM"])
    violations = sp.scan()
    assert "CT" in violations
    assert violations["CT"]["medicine"]["www.legis.state.pa.us"] == 1


def test_stale_official_source_regression_is_caught(tmp_path, monkeypatch):
    # the exact bug this tool exists for: a state that's supposed to be 100%
    # Justia has some sections that regressed onto its old official-source host
    monkeypatch.setattr(sp, "TEXT_DIR", tmp_path)
    _write_corpus(tmp_path, "nursing", "WA", [
        "https://law.justia.com/codes/washington/title-18/x/",
        "https://app.leg.wa.gov/RCW/default.aspx?cite=18.79",
    ])
    violations = sp.scan()
    assert violations == {"WA": {"nursing": {"app.leg.wa.gov": 1}}}


def test_main_exits_nonzero_on_violation(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sp, "TEXT_DIR", tmp_path)
    _write_corpus(tmp_path, "nursing", "WA", ["https://app.leg.wa.gov/x"])
    monkeypatch.setattr("sys.argv", ["source_purity", "--quiet"])
    assert sp.main() == 1


def test_main_exits_zero_when_clean(tmp_path, monkeypatch):
    monkeypatch.setattr(sp, "TEXT_DIR", tmp_path)
    _write_corpus(tmp_path, "medicine", "CA",
                  ["https://law.justia.com/codes/california/x/"])
    monkeypatch.setattr("sys.argv", ["source_purity", "--quiet"])
    assert sp.main() == 0


def test_real_committed_corpus_is_clean():
    """The actual CI gate: runs against the real, checked-in TEXT_DIR (no
    monkeypatch) — this is what catches a future re-pull silently regressing
    onto a stale official-source host, in every CI run, with no config trusted."""
    violations = sp.scan()
    assert violations == {}, (
        f"non-Justia sections found outside ALLOWED_NON_JUSTIA: {violations}. "
        "Either this is a genuine new non-Justia source (update "
        "ALLOWED_NON_JUSTIA deliberately) or a re-pull regressed onto an old "
        "official-source path (re-pull the affected (profession, state) from Justia)."
    )
