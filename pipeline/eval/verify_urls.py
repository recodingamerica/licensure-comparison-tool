"""URL health probe — LLM-free. Distinguishes a working statute URL from a
soft-stub (HTTP 200 but no statute content), a dead 404, or a Cloudflare
challenge.

Motivation (the MN lesson, 2026-07-02): HTTP 200 is meaningless on Justia. A
wrong URL form — e.g. the year-versioned `/codes/minnesota/2024/chapter-147/`
that Justia serves as an empty shell — returns 200 with a full 50 KB HTML
skeleton and ZERO statute text. We only caught it because the flip recipe forced
a manual leaf-verify, done ad-hoc in throwaway python each time. This tool
encodes the reliable discriminators so leaf-verify is a command, not a habit.

The discriminators (all structural, no LLM):
  * <title>       a real Justia statute page carries a statute title
                  ("Minnesota Statutes Chapter 364 (2024) - Criminals; …"); the
                  soft-stub carries an EMPTY <title>. This is the strongest tell.
  * child links   a chapter/index page links its sections; a stub links none.
  * body text     a section leaf has substantial visible statute text; the stub's
                  visible text is just the Justia nav chrome.

Verdicts:
  LIVE       real page — statute <title> AND (section links OR substantial body)
  STUB       200 but empty/generic <title>, no section links, thin body — the URL
             form is wrong; go FIND THE RIGHT LINK
  DEAD_404   explicit not-found
  CHALLENGE  Cloudflare interstitial never cleared — a RETRY condition (re-solve
             in the debug Chrome), not a data problem
  ERROR      fetch failed (network / timeout)

This is now a LIBRARY (`probe` + its structural helpers). The runnable URL-health
check moved to `python -m pipeline.eval.corpus_status gate --check-urls`, which
probes the suspect cells' mapped urls and folds STUB/DEAD_404 into the one health
gate. `refresh_corpus` also imports `probe` to explain an EMPTY pull.

`probe` fetches through pipeline.ingest.pull_text.fetch (Justia -> headless
Scrapling, other hosts -> curl_cffi), so a Justia probe just needs Scrapling
installed (pip install "scrapling[fetchers]" && scrapling install).
"""

from __future__ import annotations

import re

from pipeline.ingest.pull_text import fetch, extract_child_links

_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)
_CHALLENGE_MARKERS = ("just a moment", "attention required", "cf-challenge",
                      "enable javascript and cookies", "checking your browser")
_NOTFOUND_MARKERS = ("page not found", "404 not found", "the page you requested",
                     "no longer available", "could not be found")

# A statute title says "Chapter/Section/Title/Article/Part N", "§", "Statutes",
# or "Code". A stub title is empty, or a bare "Justia" site name.
_STATUTE_TITLE_RE = re.compile(
    r"\b(chapter|section|title|article|part|statutes?|code|§)\b|\d", re.I)
_GENERIC_TITLE_RE = re.compile(r"^(justia|law\.?justia|page not found|)$", re.I)

# Visible-body threshold: the Justia nav chrome alone renders ~500-900 chars of
# visible text ("Log In Sign Up Find a Lawyer …"). A real statute leaf is far
# longer. Calibrated against observed stub vs live pages (see module test).
BODY_MIN_CHARS = 1200


def _visible_text(html: str) -> str:
    t = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def probe(url: str) -> dict:
    """Fetch one URL and classify it. Never raises — returns a verdict dict."""
    status, html, err = fetch(url)
    rec: dict = {"url": url, "status": status}
    if err or html is None:
        rec.update(verdict="ERROR", detail=err or "no html")
        return rec

    low = html.lower()
    m = _TITLE_RE.search(html)
    title = (m.group(1).strip() if m else "")
    try:
        children, _ = extract_child_links(html, url)
    except Exception:
        children = []
    n_child = len(children)
    body_chars = len(_visible_text(html))

    title_ok = bool(_STATUTE_TITLE_RE.search(title)) and not _GENERIC_TITLE_RE.match(title)
    has_content = n_child >= 1 or body_chars >= BODY_MIN_CHARS
    rec.update(title=title[:80], n_child=n_child, body_chars=body_chars)

    # Order matters: challenge and 404 are distinct remedies from STUB.
    if status in (403, 503) or (any(k in low for k in _CHALLENGE_MARKERS) and not title_ok):
        rec["verdict"] = "CHALLENGE"
    elif status == 404 or (any(k in low for k in _NOTFOUND_MARKERS) and n_child == 0 and not title_ok):
        rec["verdict"] = "DEAD_404"
    elif title_ok and has_content:
        rec["verdict"] = "LIVE"
    else:
        # 200 (or unknown) with no statute title and no content == the MN stub.
        rec["verdict"] = "STUB"
    return rec
