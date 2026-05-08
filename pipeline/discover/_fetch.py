"""Polite fetch helpers shared by every discover/* script.

Strategies, in fallback order: requests → curl_cffi → playwright. Most Justia
pages need curl_cffi (Cloudflare), some state official sites need playwright
(JS-rendered indexes).
"""

from __future__ import annotations

import logging
from typing import Tuple

import requests

try:
    from curl_cffi import requests as cffi_requests  # type: ignore
    HAVE_CFFI = True
except ImportError:
    HAVE_CFFI = False

try:
    from playwright.sync_api import sync_playwright  # type: ignore
    HAVE_PW = True
except ImportError:
    HAVE_PW = False


log = logging.getLogger("discover._fetch")

UA_BOT = "scrape-probe/1.0 (+research; contact: abigail.haddad@gmail.com)"
UA_BROWSER = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
TIMEOUT = 25


def fetch_with(strategy: str, url: str) -> Tuple[int | None, str | None, str | None]:
    """Try `strategy`; on non-2xx fall back through requests → curl_cffi → playwright.
    Returns (status, html_text, error). Caller is responsible for sleeping
    between fetches (PER_HOST_DELAY)."""
    def _try(strat: str):
        try:
            if strat == "requests":
                r = requests.get(url, headers={"User-Agent": UA_BROWSER}, timeout=TIMEOUT, allow_redirects=True)
                return r.status_code, r.text, None
            if strat == "curl_cffi":
                if not HAVE_CFFI:
                    return None, None, "curl_cffi not installed"
                r = cffi_requests.get(url, impersonate="chrome", timeout=TIMEOUT, allow_redirects=True)
                return r.status_code, r.text, None
            if strat == "playwright":
                return fetch_playwright(url)
            return None, None, f"unknown strategy: {strat}"
        except Exception as e:
            return None, None, f"{type(e).__name__}: {e}"

    status, html, err = _try(strategy)
    if status and 200 <= status < 300:
        return status, html, err
    if strategy == "requests" and HAVE_CFFI:
        s2, h2, e2 = _try("curl_cffi")
        if s2 and 200 <= s2 < 300:
            return s2, h2, e2
    if strategy in ("requests", "curl_cffi") and HAVE_PW:
        s3, h3, e3 = _try("playwright")
        if s3 and 200 <= s3 < 300:
            return s3, h3, e3
    return status, html, err


_PW = {"playwright": None, "browser": None, "context": None}


def _ensure_pw():
    if _PW["context"] is None:
        _PW["playwright"] = sync_playwright().start()
        _PW["browser"] = _PW["playwright"].chromium.launch(headless=True)
        _PW["context"] = _PW["browser"].new_context(user_agent=UA_BROWSER)
    return _PW["context"]


def shutdown_pw() -> None:
    try:
        if _PW["context"]: _PW["context"].close()
        if _PW["browser"]: _PW["browser"].close()
        if _PW["playwright"]: _PW["playwright"].stop()
    except Exception:
        pass


def fetch_playwright(url: str) -> Tuple[int | None, str | None, str | None]:
    if not HAVE_PW:
        return None, None, "playwright not installed"
    try:
        ctx = _ensure_pw()
        page = ctx.new_page()
        try:
            response = page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        except Exception as e:
            page.close()
            return None, None, f"goto failed: {e}"
        try:
            page.wait_for_load_state("networkidle", timeout=10_000)
        except Exception:
            pass
        status = response.status if response else None
        html = page.content()
        page.close()
        return status, html, None
    except Exception as e:
        return None, None, f"{type(e).__name__}: {e}"
