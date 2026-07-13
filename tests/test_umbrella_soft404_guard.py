"""Regression guard: pull_state_umbrella must reject Justia soft-404 blobs.

pull_umbrella_text drifted from pull_text.pull_state — its section loop only
skipped truly-empty extractions (`if not text`), so Justia's fixed 1144-char
"Justia Legal Resources / Find a Lawyer" nav blob (a URL that 200s with no real
content div) was silently ingested as umbrella statute text. The fix routes the
extracted text through the shared bad_section_text() guard for parity with
pull_state. These tests exercise that guard end-to-end with fetch mocked.
"""

from __future__ import annotations

import json

import pipeline.ingest.pull_umbrella_text as pu


def _setup(tmp_path, monkeypatch, extract_returns: str):
    chdir = tmp_path / "chapters"
    chdir.mkdir()
    txtdir = tmp_path / "text"
    txtdir.mkdir()
    monkeypatch.setattr(pu, "UMBRELLA_CHAPTERS_DIR", chdir)
    monkeypatch.setattr(pu, "UMBRELLA_TEXT_DIR", txtdir)
    (chdir / "ZZ.json").write_text(json.dumps({
        "state": "ZZ",
        "umbrella_chapters": [{
            "slug": "chapter-1",
            "label": "General Provisions",
            "url": "https://law.justia.com/codes/zz/chapter-1/section-1/",
        }],
    }))
    # Section-URL chapter → no child collection needed.
    monkeypatch.setattr(pu, "is_section_url", lambda u: True)
    monkeypatch.setattr(pu, "fetch", lambda u: (200, "<html></html>", None))
    monkeypatch.setattr(pu, "polite_sleep", lambda: None)
    monkeypatch.setattr(pu, "extract_section_text", lambda html: extract_returns)
    # bad_section_text is intentionally NOT patched — the real guard must run.


def test_pull_state_umbrella_rejects_soft404_navblob(tmp_path, monkeypatch):
    blob = "Justia Legal Resources\nFind a Lawyer\n" + "x" * 1100
    _setup(tmp_path, monkeypatch, extract_returns=blob)
    rec = pu.pull_state_umbrella("ZZ", force=True)
    assert rec is not None
    assert rec["sections"] == [], "soft-404 nav blob must not be ingested"


def test_pull_state_umbrella_rejects_thin_extraction(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, extract_returns="   ")
    rec = pu.pull_state_umbrella("ZZ", force=True)
    assert rec is not None
    assert rec["sections"] == []


def test_pull_state_umbrella_keeps_real_statute_text(tmp_path, monkeypatch):
    real = "Section 1. Every applicant for licensure shall satisfy the board. " * 5
    _setup(tmp_path, monkeypatch, extract_returns=real)
    rec = pu.pull_state_umbrella("ZZ", force=True)
    assert rec is not None
    assert len(rec["sections"]) == 1
    assert rec["sections"][0]["umbrella_chapter_slug"] == "chapter-1"
    assert rec["sections"][0]["text"] == real
