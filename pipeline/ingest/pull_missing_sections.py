"""Fetch the individual sections our quotes cite but our corpora don't contain.

The alternative is re-pulling whole chapters, which is both wasteful and dangerous: IL's
"umbrella" chapter is *Chapter 225 - PROFESSIONS, OCCUPATIONS, AND BUSINESS OPERATIONS*,
i.e. the entire professions title, so re-pulling it to recover a handful of sections
would drag thousands of unrelated sections into every Illinois profession's context.

We already know exactly which sections we want: any citation an extracted quote points at
that isn't among the sections shipped with that row. This fetches those and nothing else.

SELF-VERIFYING. A section URL is derived by analogy with a sibling (OK's `328.3` lives at
.../section-59-328-3/, so `328.11` should be at .../section-59-328-11/), which is a GUESS
-- reconstructing known URLs this way succeeds ~87% of the time, and the misses are real
(Alaska splits one chapter across article-1/, article-2/, ... so a sibling's path can name
the wrong article). So a fetch is kept ONLY if the quote that wanted it actually appears
in the returned text. A wrong guess costs one fetch and is discarded; it can never enter a
corpus. Several siblings are tried per target, which is what covers the Alaska shape.

Usage:
  python -m pipeline.ingest.pull_missing_sections --dry-run          # what would be fetched
  python -m pipeline.ingest.pull_missing_sections --limit 50         # fetch and write
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
from collections import defaultdict
from pathlib import Path

from pipeline.extract.locate_quote import locate_quote_in_section
from pipeline.extract.model_helpers import iter_quote_carriers
from pipeline.ingest.pull_text import _fetch_section_text, polite_sleep
from pipeline.paths import RESULTS_DIR

log = logging.getLogger(__name__)

PUBLISHED_DIR = Path("pipeline/publish/web/public/data")
NON_PROFESSION = {
    "tag_sheet", "scope_matrices", "scope_capabilities", "states",
    "scorecard", "downloads_index", "_skiptest",
}
# Attempts per wanted section. Each is one polite Justia fetch, so this bounds the cost of
# a target whose siblings all sit under a different sub-path.
MAX_CANDIDATES = 4


def slug_token(cite: str) -> str:
    """Citation -> the token Justia uses in a slug: '328.11' -> '328-11'."""
    c = (cite or "").strip().lstrip("§ ").strip()
    c = re.sub(r"^\d+\s*§\s*", "", c)                 # ME: '32 §18302. Definitions' -> '18302. ...'
    c = re.split(r"\.\s+", c)[0]                       # drop a trailing '. Section title'
    c = c.rstrip(".").strip()
    # Comma too: KS cites 50-6,122 and Justia renders it .../section-50-6-122/.
    return re.sub(r"[.,\s]+", "-", c).lower()


def derive_url(target_cite: str, sibling_cite: str, sibling_url: str) -> str | None:
    """Swap the sibling's own token in its URL for the target's token."""
    st, tt = slug_token(sibling_cite), slug_token(target_cite)
    if not st or not tt or st == tt or len(st) < 2:
        return None
    low = sibling_url.lower()
    if st not in low:
        return None
    i = low.rindex(st)
    return sibling_url[:i] + tt + sibling_url[i + len(st):]


def wanted_sections(published_dir: Path = PUBLISHED_DIR) -> dict:
    """{(profession, state): {citation: {"quotes": [...], "siblings": [(cite, url), ...]}}}

    A citation is WANTED when a quote cites it and no shipped section answers to it.
    """
    want: dict = defaultdict(lambda: defaultdict(lambda: {"quotes": [], "siblings": []}))
    for f in sorted(published_dir.glob("*.json")):
        prof = f.stem
        if prof in NON_PROFESSION:
            continue
        try:
            data = json.loads(f.read_text())
        except Exception:
            continue
        rows = data if isinstance(data, list) else (data.get("rows") or [])
        if not rows or not isinstance(rows[0], dict) or "sections" not in rows[0]:
            continue
        for row in rows:
            state = row.get("state") or row.get("state_code")
            sections = row.get("sections") or []
            shipped = {(s.get("citation") or "").strip() for s in sections}
            siblings = [
                ((s.get("citation") or "").strip(), s.get("url"))
                for s in sections
                if (s.get("citation") or "").strip() and s.get("url")
                and "UMBRELLA" not in (s.get("citation") or "")
            ]
            if not siblings:
                continue
            for _, node in iter_quote_carriers(row):
                cite = (node.get("citation") or "").strip()
                target = (node.get("quote_section") or cite).strip()
                if node.get("quote_spans") and target in shipped:
                    continue
                if not cite or cite in shipped or "UMBRELLA" in cite:
                    continue
                entry = want[(prof, state)][cite]
                entry["quotes"].append(node.get("quote") or "")
                entry["siblings"] = siblings
    return want


def candidates(cite: str, siblings: list[tuple[str, str]]) -> list[str]:
    """Distinct derived URLs, in sibling order, capped at MAX_CANDIDATES."""
    out: list[str] = []
    for sib_cite, sib_url in siblings:
        url = derive_url(cite, sib_cite, sib_url)
        if url and url not in out:
            out.append(url)
            if len(out) >= MAX_CANDIDATES:
                break
    return out


def verify(text: str, quotes: list[str]) -> bool:
    """Does the fetched text actually contain one of the quotes that wanted it?"""
    return any(q and locate_quote_in_section(q, text) for q in quotes)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="report the plan, fetch nothing")
    ap.add_argument("--limit", type=int, default=0, help="stop after N successful sections")
    ap.add_argument("--states", help="comma-separated state filter")
    ap.add_argument("--published-dir", default=str(PUBLISHED_DIR),
                    help="read the want-list from this payload dir (use a snapshot when a "
                         "publish is concurrently rewriting the live one)")
    args = ap.parse_args()

    only = {s.strip().upper() for s in (args.states or "").split(",") if s.strip()}
    want = wanted_sections(Path(args.published_dir))
    targets = [
        (prof, state, cite, entry)
        for (prof, state), cites in sorted(want.items())
        for cite, entry in sorted(cites.items())
        if not only or state in only
    ]
    n_quotes = sum(len(e["quotes"]) for *_, e in targets)
    print(f"wanted sections: {len(targets):,}   quotes they would recover: {n_quotes:,}")
    if args.dry_run:
        for prof, state, cite, entry in targets[:25]:
            cands = candidates(cite, entry["siblings"])
            print(f"  {prof}/{state} {cite!r} ({len(entry['quotes'])} quotes) -> "
                  f"{cands[0] if cands else 'NO CANDIDATE'}")
        return

    added: dict[tuple[str, str], list[dict]] = defaultdict(list)
    ok = miss = 0
    for prof, state, cite, entry in targets:
        got = None
        for url in candidates(cite, entry["siblings"]):
            text, err = _fetch_section_text(url)
            polite_sleep()
            if err or not text:
                continue
            if verify(text, entry["quotes"]):
                got = {"url": url, "citation": cite, "label": "", "text": text}
                break
        if got:
            ok += 1
            added[(prof, state)].append(got)
            log.info("  OK   %s/%s %s -> %s", prof, state, cite, got["url"])
        else:
            miss += 1
            log.info("  MISS %s/%s %s (no candidate contained the quote)", prof, state, cite)
        if args.limit and ok >= args.limit:
            break

    for (prof, state), secs in added.items():
        path = RESULTS_DIR / "text" / prof / f"{state}.json"
        if not path.exists():
            log.warning("  no corpus at %s — skipping %d section(s)", path, len(secs))
            continue
        data = json.loads(path.read_text())
        existing = data.get("sections") if isinstance(data, dict) else data
        have = {(s.get("url") or "").rstrip("/") for s in existing}
        fresh = [s for s in secs if (s["url"] or "").rstrip("/") not in have]
        existing.extend(fresh)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        os.replace(tmp, path)
        log.info("%s/%s: +%d section(s) -> %d total", prof, state, len(fresh), len(existing))

    print(f"\nverified and added: {ok}   unresolved: {miss}")
    print("NEXT: re-run clean -> trim for the touched cells, then publish "
          "(build_frontend ships row.sections from trimmed/, not text/).")


if __name__ == "__main__":
    main()
