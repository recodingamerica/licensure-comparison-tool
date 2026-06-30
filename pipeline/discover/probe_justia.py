"""Reusable CDP Justia structure prober (#53).

Encodes the LLM-free "poke around Justia by hand" technique we kept re-inlining: attach
to the hand-started Chrome (CDP), navigate a code page, and read its structure or text.
This is how you find chapters the keyword matcher / llm_map can't see — number-labeled
articles (MI Occ Code Art 20 = Architects), combined chapters, or acts buried in a
container — by READING the labels/text instead of guessing.

Lessons baked in:
- Connect with suppress_origin=True (the CDP origin guard 403s the websocket otherwise).
- Read CHAPTER/section LABELS, not just keyword-filtered links — the right article is
  often number-labeled ("Article 20"), so confirm by reading its text (--text).
- Some states are YEAR-PREFIXED on Justia (NH: /codes/new-hampshire/2025/title-xxx/...).
  If a bare path looks empty, `--links` the state root to learn its URL shape first.
- ONE shared Chrome: do NOT run this while a pull_text/pull_all harvest is going — the
  navigations collide and you get empty results. Run it when the grind is paused.

Usage:
  python -m pipeline.discover.probe_justia --url https://law.justia.com/codes/michigan/chapter-339/act-299-of-1980/ --links
  python -m pipeline.discover.probe_justia --url <chapter-url> --match 'architect|electric|plumb'
  python -m pipeline.discover.probe_justia --url <article-url>  --text     # confirm what an article actually is
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request

CDP = os.environ.get("JUSTIA_CDP_URL", "http://localhost:9222")


def _connect():
    try:
        import websocket  # websocket-client
    except ImportError:
        sys.exit("pip install websocket-client (in the project venv)")
    tabs = json.load(urllib.request.urlopen(f"{CDP}/json", timeout=4))
    page = next((t for t in tabs if t.get("type") == "page"), None)
    if not page:
        sys.exit(f"no page tab on {CDP} — start Chrome with --remote-debugging-port and open Justia once")
    # suppress_origin: the CDP guard 403s a websocket that sends an Origin header.
    ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=15, suppress_origin=True)
    return ws


def _cmd(ws, method, params=None, _id=[0]):
    _id[0] += 1
    ws.send(json.dumps({"id": _id[0], "method": method, "params": params or {}}))
    while True:
        m = json.loads(ws.recv())
        if m.get("id") == _id[0]:
            return m


def _eval(ws, expr: str):
    r = _cmd(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True})
    return (r.get("result", {}).get("result", {}) or {}).get("value")


def navigate(ws, url: str, settle: float = 4.0):
    _cmd(ws, "Page.enable"); _cmd(ws, "Runtime.enable")
    _cmd(ws, "Page.navigate", {"url": url})
    time.sleep(settle)
    title = _eval(ws, "document.title") or ""
    if re.search(r"just a moment|attention required|access denied", title, re.I):
        print(f"  ⚠ Cloudflare challenge on {url} — solve it in the Chrome window, then re-run")
    return title


def links(ws, match: str | None = None, n: int = 30) -> list[tuple[str, str]]:
    """(label, code-relative-href) for anchor links, optionally filtered by regex on label."""
    js = ("Array.from(document.querySelectorAll('a'))"
          ".map(a=>[a.textContent.trim(), a.href])"
          ".filter(p=>p[0].length>4 && /\\/codes\\//.test(p[1]))")
    if match:
        js += f".filter(p=>new RegExp({json.dumps(match)},'i').test(p[0]))"
    js += f".slice(0,{n})"
    rows = _eval(ws, "JSON.stringify(" + js + ")") or "[]"
    out = []
    for label, href in json.loads(rows):
        out.append((label[:70], href.split("/codes/")[-1] if "/codes/" in href else href))
    return out


def text_head(ws, chars: int = 400) -> str:
    return (_eval(ws, "(document.body.innerText||'')") or "")[:chars]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--match", help="regex to filter link labels (case-insensitive)")
    ap.add_argument("--links", action="store_true", help="dump structure links (default)")
    ap.add_argument("--text", action="store_true", help="dump the page's text head (confirm what a chapter/article is)")
    ap.add_argument("-n", type=int, default=30)
    args = ap.parse_args()

    ws = _connect()
    try:
        title = navigate(ws, args.url)
        print(f"TITLE: {title[:70]}")
        if args.text:
            print(text_head(ws))
        else:
            for label, href in links(ws, args.match, args.n):
                print(f"  {label}  ::  {href}")
    finally:
        ws.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
