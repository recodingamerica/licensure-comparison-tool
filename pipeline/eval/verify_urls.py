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

Usage:
  python -m pipeline.eval.verify_urls --url URL [URL ...] [--debug]
  python -m pipeline.eval.verify_urls --profession medicine --state MN
  python -m pipeline.eval.verify_urls --profession medicine          # all states
  python -m pipeline.eval.verify_urls --sample [--only-bad]          # 1 url / (prof,state)

Reads the frozen profession_index for the mapping source of truth. Fetches
through pipeline.ingest.pull_text.fetch (Justia -> CDP browser, official ->
curl_cffi), so a Justia run needs JUSTIA_CDP_URL pointed at a cleared debug
Chrome, and must not overlap a pull (one scraper per Chrome).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse

from pipeline.ingest.pull_text import fetch, extract_child_links
from pipeline.paths import PROFESSION_INDEX_DIR

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


# ---------------------------------------------------------------------------
# Worklist assembly from the frozen index
# ---------------------------------------------------------------------------
def _index_urls(profession: str, state: str | None) -> list[tuple[str, str, str]]:
    """(profession, state, url) for each mapped chapter node. One url per node
    (the chapter url); that's the leaf-verify target."""
    path = PROFESSION_INDEX_DIR / f"{profession}.json"
    if not path.exists():
        return []
    idx = json.loads(path.read_text())
    out = []
    for st, blk in idx.get("by_state", {}).items():
        if state and st != state:
            continue
        for node in blk.get("matched", []):
            u = node.get("url", "")
            if u:
                out.append((profession, st, u))
    return out


def _all_professions() -> list[str]:
    return sorted(p.stem for p in PROFESSION_INDEX_DIR.glob("*.json")
                  if not p.stem.startswith("_"))


def _emit(rec: dict, prof: str | None = None, state: str | None = None, debug: bool = False) -> None:
    tag = f"{prof}/{state}  " if prof else ""
    line = f"  {rec['verdict']:9s} {tag}{rec['url']}"
    print(line)
    if debug or rec["verdict"] != "LIVE":
        det = {k: rec.get(k) for k in ("status", "title", "n_child", "body_chars", "detail")
               if rec.get(k) is not None}
        print(f"            {det}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", nargs="+", help="probe explicit URL(s)")
    ap.add_argument("--profession", help="probe the mapped urls for this profession")
    ap.add_argument("--state", help="restrict --profession to one state")
    ap.add_argument("--sample", action="store_true",
                    help="probe one url per (profession,state) across the whole index")
    ap.add_argument("--only-bad", action="store_true", help="print only non-LIVE verdicts")
    ap.add_argument("--debug", action="store_true", help="print raw signals for every url")
    args = ap.parse_args()

    targets: list[tuple[str | None, str | None, str]] = []
    if args.url:
        targets = [(None, None, u) for u in args.url]
    elif args.sample:
        for prof in _all_professions():
            targets += _index_urls(prof, None)
    elif args.profession:
        targets = _index_urls(args.profession, args.state)
    else:
        ap.error("give --url, --profession, or --sample")

    counts: dict[str, int] = {}
    bad: list[dict] = []
    for prof, state, url in targets:
        rec = probe(url)
        counts[rec["verdict"]] = counts.get(rec["verdict"], 0) + 1
        if rec["verdict"] != "LIVE":
            bad.append({**rec, "profession": prof, "state": state})
        if not args.only_bad or rec["verdict"] != "LIVE":
            _emit(rec, prof, state, args.debug)

    print("\n=== summary ===")
    for v in ("LIVE", "STUB", "DEAD_404", "CHALLENGE", "ERROR"):
        if counts.get(v):
            print(f"  {v:9s} {counts[v]}")
    # Non-zero exit if any URL needs a human to find a new link.
    sys.exit(1 if (counts.get("STUB") or counts.get("DEAD_404")) else 0)


if __name__ == "__main__":
    main()
