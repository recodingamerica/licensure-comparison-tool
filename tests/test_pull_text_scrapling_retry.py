"""fetch_via_scrapling retries a clearly-bad response (empty/challenge/error),
recreating the session, but never loops on a small-but-real page."""
from __future__ import annotations

from pipeline.ingest import pull_text as pt

URL = "https://law.justia.com/codes/x/"


class _Page:
    def __init__(self, html, status=200):
        self.html_content = html
        self.status = status


def _patch(monkeypatch, sess):
    monkeypatch.setattr(pt, "_get_scrapling_session", lambda: sess)
    monkeypatch.setattr(pt, "_reset_scrapling_session", lambda: None)
    monkeypatch.setattr(pt.time, "sleep", lambda *_: None)


def test_retries_then_recovers_on_empty(monkeypatch):
    calls = {"n": 0}

    class S:
        def fetch(self, url, **k):
            calls["n"] += 1
            return _Page("" if calls["n"] == 1 else "<html>" + "x" * 3000 + "</html>")

    _patch(monkeypatch, S())
    status, html, err = pt.fetch_via_scrapling(URL)
    assert calls["n"] == 2 and status == 200 and err is None and len(html) > 2000


def test_challenge_body_triggers_retry(monkeypatch):
    seq = ["<html>Just a moment...</html>", "<html>" + "x" * 3000 + "</html>"]

    class S:
        i = 0
        def fetch(self, url, **k):
            p = _Page(seq[self.i]); self.i += 1; return p

    _patch(monkeypatch, S())
    status, html, err = pt.fetch_via_scrapling(URL)
    assert err is None and "moment" not in html.lower()


def test_gives_up_after_retries_returns_last(monkeypatch):
    class S:
        def fetch(self, url, **k):
            return _Page("", status=200)  # always empty

    _patch(monkeypatch, S())
    status, html, err = pt.fetch_via_scrapling(URL)
    assert err and "bad response" in err


def test_small_but_real_page_not_retried(monkeypatch):
    """A genuinely small section page (non-empty, 2xx, no challenge) is returned on
    the FIRST try — the retry must not loop on valid short content."""
    calls = {"n": 0}

    class S:
        def fetch(self, url, **k):
            calls["n"] += 1
            return _Page("<html>short but real section text</html>")

    _patch(monkeypatch, S())
    status, html, err = pt.fetch_via_scrapling(URL)
    assert calls["n"] == 1 and err is None
