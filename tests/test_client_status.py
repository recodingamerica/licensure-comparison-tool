"""Tests for pipeline.client.status — the stage-detection precedence and the
cost/summary aggregation that the dashboard and runner both rely on."""

import pytest

from pipeline.client import status


# --- _stage precedence --------------------------------------------------------

@pytest.fixture
def stage_dirs(tmp_path, monkeypatch):
    """Point the three file-backed stage dirs at empty tmp dirs. `_has_corpus`
    (the text/pulled level) is monkeypatched per-test."""
    dirs = {}
    for name in ("STRUCTURED_DIR", "TRIMMED_DIR", "CLEAN_DIR"):
        d = tmp_path / name
        monkeypatch.setattr(status, name, d)
        dirs[name] = d
    return dirs


def _touch(d, prof, state):
    (d / prof).mkdir(parents=True, exist_ok=True)
    (d / prof / f"{state}.json").write_text("{}")


def test_stage_done_beats_everything(stage_dirs, monkeypatch):
    monkeypatch.setattr(status, "_has_corpus", lambda p, s: True)
    _touch(stage_dirs["STRUCTURED_DIR"], "x", "UT")
    _touch(stage_dirs["TRIMMED_DIR"], "x", "UT")
    _touch(stage_dirs["CLEAN_DIR"], "x", "UT")
    assert status._stage("x", "UT", {}) == "done"


def test_stage_trimmed(stage_dirs, monkeypatch):
    monkeypatch.setattr(status, "_has_corpus", lambda p, s: True)
    _touch(stage_dirs["TRIMMED_DIR"], "x", "UT")
    _touch(stage_dirs["CLEAN_DIR"], "x", "UT")
    assert status._stage("x", "UT", {}) == "trimmed"


def test_stage_cleaned(stage_dirs, monkeypatch):
    monkeypatch.setattr(status, "_has_corpus", lambda p, s: True)
    _touch(stage_dirs["CLEAN_DIR"], "x", "UT")
    assert status._stage("x", "UT", {}) == "cleaned"


def test_stage_pulled_when_only_corpus(stage_dirs, monkeypatch):
    monkeypatch.setattr(status, "_has_corpus", lambda p, s: True)
    assert status._stage("x", "UT", {}) == "pulled"


def test_stage_needs_fetch_when_located_but_no_corpus(stage_dirs, monkeypatch):
    monkeypatch.setattr(status, "_has_corpus", lambda p, s: False)
    loc = {"x": {"UT": {"url": "https://law.justia.com/codes/utah/..."}}}
    assert status._stage("x", "UT", loc) == "needs-fetch"


@pytest.mark.parametrize("url", [None, "null", ""])
def test_stage_absent_when_located_null(stage_dirs, monkeypatch, url):
    monkeypatch.setattr(status, "_has_corpus", lambda p, s: False)
    loc = {"x": {"UT": {"url": url}}}
    assert status._stage("x", "UT", loc) == "absent"


def test_stage_verified_absence_beats_locator_url(stage_dirs, monkeypatch):
    """A verified absence is a correct-blank: even when the gap-harvest locator has
    a (mis-located) URL, the cell is 'absent', not 'needs-fetch' — so it never counts
    as pending scrape work."""
    monkeypatch.setattr(status, "_has_corpus", lambda p, s: False)
    loc = {"x": {"UT": {"url": "https://law.justia.com/codes/utah/wrong-chapter/"}}}
    absences = {"x": {"UT": {"basis": "not_regulated"}}}
    assert status._stage("x", "UT", loc, absences) == "absent"
    # without the absences map it would (wrongly) look like a fetch gap
    assert status._stage("x", "UT", loc) == "needs-fetch"


def test_stage_unknown_when_never_searched(stage_dirs, monkeypatch):
    monkeypatch.setattr(status, "_has_corpus", lambda p, s: False)
    assert status._stage("x", "UT", {}) == "unknown"


# --- build() aggregation + cost math ------------------------------------------

def test_build_aggregation_and_costs(monkeypatch):
    monkeypatch.setattr(status, "load_professions", lambda: {"a": {}, "b": {}, "_hidden": {}})
    monkeypatch.setattr(status.C, "ALL_STATES", ["S1", "S2", "S3"])
    monkeypatch.setattr(status.C, "load_json", lambda *a, **k: {})
    monkeypatch.setattr(status, "_chapter_urls", lambda p, s: None)
    monkeypatch.setattr(status, "_has_schema", lambda p: True)
    monkeypatch.setattr(status.provenance, "last_stamped", lambda p, s: None)
    monkeypatch.setattr(status.provenance, "cell_freshness", lambda p, s: ("current", None))
    stages = {
        ("a", "S1"): "done", ("a", "S2"): "trimmed", ("a", "S3"): "needs-fetch",
        ("b", "S1"): "cleaned", ("b", "S2"): "absent", ("b", "S3"): "unknown",
    }
    monkeypatch.setattr(status, "_stage", lambda p, s, loc, va=None: stages[(p, s)])

    data = status.build()

    # underscore-prefixed profession filtered out
    assert set(data["professions"]) == {"a", "b"}

    a = data["professions"]["a"]["summary"]
    assert (a["done"], a["ready"], a["needs_fetch"], a["absent"], a["unknown"]) == (1, 1, 1, 0, 0)
    # trimmed -> extract only ($0.15) counts toward finish; needs-fetch not runnable
    assert a["cost_to_finish"] == pytest.approx(status.COST_EXTRACT)
    assert a["cost_runnable"] == pytest.approx(status.COST_EXTRACT)  # nothing stale

    b = data["professions"]["b"]["summary"]
    assert (b["ready"], b["absent"], b["unknown"]) == (1, 1, 1)
    assert b["cost_to_finish"] == pytest.approx(status.COST_TO_TRIM)  # cleaned = trim+extract

    t = data["totals"]
    assert t["cells_done"] == 1 and t["cells_ready"] == 2 and t["cells_needs_fetch"] == 1
    assert t["cost_to_finish"] == pytest.approx(status.COST_EXTRACT + status.COST_TO_TRIM)


def test_build_gates_no_schema(monkeypatch):
    """A corpus-on-disk cell for a profession with no discovered schema must NOT be
    runnable or charged — extract can't reach it. It's counted as needs_schema instead of
    ready, and stays out of the queue (run=False, cost=0)."""
    monkeypatch.setattr(status, "load_professions", lambda: {"a": {}})
    monkeypatch.setattr(status.C, "ALL_STATES", ["S1", "S2"])
    monkeypatch.setattr(status.C, "load_json", lambda *a, **k: {})
    monkeypatch.setattr(status, "_chapter_urls", lambda p, s: None)
    monkeypatch.setattr(status, "_has_schema", lambda p: False)
    monkeypatch.setattr(status.provenance, "last_stamped", lambda p, s: None)
    monkeypatch.setattr(status.provenance, "cell_freshness", lambda p, s: ("current", None))
    stages = {("a", "S1"): "trimmed", ("a", "S2"): "cleaned"}
    monkeypatch.setattr(status, "_stage", lambda p, s, loc, va=None: stages[(p, s)])

    data = status.build()
    sm = data["professions"]["a"]
    s = sm["summary"]
    assert s["has_schema"] is False
    assert s["needs_schema"] == 2 and s["ready"] == 0
    assert s["cost_to_finish"] == 0.0 and s["cost_runnable"] == 0.0
    for st in ("S1", "S2"):
        assert sm["states"][st]["run"] is False and sm["states"][st]["cost"] == 0.0
        assert sm["states"][st]["needs_schema"] is True
    assert data["totals"]["cells_needs_schema"] == 2
    assert data["totals"]["professions_no_schema"] == 1


def test_build_freshness_split(monkeypatch):
    """A done cell is split into current / stale / unstamped, and a stale cell is
    queue-eligible (run=True) with the re-run cost."""
    monkeypatch.setattr(status, "load_professions", lambda: {"a": {}})
    monkeypatch.setattr(status.C, "ALL_STATES", ["S1", "S2", "S3"])
    monkeypatch.setattr(status.C, "load_json", lambda *a, **k: {})
    monkeypatch.setattr(status, "_chapter_urls", lambda p, s: None)
    monkeypatch.setattr(status.provenance, "last_stamped", lambda p, s: None)
    monkeypatch.setattr(status, "_stage", lambda p, s, loc, va=None: "done")
    fresh = {("a", "S1"): ("current", None),
             ("a", "S2"): ("stale", "extract"),
             ("a", "S3"): ("unstamped", None)}
    monkeypatch.setattr(status.provenance, "cell_freshness", lambda p, s: fresh[(p, s)])

    sm = status.build()["professions"]["a"]
    s = sm["summary"]
    assert (s["done"], s["done_current"], s["done_stale"], s["done_unstamped"]) == (3, 1, 1, 1)
    assert s["cost_to_refresh"] == pytest.approx(status.COST_EXTRACT)  # stale at extract
    assert sm["states"]["S2"]["run"] is True and sm["states"]["S2"]["fresh"] == "stale"
    assert sm["states"]["S1"]["run"] is False and sm["states"]["S3"]["run"] is False
