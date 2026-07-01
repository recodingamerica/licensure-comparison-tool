"""Survey all 50 states' umbrella_text + umbrella_chapters to answer:
'How many distinct citation styles, anchor-section formats, and upstream
discover-step gaps exist across states?' — the questions blocking a sweep
to states beyond UT/FL/CO.

We don't try to scope anything — that needs per-state rules. We just count
pattern occurrences (universal phrasings, trigger phrases, citation forms,
department-scoping language) in each state's anchor sections and emit a
one-line-per-state table.

Run as:
  python -m pipeline.discover.survey_umbrella_states
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict

from pipeline.paths import RESULTS_DIR, PROFESSION_INDEX_DIR

UMBRELLA_TEXT_DIR = RESULTS_DIR / "umbrella_text"
UMBRELLA_CHAPTERS_DIR = RESULTS_DIR / "umbrella_chapters"
OUT_PATH = RESULTS_DIR / "umbrella_scope" / "_survey.csv"

# Anchor detection: any section whose label suggests it declares scope.
ANCHOR_LABEL_RE = re.compile(
    r"(applicability|definitions|short title|"
    r"scope\s+of\s+(?:chapter|part|article|title)|"
    r"\bscope$)",
    re.I,
)

# Universal-phrase variants we know about across states.
UNIVERSAL_PHRASE_PATTERNS = {
    "this_title_applies": re.compile(r"this\s+title\s+applies\b", re.I),
    "applies_to_every_article": re.compile(r"applies\s+to\s+every\s+article\b", re.I),
    "applies_to_every_chapter": re.compile(r"applies\s+to\s+every\s+chapter\b", re.I),
    "applies_to_any_regulation": re.compile(r"applies\s+to\s+(?:any|every)\s+regulation\b", re.I),
    "applies_only_to_regulation": re.compile(r"applies\s+only\s+to\s+the\s+regulation\b", re.I),
    "applies_to_articles_N_to_M": re.compile(r"applies\s+to\s+articles?\s+\d+\s+to\s+\d+", re.I),
    "as_used_in_this_title": re.compile(r"as\s+used\s+in\s+this\s+title\b", re.I),
    "as_used_in_this_chapter": re.compile(r"as\s+used\s+in\s+this\s+chapter\b", re.I),
    "as_used_in_this_part": re.compile(r"as\s+used\s+in\s+this\s+part\b", re.I),
    "any_holder_of_a_license": re.compile(r"any\s+holder\s+of\s+a\s+license\b", re.I),
}

# Trigger phrases that introduce a practice-act enumeration.
TRIGGER_PATTERNS = {
    "licensed_under": re.compile(r"licensed\s+under\b", re.I),
    "licensed_to_practice": re.compile(r"licensed\s+to\s+practice\b", re.I),
    "licensed_pursuant_to": re.compile(r"licensed\s+pursuant\s+to\b", re.I),
    "licensed_as": re.compile(r"licensed\s+as\b", re.I),
    "regulated_by_a_part_or_article": re.compile(r"regulated\s+by\s+a\s+part\s+or\s+article\b", re.I),
}

# Citation forms we've seen.
CITATION_PATTERNS = {
    "Title_N_Chapter_X": re.compile(r"\bTitle\s+\d+,?\s+Chapter\s+\w+\b", re.I),
    "Chapter_X_capital": re.compile(r"\bChapter\s+\d+[a-z]?\b"),  # case-sensitive: UT/UT-like
    "chapter_X_lowercase": re.compile(r"\bchapter\s+\d+[a-z]?\b"),  # FL-style bare
    "article_X": re.compile(r"\barticle\s+\d+\b", re.I),
    "section_N_dash_M": re.compile(r"\b\d+-\d+-\d+\b"),  # CO-style: 12-200-103
    "section_N_dot_M": re.compile(r"\b\d+\.\d+\b"),  # FL-style: 456.001
    "spelled_out_numbers": re.compile(
        r"\b(?:chapter|section|article)\s+(?:one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|"
        r"thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred)\b",
        re.I,
    ),
}

# Department-scoping language — flags states likely to have multi-department
# (FL-style Ch 455) issues.
DEPT_PHRASE_PATTERNS = {
    "by_the_department": re.compile(r"by\s+the\s+department\b", re.I),
    "department_of_health": re.compile(r"department\s+of\s+health\b", re.I),
    "department_of_state": re.compile(r"department\s+of\s+state\b", re.I),
    "division_of": re.compile(r"division\s+of\s+\w+", re.I),
}


def survey_state(state: str) -> dict:
    text_path = UMBRELLA_TEXT_DIR / f"{state}.json"
    if not text_path.exists():
        return {"state": state, "missing_umbrella_text": True}

    raw = json.loads(text_path.read_text())
    all_sections = raw.get("sections", [])
    sections = [s for s in all_sections if "/section-" in s.get("url", "")]

    if not sections:
        return {
            "state": state,
            "total_sections_raw": len(all_sections),
            "real_sections": 0,
            "issue": "no_section_urls",
        }

    chap_counter = Counter(s.get("umbrella_chapter_slug", "?") for s in sections)
    anchors = [s for s in sections if ANCHOR_LABEL_RE.search(s.get("label", ""))]

    # Group anchors by chapter to detect "sections-as-chapters" (every chapter
    # has exactly 1 section — the discover step caught sections not chapters).
    sections_per_chapter = list(chap_counter.values())
    sections_as_chapters = (
        len(chap_counter) > 5 and max(sections_per_chapter) == 1
    )

    anchor_text = "\n\n".join(s.get("text", "") for s in anchors)

    univ_hits = {name: bool(p.search(anchor_text)) for name, p in UNIVERSAL_PHRASE_PATTERNS.items()}
    trig_hits = {name: bool(p.search(anchor_text)) for name, p in TRIGGER_PATTERNS.items()}
    cite_counts = {name: len(p.findall(anchor_text)) for name, p in CITATION_PATTERNS.items()}
    dept_hits = {name: bool(p.search(anchor_text)) for name, p in DEPT_PHRASE_PATTERNS.items()}

    titles_in_urls = Counter()
    title_re = re.compile(r"/title-(\d+)/", re.I)
    for s in sections:
        m = title_re.search(s.get("url", ""))
        if m:
            titles_in_urls[m.group(1)] += 1

    return {
        "state": state,
        "real_sections": len(sections),
        "chapters": len(chap_counter),
        "anchors": len(anchors),
        "titles": ",".join(f"t{t}({n})" for t, n in titles_in_urls.most_common()),
        "sections_as_chapters": sections_as_chapters,
        # Universal phrase signals (truthy → at least one anchor uses it)
        **{f"u_{k}": v for k, v in univ_hits.items()},
        # Trigger phrase signals
        **{f"t_{k}": v for k, v in trig_hits.items()},
        # Citation pattern counts (raw count in anchor text)
        **{f"c_{k}": v for k, v in cite_counts.items()},
        # Department-scoping language
        **{f"d_{k}": v for k, v in dept_hits.items()},
    }


def classify(row: dict) -> str:
    """One-line summary judgment of where the state sits, for the human reading."""
    if row.get("missing_umbrella_text"):
        return "MISSING_UMBRELLA_TEXT"
    if row.get("issue") == "no_section_urls":
        return f"NO_SECTION_URLS ({row.get('total_sections_raw',0)} raw entries)"
    if row.get("real_sections", 0) == 0:
        return "EMPTY"
    if row.get("sections_as_chapters"):
        return "SECTIONS_AS_CHAPTERS"
    if row.get("anchors", 0) == 0:
        return "NO_ANCHORS_DETECTED"

    # Try to match a known style
    notes = []
    if row.get("c_Title_N_Chapter_X", 0) >= 3:
        notes.append("UT-style (Title-N Chapter X)")
    if row.get("c_chapter_X_lowercase", 0) >= 3 and not row.get("c_Title_N_Chapter_X", 0) >= 3:
        notes.append("FL-style (bare chapter N)")
    if row.get("c_article_X", 0) >= 3:
        notes.append("CO-style (article N)")
    if row.get("u_applies_to_articles_N_to_M"):
        notes.append("range scope")
    if row.get("c_spelled_out_numbers", 0) > 0:
        notes.append("MA-style spelled numbers")

    has_universal = any(row.get(f"u_{k}") for k in ["this_title_applies","applies_to_every_article","applies_to_every_chapter","applies_to_any_regulation","applies_only_to_regulation","as_used_in_this_title","as_used_in_this_chapter","any_holder_of_a_license"])
    has_trigger = any(row.get(f"t_{k}") for k in TRIGGER_PATTERNS)

    if not notes and not has_universal and not has_trigger:
        return f"NO_RECOGNIZED_PATTERNS (sections={row['real_sections']}, anchors={row['anchors']})"

    if has_universal:
        notes.append("has_universal")
    if has_trigger:
        notes.append("has_trigger")
    return "; ".join(notes) if notes else "UNCLEAR"


def main():
    from pipeline.config.states import ALL_STATES
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    rows = [survey_state(st) for st in ALL_STATES]
    classified = [(r["state"], classify(r), r) for r in rows]

    # Console summary
    by_class = defaultdict(list)
    for st, cls, _r in classified:
        by_class[cls].append(st)
    print(f"\n=== {len(rows)} states surveyed ===\n")
    for cls, states in sorted(by_class.items(), key=lambda kv: -len(kv[1])):
        print(f"[{len(states):2d}] {cls}")
        print(f"      {', '.join(states)}")
        print()

    # CSV with all the boolean/count detail
    fields = ["state", "classification"]
    sample = {k for r in rows for k in r.keys()}
    fields += sorted(sample - {"state"})
    with OUT_PATH.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for st, cls, r in classified:
            row = {"state": st, "classification": cls, **r}
            w.writerow(row)
    print(f"detail CSV: {OUT_PATH}")


if __name__ == "__main__":
    main()
