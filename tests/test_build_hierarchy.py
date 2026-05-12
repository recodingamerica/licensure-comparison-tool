"""Tests for pipeline.discover.build_hierarchy pure functions.

The year-versioned auto-redirect is what got KY/NV/OR/WI working without
per-state overrides; lock in the regex behavior so a Justia layout shift
doesn't silently regress those states.
"""

from pipeline.discover.build_hierarchy import _maybe_redirect_year_versioned


def test_redirect_picks_latest_year():
    html = """
    <a href="/codes/kentucky/2024/">2024 Kentucky Statutes</a>
    <a href="/codes/kentucky/2023/">2023 Kentucky Statutes</a>
    <a href="/codes/kentucky/2025/">2025 Kentucky Statutes</a>
    """
    out = _maybe_redirect_year_versioned("https://law.justia.com/codes/kentucky/", html)
    assert out == "https://law.justia.com/codes/kentucky/2025/"


def test_no_year_links_returns_none():
    html = '<a href="/codes/california/code-bpc/">Business and Professions Code</a>'
    assert _maybe_redirect_year_versioned("https://law.justia.com/codes/california/", html) is None


def test_single_year_link():
    html = '<a href="/codes/nevada/2025/">2025 Nevada Statutes</a>'
    out = _maybe_redirect_year_versioned("https://law.justia.com/codes/nevada/", html)
    assert out == "https://law.justia.com/codes/nevada/2025/"


def test_trailing_slash_handling():
    """Caller may pass URL with or without trailing slash — output is normalized."""
    html = '<a href="/codes/oregon/2024/">2024</a>'
    a = _maybe_redirect_year_versioned("https://law.justia.com/codes/oregon", html)
    b = _maybe_redirect_year_versioned("https://law.justia.com/codes/oregon/", html)
    assert a == b == "https://law.justia.com/codes/oregon/2024/"
