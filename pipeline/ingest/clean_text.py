"""Regex-based cleanup of pulled statute text.

Source-keyed dispatch: each section's URL host picks a cleaner. Currently
only Justia is implemented; non-Justia hosts fall back to a generic cleaner.
State-specific overrides slot in by registering a new SOURCE_CLEANERS entry.

For each pulled state JSON, produces a cleaned counterpart that:
  - strips source chrome (version navigation, disclaimer, Previous/Next nav)
  - collapses runs of blank lines
  - drops sections that are repealed / reserved / expired

Inputs:  extract/results/text/<profession>/<STATE>.json
Outputs: extract/results/clean/<profession>/<STATE>.json
         extract/results/clean/<profession>/_summary.json

Usage:
  python clean_text.py --profession podiatry
"""

from __future__ import annotations

import argparse
import html
import json
import logging
import re
import urllib.parse
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import TEXT_DIR, CLEAN_DIR, LOGS_DIR  # noqa: E402

LOG_PATH = LOGS_DIR / "clean_text.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("clean_text")


# --- shared regexes ---
BLANK_LINE_RUNS = re.compile(r"\n[ \t]*\n[ \t]*(?:\n[ \t]*)+")
TRAILING_WHITESPACE = re.compile(r"[ \t]+$", re.MULTILINE)


# --- Justia-specific patterns ---
# Order matters: nav blocks first (so disclaimer doesn't catch trailing nav),
# then line-level strips, then whitespace collapse.

JUSTIA_VERSION_NAV = re.compile(
    r"Go to Previous Versions[\s\S]*?View All Versions",
    re.IGNORECASE,
)
JUSTIA_DISCLAIMER_TAIL = re.compile(
    r"Disclaimer:\s*These codes may not be the most recent[\s\S]*?(?=\Z)",
    re.IGNORECASE,
)
JUSTIA_PUBLIC_SERVICE_TAIL = re.compile(
    r"\b[\w\-\.\s]*Code section information is provided by Justia[\s\S]*?(?=\Z)",
    re.IGNORECASE,
)
JUSTIA_LONELY_NAV_LINE = re.compile(r"^\s*(?:Previous|Next|View All Versions|Learn more|Download as PDF)\s*$", re.IGNORECASE | re.MULTILINE)
JUSTIA_YEAR_VERSION_LINE = re.compile(r"^\s*\d{4}\s+[A-Za-z][\w\s\-\(\)\.,]*\b(?:Code|Statutes?)\b.*$", re.MULTILINE)
# Justia stamps a "Universal Citation" block (media-neutral cite + AALL blurb)
# onto every code section; it's site furniture, not statute text. Seen across
# all Justia states (KY, CT, ...). Strip the cite line and the boilerplate blurb.
JUSTIA_UNIVERSAL_CITATION = re.compile(
    r"Universal Citation:\s*\n?\s*[^\n]*\(\d{4}\)", re.IGNORECASE)
JUSTIA_MEDIA_NEUTRAL_BLURB = re.compile(
    r"This media-neutral citation is based[\s\S]*?official citation\.", re.IGNORECASE)
# Pagination marker on its own line, e.g. `Page No. 3`. Justia's ND
# chapter-blob renders embed these from the source PDF and they end up
# interjected between actual statute sentences, defeating verbatim quote
# matching. Only known to affect ND; harmless on other Justia pages.
JUSTIA_PAGE_NUMBER_LINE = re.compile(r"^\s*Page No\.\s*\d+\s*$", re.IGNORECASE | re.MULTILINE)


def clean_justia(text: str) -> str:
    if not text:
        return ""
    t = text
    t = JUSTIA_VERSION_NAV.sub("", t)
    t = JUSTIA_DISCLAIMER_TAIL.sub("", t)
    t = JUSTIA_PUBLIC_SERVICE_TAIL.sub("", t)
    t = JUSTIA_MEDIA_NEUTRAL_BLURB.sub("", t)
    t = JUSTIA_UNIVERSAL_CITATION.sub("", t)
    t = JUSTIA_LONELY_NAV_LINE.sub("", t)
    t = JUSTIA_YEAR_VERSION_LINE.sub("", t)
    t = JUSTIA_PAGE_NUMBER_LINE.sub("", t)
    t = TRAILING_WHITESPACE.sub("", t)
    t = BLANK_LINE_RUNS.sub("\n\n", t)
    return t.strip()


def clean_generic(text: str) -> str:
    """Fallback for unknown sources — only whitespace normalization."""
    if not text:
        return ""
    t = TRAILING_WHITESPACE.sub("", text)
    t = BLANK_LINE_RUNS.sub("\n\n", t)
    return t.strip()


# Utah le.utah.gov text comes from the chapter XML (parse_utah_chapter_xml), so
# it carries no site chrome — version nav / disclaimers / pagination never enter
# the corpus. Only whitespace normalization is needed; alias the generic cleaner
# so the source is explicitly registered (and a place exists if quirks surface).
clean_utah_le = clean_generic


# Source dispatch: URL host substring → cleaner function.
# Add an entry here when a new source layout shows up (e.g., leginfo.legislature.ca.gov).
SOURCE_CLEANERS: dict[str, Callable[[str], str]] = {
    "law.justia.com": clean_justia,
    "le.utah.gov": clean_utah_le,
}


def cleaner_for(url: str) -> Callable[[str], str]:
    host = urllib.parse.urlparse(url).netloc.lower()
    for source_host, fn in SOURCE_CLEANERS.items():
        if source_host in host:
            return fn
    return clean_generic


# MI legislature.mi.gov doesn't surface a section ID in the page HTML the way
# Justia does (Justia's page has the citation in a known element; MI just
# embeds it in body text). When pull_text leaves the citation blank for an
# MI section we can recover it from the URL: e.g. objectName=mcl-333-17011
# → "MCL 333.17011".
_MI_OBJECT_RE = re.compile(r"objectName=mcl-(\d+)-(\d+[a-z]?)", re.IGNORECASE)


def derive_citation(url: str, existing: str) -> str:
    if existing:
        return existing
    if "legislature.mi.gov" in url:
        m = _MI_OBJECT_RE.search(url)
        if m:
            return f"MCL {m.group(1)}.{m.group(2)}"
    return existing

# --- repealed / reserved / expired detection ---
# In labels: anything containing these tokens, case-insensitive.
DROP_LABEL_TOKENS = re.compile(r"\b(repealed|reserved|expired|omitted|renumbered|transferred|deleted)\b", re.IGNORECASE)

# In text body: a short body that consists primarily of a "[Repealed]" / "Section X is repealed" assertion.
# We require the body be short AND contain the marker — long bodies that merely mention "repealed" in passing pass through.
DROP_TEXT_MARKER = re.compile(
    r"\b(repealed|reserved|expired|omitted|renumbered|transferred)\b",
    re.IGNORECASE,
)
DROP_BODY_MAX_CHARS = 350  # any body shorter than this *and* containing a drop marker → drop


@dataclass
class CleanSection:
    url: str
    label: str
    citation: str
    text: str
    text_len: int


@dataclass
class CleanCorpus:
    state: str
    profession: str
    chapter_urls: list[str] = field(default_factory=list)
    sections: list[CleanSection] = field(default_factory=list)
    dropped: list[dict] = field(default_factory=list)  # {url, label, reason}
    total_chars: int = 0


# Future-effective repeal: "Repealed effective <DATE>" means the section is
# STILL ACTIVE today (the repeal kicks in later). Observed on NM CPA where
# every section in 61-28B was labeled "(Repealed effective July 1, 2030...)".
# Skip the drop when this pattern appears.
KEEP_FUTURE_REPEAL = re.compile(r"\brepealed\s+effective\b", re.IGNORECASE)


def should_drop(label: str, text: str) -> str | None:
    """Return drop reason or None to keep."""
    if not KEEP_FUTURE_REPEAL.search(label or "") and DROP_LABEL_TOKENS.search(label or ""):
        return "label_marked_inactive"
    if not text:
        return "empty_body"
    if not KEEP_FUTURE_REPEAL.search(text) and len(text) < DROP_BODY_MAX_CHARS and DROP_TEXT_MARKER.search(text):
        return "body_marked_inactive"
    if len(text) < 50:
        return "trivial_body"
    return None


def clean_state(in_path: Path) -> CleanCorpus:
    raw = json.loads(in_path.read_text())
    out = CleanCorpus(
        state=raw["state"],
        profession=raw["profession"],
        chapter_urls=raw.get("chapter_urls", []),
    )
    for sec in raw.get("sections", []):
        cleaner = cleaner_for(sec.get("url", ""))
        # Decode HTML entities before the source-specific cleaner. BeautifulSoup's
        # get_text usually handles this, but some Justia layouts (KY, ND) leak
        # raw &quot; / &#039; — those defeat the quote-verifier (the matcher
        # keeps alnum chars, so &quot; survives as the literal token "quot").
        cleaned = cleaner(html.unescape(sec.get("text", "")))
        reason = should_drop(sec.get("label", ""), cleaned)
        if reason:
            out.dropped.append({"url": sec["url"], "label": sec["label"], "reason": reason})
            continue
        out.sections.append(CleanSection(
            url=sec["url"],
            label=sec["label"],
            citation=derive_citation(sec["url"], sec.get("citation", "")),
            text=cleaned,
            text_len=len(cleaned),
        ))
        out.total_chars += len(cleaned)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True, help="Profession dir name under results/text/")
    ap.add_argument("--states", default="", help="Comma-separated subset; empty = all")
    args = ap.parse_args()

    profession = args.profession.lower()
    only_states = {s.strip().upper() for s in args.states.split(",") if s.strip()}

    in_dir = TEXT_DIR / profession
    out_dir = CLEAN_DIR / profession
    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_dir.exists():
        raise SystemExit(f"input dir not found: {in_dir}")

    for path in sorted(in_dir.glob("*.json")):
        if path.name.startswith("_"):
            continue
        state = path.stem
        if only_states and state not in only_states:
            continue
        try:
            corpus = clean_state(path)
        except Exception as e:
            log.exception("[%s] clean failed", state)
            continue
        out_path = out_dir / f"{state}.json"
        out_path.write_text(json.dumps(asdict(corpus), indent=2))
        log.info(
            "[%s] kept=%d dropped=%d chars=%d (was %d)",
            state, len(corpus.sections), len(corpus.dropped), corpus.total_chars,
            sum(s.get("text_len", len(s.get("text", ""))) for s in json.loads(path.read_text()).get("sections", [])),
        )

    # Cumulative summary rebuilt from every cleaned corpus on disk (not just this
    # run's states), so a --states subset run can't drop other states' rows.
    summary = []
    for path in sorted(out_dir.glob("*.json")):
        if path.name.startswith("_"):
            continue
        d = json.loads(path.read_text())
        summary.append({
            "state": path.stem,
            "kept": len(d.get("sections") or []),
            "dropped": len(d.get("dropped") or []),
            "chars": int(d.get("total_chars") or 0),
        })
    (out_dir / "_summary.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
