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
