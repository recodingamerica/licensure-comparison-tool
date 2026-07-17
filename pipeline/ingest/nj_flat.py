"""New Jersey's flat statute layout — the single source of truth for its URL grammar.

Justia publishes NJ with **no chapter pages at all**: all ~2,286 sections of title-45
sit flat directly under the title, with the chapter encoded as a token inside each
section slug:

    chapter (conceptual):  45:5A          (citation form, e.g. "45:5A-10")
    chapter url (built):   …/codes/new-jersey/title-45/chapter-5a/
    section url (real):    …/codes/new-jersey/title-45/section-45-5a-10/

This one fact broke the pipeline in several places independently, because each assumed
the normal Justia nesting (a /chapter-X/ page whose sections live at /chapter-X/section-Y/):
  * the walk stored the whole title page as one blob (fixed by section_slug_re);
  * a built /chapter-token/ url that Justia doesn't 301 to the title page 404s and pulled
    0 sections (fixed by the title-page fallback in pull_text.collect_section_targets);
  * refresh's per-chapter attribution prefix-matched section urls to the chapter url,
    which flat sections never satisfy, so every multi-chapter NJ cell was falsely held.

So the grammar lives here once. A `key` is `(title_number, chapter_token)` with the
token **lower-cased** (url form) so keys derived from a url, a section url, or an
upper-case citation ("45:5A-1") all compare equal.

CAVEAT for callers of `chapter_url`: the /chapter-token/ url is a *convention we build*,
not a page NJ actually publishes. It resolves only because Justia usually 301-redirects
it to the title page; where it doesn't it 404s. Any fetch of one must fall back to the
title page (see pull_text.collect_section_targets / title_url_from_chapter_url).
"""

from __future__ import annotations

import re

Key = tuple[str, str]  # (title_number, chapter_token) — token lower-cased

_CHAPTER_URL_RE = re.compile(r"/title-([^/]+)/chapter-([^/]+?)/?$", re.I)
# A flat section url repeats the title number in the slug (…/title-45/section-45-5a-1/);
# the backreference keeps the two in agreement.
_SECTION_URL_RE = re.compile(r"/title-(\d+)/section-\1-([0-9a-z]+)-", re.I)
_CITATION_RE = re.compile(r"(\d+):([0-9A-Za-z]+?)-")  # "45:5A-1" -> ("45", "5A")
_TITLE_URL_RE = re.compile(
    r"^(?P<title_url>https?://[^/]+/.+/title-[^/]+/)chapter-[^/]+/?$", re.I)

_CHAPTER_URL_TMPL = "https://law.justia.com/codes/new-jersey/title-{title}/chapter-{token}/"


def key_from_chapter_url(url: str) -> Key | None:
    """(title, token) for a …/title-N/chapter-TOKEN/ url, else None."""
    m = _CHAPTER_URL_RE.search(url or "")
    return (m.group(1), m.group(2).lower()) if m else None


def key_from_section_url(url: str) -> Key | None:
    """(title, token) for a flat section url …/title-N/section-N-TOKEN-…, else None."""
    m = _SECTION_URL_RE.search(url or "")
    return (m.group(1), m.group(2).lower()) if m else None


def key_from_citation(citation: str) -> Key | None:
    """(title, token) for a citation like '45:5A-1', else None."""
    m = _CITATION_RE.match(citation or "")
    return (m.group(1), m.group(2).lower()) if m else None


def chapter_url(key: Key) -> str:
    """The conventional chapter url for a key. See the module caveat: NJ has no chapter
    pages, so this url may 301 to the title page or 404 — fetchers must handle both."""
    title, token = key
    return _CHAPTER_URL_TMPL.format(title=title, token=token)


def section_slug_re(key: Key) -> "re.Pattern[str]":
    """Match the slug of a flat section belonging to `key`: section-<title>-<token>-…
    The trailing [-_.] keeps chapter 8 from also matching chapter 8a's sections."""
    title, token = key
    return re.compile(
        rf"^(section|§|s)[-_]?{re.escape(title)}[-_]{re.escape(token)}[-_.]", re.I)


def title_url_from_chapter_url(url: str) -> str | None:
    """The parent title url of a …/title-N/chapter-TOKEN/ url, else None — where a
    section walk goes when the built chapter url itself won't fetch."""
    m = _TITLE_URL_RE.match((url or "").strip())
    return m.group("title_url") if m else None
