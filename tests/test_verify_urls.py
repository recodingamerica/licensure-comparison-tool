"""Tests for pipeline.eval.verify_urls.probe verdict logic.

The fetch I/O isn't unit-testable, but the classification is — it's the whole
point of the tool (HTTP 200 != valid; the MN year-form stub returned 200). We
monkeypatch fetch() + extract_child_links() with the HTML shapes observed on
2026-07-02: a real Justia chapter page, a section leaf, and Justia's not-found
page that a wrong URL form (e.g. /codes/minnesota/2024/chapter-147/) resolves to.
"""

import pipeline.eval.verify_urls as vu

STATUTE_BODY = "147.01 Board of Medical Practice. " + ("The board shall license " * 200)
NAV_CHROME = "Log In Sign Up Find a Lawyer Ask a Lawyer Research the Law Law Schools"


def _patch(monkeypatch, status, html, err=None, children=()):
    monkeypatch.setattr(vu, "fetch", lambda url: (status, html, err))
    monkeypatch.setattr(vu, "extract_child_links", lambda html, url: (list(children), []))


class TestLive:
    def test_chapter_with_section_links(self, monkeypatch):
        html = f"<title>Minnesota Statutes Chapter 147 (2025) - Board Of Medical Practice</title><body>{NAV_CHROME}</body>"
        _patch(monkeypatch, 200, html, children=[{"url": f"s{i}"} for i in range(37)])
        assert vu.probe("u")["verdict"] == "LIVE"

    def test_section_leaf_no_children_but_body(self, monkeypatch):
        # a leaf has no child links; the statute text carries it
        html = f"<title>Minnesota Statutes Section 147.01 (2025)</title><body>{STATUTE_BODY}</body>"
        _patch(monkeypatch, 200, html, children=[])
        rec = vu.probe("u")
        assert rec["verdict"] == "LIVE"
        assert rec["body_chars"] >= vu.BODY_MIN_CHARS


class TestBroken:
    def test_notfound_page_is_dead404(self, monkeypatch):
        # Justia's soft not-found page: empty title, no links, thin body, marker
        html = "<title></title><body>The page you requested could not be found. " + NAV_CHROME + "</body>"
        _patch(monkeypatch, 200, html, children=[])
        assert vu.probe("u")["verdict"] == "DEAD_404"

    def test_empty_shell_without_marker_is_stub(self, monkeypatch):
        # 200, empty title, no links, only nav chrome, NO not-found marker
        html = f"<title></title><body>{NAV_CHROME}</body>"
        _patch(monkeypatch, 200, html, children=[])
        assert vu.probe("u")["verdict"] == "STUB"

    def test_generic_title_is_stub(self, monkeypatch):
        html = f"<title>Justia</title><body>{NAV_CHROME}</body>"
        _patch(monkeypatch, 200, html, children=[])
        assert vu.probe("u")["verdict"] == "STUB"


class TestChallengeAndError:
    def test_403_is_challenge(self, monkeypatch):
        _patch(monkeypatch, 403, "<title></title><body>Just a moment...</body>", children=[])
        assert vu.probe("u")["verdict"] == "CHALLENGE"

    def test_challenge_marker_is_challenge(self, monkeypatch):
        _patch(monkeypatch, 200, "<title></title><body>Checking your browser before accessing</body>", children=[])
        assert vu.probe("u")["verdict"] == "CHALLENGE"

    def test_fetch_error_is_error(self, monkeypatch):
        _patch(monkeypatch, None, None, err="Timeout")
        assert vu.probe("u")["verdict"] == "ERROR"
