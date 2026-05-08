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
JUSTIA_LONELY_NAV_LINE = re.compile(r"^\s*(?:Previous|Next|View All Versions|Learn more)\s*$", re.IGNORECASE | re.MULTILINE)
JUSTIA_YEAR_VERSION_LINE = re.compile(r"^\s*\d{4}\s+[A-Za-z][\w\s\-\(\)\.,]*\bCode\b.*$", re.MULTILINE)


def clean_justia(text: str) -> str:
    if not text:
        return ""
    t = text
    t = JUSTIA_VERSION_NAV.sub("", t)
    t = JUSTIA_DISCLAIMER_TAIL.sub("", t)
    t = JUSTIA_PUBLIC_SERVICE_TAIL.sub("", t)
    t = JUSTIA_LONELY_NAV_LINE.sub("", t)
    t = JUSTIA_YEAR_VERSION_LINE.sub("", t)
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


# Source dispatch: URL host substring → cleaner function.
# Add an entry here when a new source layout shows up (e.g., leginfo.legislature.ca.gov).
SOURCE_CLEANERS: dict[str, Callable[[str], str]] = {
    "law.justia.com": clean_justia,
}


def cleaner_for(url: str) -> Callable[[str], str]:
    host = urllib.parse.urlparse(url).netloc.lower()
    for source_host, fn in SOURCE_CLEANERS.items():
        if source_host in host:
            return fn
    return clean_generic

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


def should_drop(label: str, text: str) -> str | None:
    """Return drop reason or None to keep."""
    if DROP_LABEL_TOKENS.search(label or ""):
        return "label_marked_inactive"
    if not text:
        return "empty_body"
    if len(text) < DROP_BODY_MAX_CHARS and DROP_TEXT_MARKER.search(text):
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
        cleaned = cleaner(sec.get("text", ""))
        reason = should_drop(sec.get("label", ""), cleaned)
        if reason:
            out.dropped.append({"url": sec["url"], "label": sec["label"], "reason": reason})
            continue
        out.sections.append(CleanSection(
            url=sec["url"],
            label=sec["label"],
            citation=sec.get("citation", ""),
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

    summary = []
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
        summary.append({
            "state": state,
            "kept": len(corpus.sections),
            "dropped": len(corpus.dropped),
            "chars": corpus.total_chars,
        })
    (out_dir / "_summary.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
