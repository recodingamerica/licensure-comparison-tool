"""Pull a state's ADMINISTRATIVE RULES as a supplementary corpus source.

The gap_loop showed that a systematic class of fields the statutes leave blank
(CE hours, CPR/BLS, pharmacology training, record retention, jurisprudence exam…)
live in the administrative RULES, not the statute. This pulls them.

Source: the official state admin-rule site. For Utah that's adminrules.utah.gov,
a JS SPA — so we render it in the SAME CDP Chrome we use for Justia and WAIT for
the SPA to load its data (the rule body is fetched async after domcontentloaded).
The whole rule renders on one page; we split it into per-section records by the
rule-number headings. Output mirrors text/: results/regulations_text/<prof>/<state>.json
with {url, label, citation, text} sections, ready to merge before clean→trim→extract.

Run (debug Chrome on :9222):
  JUSTIA_CDP_URL=http://127.0.0.1:9222 pipeline/.venv/bin/python -m pipeline.ingest.pull_regulations \
      --profession optometry --state UT \
      --url "https://adminrules.utah.gov/public/rule/R156-16a/Current%20Rules"
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ingest import pull_text as pt  # noqa: E402
from paths import RESULTS_DIR  # noqa: E402

OUT_DIR = RESULTS_DIR / "regulations_text"
# Rule-section heading, e.g. "R156-16a-304." or "R277-419-2." — the split point.
_SECTION_HEAD = re.compile(r"\b(R\d{3}[A-Za-z]?-\d+[a-z]?-\d+[a-z]?)\.")


def render_spa(url: str, *, want="continuing|hours|shall|section", min_chars=3000, max_polls=20) -> str:
    """Render a JS admin-rule SPA in the CDP Chrome and WAIT for its async body
    to load (the rule text is fetched after domcontentloaded). Returns innerText."""
    with pt._get_browser_page() as page:
        page.goto(url, timeout=90000, wait_until="domcontentloaded")
        # clear any Cloudflare challenge first (same as fetch_via_browser)
        waited = 0
        while pt._challenge_showing(page) and waited < 120:
            page.wait_for_timeout(2000); waited += 2
        txt = ""
        for _ in range(max_polls):
            page.wait_for_timeout(1500)
            txt = page.evaluate("document.body.innerText") or ""
            if len(txt) > min_chars and re.search(want, txt, re.I):
                break
        return txt


def split_sections(text: str, rule_url: str) -> list[dict]:
    """Split rendered rule text into per-section records by rule-number heading."""
    marks = list(_SECTION_HEAD.finditer(text))
    if not marks:
        return [{"url": rule_url, "label": "rule", "citation": "", "text": text.strip()}]
    out = []
    for i, m in enumerate(marks):
        start = m.start()
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        body = text[start:end].strip()
        cite = m.group(1)
        head = body.split("\n", 1)[0][:120]
        if len(body) > 40:
            out.append({"url": f"{rule_url}#{cite}", "label": head, "citation": cite, "text": body})
    # de-dupe (the SPA sometimes renders a nav copy of each heading)
    seen, uniq = set(), []
    for s in out:
        k = (s["citation"], s["text"][:80])
        if k not in seen:
            seen.add(k); uniq.append(s)
    return uniq


def pull(profession: str, state: str, url: str) -> None:
    text = render_spa(url)
    secs = split_sections(text, url)
    OUT_DIR.joinpath(profession).mkdir(parents=True, exist_ok=True)
    fp = OUT_DIR / profession / f"{state}.json"
    fp.write_text(json.dumps({"profession": profession, "state": state, "source": url,
                              "sections": secs}, indent=1))
    print(f"  {profession}/{state}: {len(secs)} rule sections, "
          f"{sum(len(s['text']) for s in secs)} chars → {fp}")
    for s in secs[:6]:
        print(f"    {s['citation']}: {s['label'][:60]}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True)
    ap.add_argument("--state", required=True)
    ap.add_argument("--url", required=True, help="official admin-rule URL (e.g. adminrules.utah.gov rule page)")
    args = ap.parse_args()
    pull(args.profession.lower(), args.state.upper(), args.url)


if __name__ == "__main__":
    main()
