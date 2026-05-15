"""Assign per-section scope to a state's umbrella sections, using the statute
text itself as evidence — no LLM, no family heuristics.

For each umbrella chapter, we identify the anchor sections (Applicability /
Definitions / Title / Scope) and read their text for two kinds of signal:
  1. A universal statement ("This chapter applies to any regulation of an
     occupation", "As used in this title", etc.) → scope = universal.
  2. An enumerated list of practice-act citations ("Licensee means an
     individual licensed... under Chapter 5a, ... Chapter 17b, ...") →
     scope = the list of professions those chapters resolve to in the
     reverse-index.

Each signal carries a *scope target* — `title`, `chapter`, or `part`. A
title-target signal scopes every section in every chapter of that title; a
chapter-target signal scopes every section in that chapter; a part-target
signal scopes only sections within the same part as the anchor.

When several signals apply, the most specific (part > chapter > title) wins.
Sections we can't deterministically scope are written with
`scope_source: "undetermined"` and listed in the triage report. We fail
loudly rather than guessing. No LLM fallbacks.

Sections whose labels suggest a narrower scope (e.g. "Tax credit --
Psychiatrists") still inherit the chapter default in this first pass —
section-level narrowing is on the deferred list — but they ARE flagged
in the triage report for human review.

Output: pipeline/results/umbrella_scope/<STATE>.json
Triage report: same file, top-level `triage` array.

Usage:
  python -m pipeline.discover.assign_umbrella_scope --state UT
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import RESULTS_DIR, LOGS_DIR  # noqa: E402
from discover._profession_reverse_index import build_reverse_index  # noqa: E402

UMBRELLA_TEXT_DIR = RESULTS_DIR / "umbrella_text"
UMBRELLA_SCOPE_DIR = RESULTS_DIR / "umbrella_scope"
LOG_PATH = LOGS_DIR / "assign_umbrella_scope.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("assign_umbrella_scope")


URL_RE = re.compile(r"/chapter-([\w-]+)/(?:part-([\w-]+)/)?section-([\w.-]+)/")

# UT slug form: digits + optional single lowercase letter. e.g. "5a", "31b", "67a", "1b".
# We deliberately require the "under" lead-in: practice-act enumerations in UT
# statute are always phrased as "licensed under Chapter X" or "under Title 58,
# Chapter X" — exception clauses and cross-references say "Chapter X" without
# "under" right before. That structural distinction is what separates scope
# assertions from incidental references.
UNDER_CHAPTER_CITE_RE = re.compile(
    r"under\s+(?:Title\s+58,?\s+)?Chapter\s+(\d+[a-z]?)\b",
    re.I,
)
# Subsection/section enumeration items (e.g. "under Subsection 58-31b-301(2)(d)")
# — same "under" lead-in requirement.
UNDER_SECTION_CITE_RE = re.compile(
    r"under\s+(?:Sub)?[Ss]ection\s+58-(\d+[a-z]?)-",
    re.I,
)

# Anchor-section heuristic: sections whose label / role is to declare scope.
ANCHOR_LABEL_RE = re.compile(
    r"(applicability|definitions|short title|scope of (?:chapter|part|article|title))",
    re.I,
)

# Universal-by-applicability statements. Each entry maps a pattern to the
# scope target it implies. Order matters: more specific phrases first.
UNIVERSAL_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"this title applies to (?:any|every|all)\b[^.]*", re.I), "title"),
    (re.compile(r"applies to every (?:profession|occupation) in this title", re.I), "title"),
    (re.compile(r"any holder of a license[^.]*under this title", re.I), "title"),
    (re.compile(r"this chapter applies to (?:any|every|all)\b[^.]*", re.I), "chapter"),
    (re.compile(r"applies to (?:any|every) regulation of an occupation", re.I), "chapter"),
    (re.compile(r"applies only to the regulation of professions", re.I), "chapter"),
    (re.compile(r"this part applies to (?:any|every|all)\b[^.]*", re.I), "part"),
]

# "As used in this <X>" tells us the target scope of any enumeration in the section.
AS_USED_RE = re.compile(r"as used in this (title|chapter|part)", re.I)

# Section-label patterns that *hint* at profession-specific narrowing.
# Used only to flag for triage; we don't act on these in this first pass.
NARROW_LABEL_HINTS = re.compile(
    r"(psychiatr|prescrib|pharmac|nurse|dentist|optometr|physician|osteopath|"
    r"podiatr|veterinar|cosmetic medical|naturopath|chiropract|midwif|"
    r"physical therap|occupational therap|psycholog|massage|funeral|accountan|"
    r"architect|engineer|surveyor|interior design)",
    re.I,
)


def _canonical_url(url: str) -> str:
    return re.sub(r"/codes/utah/\d{4}/", "/codes/utah/", url)


def dedupe_year_versions(sections: list[dict]) -> list[dict]:
    """Same logical section may appear once per year (2023/2024/2025 plus the
    no-year canonical). Keep the no-year version when present, else the
    largest-URL one (lexicographic, which sorts later years higher)."""
    by_canonical: dict[str, list[dict]] = defaultdict(list)
    for s in sections:
        by_canonical[_canonical_url(s.get("url", ""))].append(s)

    kept: list[dict] = []
    for _key, group in by_canonical.items():
        no_year = [s for s in group if "/codes/utah/title-" in s.get("url", "")]
        kept.append(no_year[0] if no_year else max(group, key=lambda s: s.get("url", "")))
    return kept


def _split_chap_part(section: dict) -> tuple[str, str] | None:
    m = URL_RE.search(section.get("url", ""))
    if not m:
        return None
    chap, part, _sec = m.groups()
    return (f"chapter-{chap}", part or "NO_PART")


def _is_anchor(section: dict) -> bool:
    return bool(ANCHOR_LABEL_RE.search(section.get("label", "")))


def _parse_one_anchor(text: str, reverse_index: dict[str, list[str]]) -> list[dict]:
    """Return zero or more scope signals from a single anchor section's text."""
    signals: list[dict] = []

    for pat, target in UNIVERSAL_PATTERNS:
        m = pat.search(text)
        if m:
            ev_start = max(0, m.start() - 30)
            signals.append({
                "target": target,
                "kind": "universal",
                "evidence": text[ev_start : m.end() + 100].strip(),
            })

    use_m = AS_USED_RE.search(text)
    use_target = use_m.group(1).lower() if use_m else None

    cited_slugs: set[str] = set()
    first_ev = ""
    for m in UNDER_CHAPTER_CITE_RE.finditer(text):
        slug = f"chapter-{m.group(1)}"
        if slug in reverse_index:
            cited_slugs.add(slug)
            if not first_ev:
                first_ev = text[max(0, m.start() - 60) : m.end() + 100].strip()
    for m in UNDER_SECTION_CITE_RE.finditer(text):
        slug = f"chapter-{m.group(1)}"
        if slug in reverse_index:
            cited_slugs.add(slug)

    # Only treat citations as a scope assertion when an "As used in this X"
    # prefix is present in the same anchor; otherwise the citations are likely
    # cross-references, not a scope claim.
    if len(cited_slugs) >= 2 and use_target:
        professions = sorted({p for slug in cited_slugs for p in reverse_index[slug]})
        signals.append({
            "target": use_target,
            "kind": "enumerated",
            "professions": professions,
            "cited_slugs": sorted(cited_slugs),
            "evidence": first_ev,
        })

    return signals


def _select_scope(
    chap: str, part: str, anchors_in_chapter: list[dict], reverse_index: dict[str, list[str]]
) -> dict:
    """Pick the most-specific scope signal that applies to (chap, part).

    Specificity: part-in-this-part > chapter > title. Within the same
    specificity, enumerated beats universal (more informative). Returns
    `{'kind': 'undetermined', 'reason': ...}` when nothing applies.
    """
    by_target: dict[str, list[dict]] = {"part": [], "chapter": [], "title": []}
    for anchor in anchors_in_chapter:
        akey = _split_chap_part(anchor)
        if akey is None:
            continue
        _achap, apart = akey
        for sig in _parse_one_anchor(anchor.get("text", ""), reverse_index):
            if sig["target"] == "part":
                if apart == part:
                    by_target["part"].append(sig)
            elif sig["target"] == "chapter":
                by_target["chapter"].append(sig)
            elif sig["target"] == "title":
                by_target["title"].append(sig)

    for tier in ("part", "chapter", "title"):
        sigs = by_target[tier]
        if not sigs:
            continue
        enumerated = [s for s in sigs if s["kind"] == "enumerated"]
        if enumerated:
            merged_professions = sorted({p for s in enumerated for p in s["professions"]})
            merged_slugs = sorted({s for sig in enumerated for s in sig["cited_slugs"]})
            return {
                "kind": "enumerated",
                "target": tier,
                "professions": merged_professions,
                "cited_slugs": merged_slugs,
                "evidence": enumerated[0]["evidence"],
            }
        return {"kind": "universal", "target": tier, "evidence": sigs[0]["evidence"]}

    return {"kind": "undetermined", "reason": "no_anchor_signal_applies_to_this_part"}


def assign_for_state(state: str) -> dict:
    reverse_index = build_reverse_index(state)
    if not reverse_index:
        raise SystemExit(f"No profession_index entries for state {state!r}")

    src = UMBRELLA_TEXT_DIR / f"{state}.json"
    if not src.exists():
        raise SystemExit(f"Missing umbrella_text file: {src}")

    raw = json.loads(src.read_text())
    sections = dedupe_year_versions(raw.get("sections", []))
    log.info("[%s] %d sections after dedup (from %d raw)", state, len(sections), len(raw.get("sections", [])))

    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    skipped_no_url = 0
    for s in sections:
        key = _split_chap_part(s)
        if key is None:
            skipped_no_url += 1
            continue
        grouped[key].append(s)

    if skipped_no_url:
        log.warning("[%s] %d sections had no parseable URL; dropped", state, skipped_no_url)

    # Group anchors by chapter so part-2 sections can see part-1 anchors.
    anchors_by_chap: dict[str, list[dict]] = defaultdict(list)
    for (chap, _part), secs in grouped.items():
        for s in secs:
            if _is_anchor(s):
                anchors_by_chap[chap].append(s)

    out_sections: list[dict] = []
    triage: list[dict] = []
    source_counter: dict[str, int] = defaultdict(int)

    for (chap, part), secs in sorted(grouped.items()):
        scope = _select_scope(chap, part, anchors_by_chap.get(chap, []), reverse_index)
        log.info(
            "[%s] %s / %s: %d sections, %d chapter-anchors → scope=%s%s",
            state, chap, part, len(secs), len(anchors_by_chap.get(chap, [])),
            scope.get("kind"),
            f" (target={scope.get('target')})" if scope.get("kind") != "undetermined" else "",
        )

        for s in secs:
            is_anchor = _is_anchor(s)
            entry = {
                "url": s.get("url", ""),
                "label": s.get("label", ""),
                "umbrella_chapter_slug": chap,
                "umbrella_part": part,
                "is_anchor": is_anchor,
                "applies_to_professions": None,
                "scope_source": None,
                "scope_target": None,
                "scope_evidence": "",
            }

            if scope["kind"] == "universal":
                entry["scope_source"] = "anchor_universal" if is_anchor else "universal"
                entry["scope_target"] = scope["target"]
                entry["scope_evidence"] = scope["evidence"]
            elif scope["kind"] == "enumerated":
                entry["applies_to_professions"] = scope["professions"]
                entry["scope_source"] = (
                    "anchor_enumeration" if is_anchor else "inherited_enumeration"
                )
                entry["scope_target"] = scope["target"]
                entry["scope_evidence"] = scope["evidence"]
            else:
                entry["scope_source"] = "undetermined"
                triage.append({
                    "reason": "undetermined_scope",
                    "detail": scope.get("reason", ""),
                    "chapter": chap,
                    "part": part,
                    "url": entry["url"],
                    "label": entry["label"],
                })

            if NARROW_LABEL_HINTS.search(entry["label"]):
                triage.append({
                    "reason": "label_suggests_narrowing",
                    "chapter": chap,
                    "part": part,
                    "url": entry["url"],
                    "label": entry["label"],
                    "current_scope_source": entry["scope_source"],
                    "current_professions": entry["applies_to_professions"],
                })

            source_counter[entry["scope_source"]] += 1
            out_sections.append(entry)

    return {
        "state": state,
        "section_count": len(out_sections),
        "scope_source_counts": dict(source_counter),
        "triage": triage,
        "sections": out_sections,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    args = ap.parse_args()

    result = assign_for_state(args.state)

    UMBRELLA_SCOPE_DIR.mkdir(parents=True, exist_ok=True)
    out = UMBRELLA_SCOPE_DIR / f"{args.state}.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    print(f"\nWrote {out}")
    print(f"  {result['section_count']} sections")
    print(f"  scope_source counts: {result['scope_source_counts']}")
    print(f"  triage entries: {len(result['triage'])}")


if __name__ == "__main__":
    main()
