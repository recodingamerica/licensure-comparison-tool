"""Staging + review + apply of HELD candidate refresh changes."""
import json
import pipeline.ingest.refresh_corpus as rc


def _corpus(cites):
    return {"sections": [{"citation": c, "label": f"L{c}", "text": f"text of {c} " * 20} for c in cites]}


def test_stage_then_load_and_review(tmp_path, monkeypatch):
    monkeypatch.setattr(rc, "PENDING_DIR", tmp_path / "pending")
    monkeypatch.setattr(rc, "prior_committed", lambda p: _corpus(["1-1", "1-2", "1-3"]))
    new = _corpus(["1-1", "1-2", "1-10", "1-11"])          # 1-3 removed; 1-10/1-11 added

    rc.stage_pending("run9", "money_transmitter", "CO", new,
                     {"result": "REGRESSION", "reason": "1 missing", "prev": 3, "new": 4})
    pend = rc._load_pending("run9")
    assert len(pend) == 1 and pend[0]["profession"] == "money_transmitter"

    diff = rc._section_diff(new, "money_transmitter", "CO")
    assert diff["removed"] == ["1-3"] and set(diff["added"]) == {"1-10", "1-11"}

    page = rc.build_review_html("run9")
    html = page.read_text()
    assert "money_transmitter:CO" in html and "REGRESSION" in html
    assert "1-3" in html and "1-10" in html                # removed + added both shown
    assert "--apply --run-id run9" in html                 # live apply command

    # no-op when run_id is unset (ad-hoc single pull leaves no artifact)
    rc.stage_pending(None, "x", "Y", new, {})
    assert not (tmp_path / "pending" / "None").exists()


def _c(cites, chars=200):
    return {"sections": [{"citation": c, "text": "x" * chars} for c in cites]}


def test_obviously_legit_accepts_clean_same_chapter_growth():
    old = _c(["11-110-101", "11-110-102", "11-110-103"])
    # amendment/renumber within the same chapter, grew + clean -> auto-accept
    assert rc._obviously_legit(_c(["11-110-101", "11-110-301", "11-110-302", "11-110-303"]), old)
    assert rc._obviously_legit(_c(["11-110-1", "11-110-2", "11-110-3"]), old)  # same-count renumber


def test_obviously_legit_holds_ambiguous():
    old = _c(["11-110-101", "11-110-102", "11-110-103"])
    assert not rc._obviously_legit(_c(["11-110-101"]), old)                       # shrink
    assert not rc._obviously_legit(_c(["42-1-1", "42-1-2", "42-1-3", "42-1-4"]), old)  # chapter swap
    assert not rc._obviously_legit(_c(["11-110-1", "11-110-2", "11-110-3"], chars=10), old)  # collapse
    dirty = _c(["11-110-1", "11-110-2", "11-110-3"]) 
    dirty["sections"].append({"citation": "11-110-4", "text": "", "error": "bad"})
    assert not rc._obviously_legit(dirty, old)                                    # error section
