"""Corpus-source policy guard: statute text is fetched from Justia + PA ONLY.

pull_text.fetch() is the single choke point where corpus text is pulled. It must
fail loud on any host other than Justia (routed to Scrapling) or PA's legacy
static endpoint — so a stray non-Justia/PA target can never be silently scraped
in as corpus. A cell with no Justia/PA source is an accepted source_unavailable
gap, not a reason to bolt on another fetcher.

(This guards only corpus-text fetching; discovery/web-search research is a
separate, unguarded layer and is not exercised here.)
"""

from __future__ import annotations

import pytest

import pipeline.ingest.pull_text as pt


@pytest.mark.parametrize("url", [
    "https://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=4077",
    "https://arkleg.state.ar.us/Home/FTPDocument?path=/ACTS/2025R/Public/ACT435.pdf",
    "https://rules.ok.gov/code",
    "https://www.law.cornell.edu/regulations/oklahoma/title-35",
    "https://revisor.mn.gov/statutes/",  # a former official source, now off-policy
])
def test_fetch_refuses_non_justia_pa_host(url):
    with pytest.raises(RuntimeError, match="non-Justia/PA host"):
        pt.fetch(url)


def test_fetch_allows_pa_host(monkeypatch):
    """PA's legacy static endpoint passes the guard and routes to curl_cffi."""
    class _Resp:
        status_code = 200
        text = "<html>PA act</html>"
    monkeypatch.setattr(pt.cffi_requests, "get", lambda *a, **k: _Resp())
    status, html, err = pt.fetch("https://www.legis.state.pa.us/WU01/LI/LI/US/HTM/x.htm")
    assert status == 200
    assert err is None
    assert "PA act" in html


def test_fetch_allows_justia_host(monkeypatch):
    """Justia routes to Scrapling (never reaches the allowlist branch)."""
    monkeypatch.setattr(pt, "_scrapling_available", lambda: True)
    monkeypatch.setattr(pt, "fetch_via_scrapling", lambda u: (200, "<html>justia</html>", None))
    status, html, err = pt.fetch("https://law.justia.com/codes/oklahoma/title-2/")
    assert status == 200
    assert "justia" in html
