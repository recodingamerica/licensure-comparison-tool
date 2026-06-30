"""Tests for pipeline.discover.probe_justia pure logic.

The CDP/websocket I/O isn't unit-testable, but the deterministic bits are:
  - links() post-processing: code-relative href, 70-char label truncation
  - navigate()'s Cloudflare-challenge detection (the regex that tells you to go
    solve the challenge in the Chrome window)
We monkeypatch _eval / _cmd so no live Chrome is needed.
"""

import json

import pipeline.discover.probe_justia as pj


class TestLinks:
    def test_href_made_code_relative_and_label_truncated(self, monkeypatch):
        long_label = "Architects " + "x" * 100
        rows = [
            [long_label, "https://law.justia.com/codes/michigan/chapter-339/act-299/"],
            ["Plumbing", "https://law.justia.com/codes/michigan/chapter-338/"],
        ]
        monkeypatch.setattr(pj, "_eval", lambda ws, expr: json.dumps(rows))
        out = pj.links(ws=None)
        assert out[0][0] == long_label[:70]            # truncated
        assert out[0][1] == "michigan/chapter-339/act-299/"  # code-relative
        assert out[1][1] == "michigan/chapter-338/"

    def test_non_codes_href_passed_through(self, monkeypatch):
        rows = [["External", "https://example.com/foo"]]
        monkeypatch.setattr(pj, "_eval", lambda ws, expr: json.dumps(rows))
        out = pj.links(ws=None)
        assert out[0][1] == "https://example.com/foo"

    def test_empty_result(self, monkeypatch):
        monkeypatch.setattr(pj, "_eval", lambda ws, expr: None)
        assert pj.links(ws=None) == []


class TestNavigateCloudflareDetection:
    def _stub(self, monkeypatch, title):
        monkeypatch.setattr(pj, "_cmd", lambda *a, **k: {})
        monkeypatch.setattr(pj, "_eval", lambda ws, expr: title)
        monkeypatch.setattr(pj.time, "sleep", lambda *_: None)

    def test_challenge_title_warns(self, monkeypatch, capsys):
        self._stub(monkeypatch, "Just a moment...")
        title = pj.navigate(ws=None, url="https://law.justia.com/codes/x/", settle=0)
        assert title == "Just a moment..."
        assert "Cloudflare challenge" in capsys.readouterr().out

    def test_normal_title_no_warning(self, monkeypatch, capsys):
        self._stub(monkeypatch, "2024 Michigan Compiled Laws :: Chapter 339")
        pj.navigate(ws=None, url="https://law.justia.com/codes/x/", settle=0)
        assert "Cloudflare challenge" not in capsys.readouterr().out
