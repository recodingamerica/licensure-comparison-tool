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

from pipeline.paths import TEXT_DIR, CLEAN_DIR, LOGS_DIR, CONFIG_DIR
from pipeline import provenance
from pipeline._records import record_files, write_json_atomic
from pipeline._runlog import record_run
from pipeline.config.loaders import load_professions, load_corpus_overrides


def corpus_profession_for(profession: str) -> str:
    """The profession whose harvested text/<X>/ this profession reads. Normally
    itself; for a NESTED occupation declared with `parent_corpus: <parent>` in
    professions.yaml it's the parent — so e.g. dental_hygienist extracts from the
    already-harvested dentistry corpus with NO new Justia pull. The whole point of
    the nested-occupation path (see docs/runbooks/automation_handoff_assessment.md)."""
    try:
        conf = load_professions()
        return (conf.get(profession, {}) or {}).get("parent_corpus") or profession
    except (OSError, Exception):
        return profession


def corpus_from_overrides(profession: str) -> dict[str, str]:
    """Per-(state, profession) corpus reuse (#53 sibling cross-ref). config/
    corpus_overrides.yaml (shape `{profession: {STATE: sibling_profession}}`) records
    that a state's text for `profession` already lives in a sibling's harvested corpus
    — a combined or contractor chapter that governs several trades (e.g. TN Title 62
    Ch.6 covers HVAC + electrician + plumber). Written by discover.cross_ref_siblings
    so a missing trade self-heals from a sibling pull instead of logging a false gap.
    Unlike profession-wide parent_corpus this is PER-STATE, so a profession can own its
    corpus in 41 states and borrow a sibling's in the other 9. Returns {STATE: sibling}."""
    # load_corpus_overrides(profession) preserves the exact error semantics:
    # FileNotFoundError → {}, malformed → RuntimeError("corpus_overrides.yaml unreadable: …")
    return load_corpus_overrides(profession=profession)

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
    # "Previous" on year-versioned pages (KY), "Other" on Colorado's — both a
    # year-list nav block ending in "View All Versions".
    r"Go to (?:Previous|Other) Versions[\s\S]*?View All Versions",
    re.IGNORECASE,
)
# Justia's annotation apparatus — case-law ANNOTATIONS, "Research References &
# Practice Aids", the "Hierarchy Notes:" breadcrumb, "State Notes" — is editorial
# furniture, not statute. Colorado's and New Mexico's Justia section pages append a
# big block of it AFTER the operative text (and its "Source:/Laws …" history line,
# which precedes the block and is kept). Truncate from the first apparatus header to
# the end. Found 2026-07-18 when re-pulling Colorado injected this block into the raw
# corpus and it reached extraction (clean_text had no pattern for it). The markers
# are title-case or all-caps on their own line, so this won't fire on lowercase prose.
JUSTIA_ANNOTATION_APPARATUS = re.compile(
    r"\n(?:Annotations?|ANNOTATIONS?|Research References & Practice Aids|Hierarchy Notes:)"
    r"[\s\S]*$"
)
JUSTIA_DISCLAIMER_TAIL = re.compile(
    r"Disclaimer:\s*These codes may not be the most recent[\s\S]*?(?=\Z)",
    re.IGNORECASE,
)
JUSTIA_PUBLIC_SERVICE_TAIL = re.compile(
    r"\b[\w\-\.\s]*Code section information is provided by Justia[\s\S]*?(?=\Z)",
    re.IGNORECASE,
)
JUSTIA_LONELY_NAV_LINE = re.compile(r"^\s*(?:Previous|Next|View All Versions|View Our Newest Version Here|Learn more|Download as PDF)\s*$", re.IGNORECASE | re.MULTILINE)
# "2022 Colorado Code", "2025 Colorado Rev. Stat." — a year-stamped source label line.
JUSTIA_YEAR_VERSION_LINE = re.compile(r"^\s*\d{4}\s+[A-Za-z][\w\s\-\(\)\.,]*\b(?:Code|Statutes?|Rev\. ?Stat\.?)\b.*$", re.MULTILINE)
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
    t = JUSTIA_ANNOTATION_APPARATUS.sub("", t)
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


# A Justia CONTAINER page (chapter/title/article/...) served as if it were a section.
# Its body is the version-selector chrome plus a table of contents -- navigation, never
# statute. 62 such rows survive across 33 committed cells, and two cells consisted of
# nothing else until their mappings were fixed.
#
# The URL is load-bearing here. The same "Go to Previous Versions" chrome sits ABOVE the
# real statute on every KY and OR SECTION page (they are year-versioned), so matching on
# the marker alone flags ~14,000 perfectly good sections. Only a container URL carrying
# that chrome is an index page.
_CONTAINER_URL = re.compile(
    r"/(chapter|title|article|subchapter|sub-art|part|division|act)[^/]*/?$", re.I)
_INDEX_PAGE_MARKER = "Go to Previous Versions"


def should_drop(label: str, text: str, url: str = "") -> str | None:
    """Return drop reason or None to keep."""
    if (url and _INDEX_PAGE_MARKER in (text or "")[:400]
            and _CONTAINER_URL.search(url.rstrip("/"))):
        return "container_index_page"
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
    # Some older reused-from-sibling corpora (pipeline.discover.gap_harvest.reuse,
    # fixed 2026-07-08) were written without state/profession keys. The path itself
    # is authoritative (text/<profession>/<state>.json), so fall back to it rather
    # than fail on every one of those files.
    out = CleanCorpus(
        state=raw.get("state") or in_path.stem,
        profession=raw.get("profession") or in_path.parent.name,
        chapter_urls=raw.get("chapter_urls", []),
    )
    for sec in raw.get("sections", []):
        cleaner = cleaner_for(sec.get("url", ""))
        # Decode HTML entities before the source-specific cleaner. BeautifulSoup's
        # get_text usually handles this, but some Justia layouts (KY, ND) leak
        # raw &quot; / &#039; — those defeat the quote-verifier (the matcher
        # keeps alnum chars, so &quot; survives as the literal token "quot").
        cleaned = cleaner(html.unescape(sec.get("text", "")))
        reason = should_drop(sec.get("label", ""), cleaned, sec.get("url", ""))
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

    base_prof = corpus_profession_for(profession)
    base_dir = TEXT_DIR / base_prof
    overrides = corpus_from_overrides(profession)
    out_dir = CLEAN_DIR / profession
    out_dir.mkdir(parents=True, exist_ok=True)
    if base_prof != profession:
        log.info("[%s] nested occupation — reading parent corpus text/%s/ (no new pull)",
                 profession, base_prof)

    # Build the per-state source map: the profession's own (or parent) corpus, plus
    # any per-state corpus_from siblings (a sibling's already-pulled combined chapter).
    sources: dict[str, Path] = {}
    for path in record_files(base_dir):
        sources[path.stem.upper()] = path
    for state, sib in overrides.items():
        sp = TEXT_DIR / sib / f"{state}.json"
        if sp.exists():
            sources[state] = sp  # per-state sibling reuse wins over the base corpus
        else:
            log.warning("[%s] corpus_from=%s for %s but text/%s/%s.json not harvested",
                        profession, sib, state, sib, state)

    if not sources:
        raise SystemExit(f"no source corpus for {profession}: base dir {base_dir} empty and no corpus_from overrides")

    for state in sorted(sources):
        if only_states and state not in only_states:
            continue
        path = sources[state]
        try:
            corpus = clean_state(path)
        except Exception:
            log.exception("[%s] clean failed", state)
            continue
        out_path = out_dir / f"{state}.json"
        write_json_atomic(out_path, asdict(corpus))
        provenance.record("clean", profession, state)
        borrowed = path.parent.name if path.parent.name != base_prof else ""
        log.info(
            "[%s] kept=%d dropped=%d chars=%d%s",
            state, len(corpus.sections), len(corpus.dropped), corpus.total_chars,
            f" (corpus_from {borrowed})" if borrowed else "",
        )

    # Cumulative summary rebuilt from every cleaned corpus on disk (not just this
    # run's states), so a --states subset run can't drop other states' rows.
    summary = []
    for path in record_files(out_dir):
        d = json.loads(path.read_text())
        summary.append({
            "state": path.stem,
            "kept": len(d.get("sections") or []),
            "dropped": len(d.get("dropped") or []),
            "chars": int(d.get("total_chars") or 0),
        })
    write_json_atomic(out_dir / "_summary.json", summary)
    record_run("clean_text", profession=profession)


if __name__ == "__main__":
    main()
