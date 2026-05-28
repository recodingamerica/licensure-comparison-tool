"""Assign per-section scope to a state's umbrella sections, using the statute
text itself as evidence — no LLM, no family heuristics.

For each umbrella chapter, we identify the anchor sections (Applicability /
Definitions / Title / Scope) and read their text for two kinds of signal:

  1. A universal statement ("This chapter applies to any regulation of an
     occupation", "As used in this title", etc.) → scope = universal.
  2. A trigger phrase ("licensed under", "licensed to practice") followed
     by a list of practice-act citations → scope = the list of professions
     those chapters resolve to via the profession_index reverse-index.

Each signal carries a *scope target* — `title`, `chapter`, or `part`. A
title-target signal scopes every section in every chapter of that title; a
chapter-target signal scopes every section in that chapter; a part-target
signal scopes only sections within the same part as the anchor.

When several signals apply, the most specific (part > chapter > title) wins.
Sections we can't deterministically scope are written with
`scope_source: "undetermined"` and listed in the triage report. We fail
loudly rather than guessing. No LLM fallbacks.

The state-specific knobs (what universal phrasing looks like, what triggers
introduce an enumeration, what citation format the state uses) live in
`pipeline/discover/_scope_rules.py`. The walker itself is state-agnostic.

Output: pipeline/results/umbrella_scope/<STATE>.json
Triage report: same file, top-level `triage` array.

Usage:
  python -m pipeline.discover.assign_umbrella_scope --state UT
  python -m pipeline.discover.assign_umbrella_scope --state FL
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
from discover._scope_rules import (  # noqa: E402
    STATE_RULES,
    StateScopeRules,
    ANCHOR_LABEL_RE,
    AS_USED_RE,
    NARROW_LABEL_HINTS,
    LEAF_SECTION_SEG,
)
from discover._state_scope_manifest import (  # noqa: E402
    load_manifest,
    manifest_decision_for,
)
from scope_sources import METHOD_MANIFEST  # noqa: E402

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


# Used only to extract the `part` segment from a section's URL. Chapter
# grouping uses each section's `umbrella_chapter_slug` field directly so
# state-specific slug shapes (UT's `chapter-4a`, CO's `article-30`, even
# pseudo-slugs like `general-provisions`) all work without per-state URL regex.
URL_PART_RE = re.compile(r"/part-([\w-]+)/")
YEAR_PREFIX_RE = re.compile(r"/codes/[a-z-]+/\d{4}/")

# Top-level definition boundary: a newline followed by `(N)"` where N is a
# digit. Sub-items use `(a)`, `(i)`, etc. — this regex deliberately doesn't
# match those. We use it to bound the trigger-then-scan window so that a
# scope enumeration in one definition doesn't bleed into the next definition's
# cross-references (e.g. UT Ch 88 § 201's "Dispensing practitioner" list
# stopping before "Drug means the same as defined in Section 58-17b-102").
DEFINITION_BOUNDARY_RE = re.compile(r'\n\s*\(\d+\)\s*"')


def _cite_token_to_slug(token: str | None, slug_prefix: str) -> str:
    """Build a reverse-index slug from a captured citation token.

    Justia slugs are dash-joined (`chapter-18-22`), but some states write
    multi-part cites with dots (WA "chapter 18.22", "18.22.010") — so we
    normalize dots to dashes. For states whose tokens are already single
    dash/letter forms (UT "31b", FL "456", CO "200") this is a no-op.

    Returns "" for a None token (an LLM-proposed pattern with an optional
    capturing group can match with group(1) unset) — "" won't be in any
    reverse-index, so the cite is simply skipped rather than crashing.
    """
    if token is None:
        return ""
    return f"{slug_prefix}-{token.lower().replace('.', '-')}"


def _canonical_url(url: str) -> str:
    """Strip the year-version segment so 2024/foo and current/foo dedupe."""
    return YEAR_PREFIX_RE.sub(lambda m: m.group(0).rsplit("/", 2)[0] + "/", url)


def dedupe_year_versions(sections: list[dict]) -> list[dict]:
    """Same logical section often appears once per year (2023/2024/2025 plus
    the no-year canonical URL). Keep the no-year version when present, else
    the largest-URL one (lexicographic sort puts later years higher)."""
    by_canonical: dict[str, list[dict]] = defaultdict(list)
    for s in sections:
        by_canonical[_canonical_url(s.get("url", ""))].append(s)

    kept: list[dict] = []
    for _key, group in by_canonical.items():
        no_year = [s for s in group if not YEAR_PREFIX_RE.search(s.get("url", ""))]
        kept.append(no_year[0] if no_year else max(group, key=lambda s: s.get("url", "")))
    return kept


def _split_chap_part(section: dict) -> tuple[str, str] | None:
    """Group key for a section: the umbrella_chapter_slug (which is whatever
    Justia calls the chapter — e.g. `chapter-4a`, `article-30`, or even
    pseudo-slugs the discover step inferred like `general-provisions`),
    plus the part token extracted from the URL when present.

    Returns None for chapter-landing-page entries that snuck into the
    umbrella_text record (Justia banner pages with URLs like
    `/codes/utah/title-58/chapter-88/` and labels like `2025 Utah Code`).
    Those aren't sections and shouldn't be scoped. A section is recognised by
    its last URL segment matching LEAF_SECTION_SEG (section-/statute-/rs-/bare-
    integer forms across states), which container segments like `chapter-88`
    do not.
    """
    url = section.get("url", "")
    slug = section.get("umbrella_chapter_slug")
    if not slug:
        return None
    segments = [s for s in url.rstrip("/").split("/") if s]
    if not segments or not LEAF_SECTION_SEG.match(segments[-1]):
        return None
    part_m = URL_PART_RE.search(url)
    return (slug, part_m.group(1) if part_m else "NO_PART")


def _is_anchor(section: dict) -> bool:
    return bool(ANCHOR_LABEL_RE.search(section.get("label", "")))


_PROFESSION_TERMS_CACHE: list[tuple[str, str, list[str]]] | None = None


def _load_profession_terms() -> list[tuple[str, str, list[str]]]:
    """Return a list of (profession_id, term_lower, excludes_lower) entries
    from professions.yaml. One entry per pattern/alias term, sorted longest
    first so most-specific matches win when iterating.

    `term_lower` is what we substring-match against. `excludes_lower` is the
    profession's exclude list (a hit on any exclude in the *same containing
    term* disqualifies that profession for that term — same convention as
    chapter-label matching).
    """
    global _PROFESSION_TERMS_CACHE
    if _PROFESSION_TERMS_CACHE is not None:
        return _PROFESSION_TERMS_CACHE
    import yaml
    from paths import CONFIG_DIR
    cfg = yaml.safe_load((CONFIG_DIR / "professions.yaml").read_text()) or {}
    entries: list[tuple[str, str, list[str]]] = []
    for pid, pdef in cfg.items():
        if not isinstance(pdef, dict):
            continue
        excludes = [e.lower() for e in (pdef.get("excludes") or [])]
        terms = (pdef.get("patterns") or []) + (pdef.get("enumeration_aliases") or [])
        for t in terms:
            entries.append((pid, t.lower().strip(), excludes))
    entries.sort(key=lambda e: -len(e[1]))  # longest first → most-specific wins
    _PROFESSION_TERMS_CACHE = entries
    return entries


_SPLIT_LIST_RE = re.compile(r"\s*(?:,|;|\bor\b)\s*", re.I)


def _match_professions_in_window(text: str) -> tuple[set[str], str]:
    """Walk a post-trigger window of text. Split into comma/semicolon/or-
    separated terms; for each term, find the most-specific profession match
    from `_load_profession_terms()`. Return (set of profession_ids, first
    evidence snippet).
    """
    matched: set[str] = set()
    first_ev = ""
    entries = _load_profession_terms()
    # Split into candidate terms; each is a phrase like "podiatric physician"
    # or "marital and family therapist".
    for term in _SPLIT_LIST_RE.split(text):
        term_clean = term.strip().strip(".:;").lower()
        if len(term_clean) < 4 or len(term_clean) > 120:
            continue
        # Longest pattern wins: iterate sorted entries, accept first non-
        # disqualified match.
        for pid, pattern, excludes in entries:
            if pattern in term_clean and not any(exc in term_clean for exc in excludes):
                matched.add(pid)
                if not first_ev and len(term_clean) < 80:
                    first_ev = term.strip()
                break
    return matched, first_ev


def _parse_one_anchor(
    text: str, rules: StateScopeRules, reverse_index: dict[str, list[str]]
) -> list[dict]:
    """Return zero or more scope signals from a single anchor section's text."""
    signals: list[dict] = []

    for pat, target in rules.universal_patterns:
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
    if use_target == "subtitle":
        use_target = "title"  # subtitle scope behaves like title-tier for our purposes
    # If the anchor doesn't say "As used in this <X>" explicitly, default to
    # chapter-target. A bare "Definitions." section without a scoping prefix
    # most naturally scopes its terms to the chapter it lives in.
    if use_target is None:
        use_target = "chapter"

    # Find every trigger occurrence; from each one, scan forward up to
    # scan_window chars for chapter/section citations. This is what separates
    # scope assertions (a list of practice acts following "licensed under")
    # from incidental cross-references that appear anywhere else in the text.
    cited_slugs: set[str] = set()
    first_ev = ""
    for trigger_re in rules.trigger_patterns:
        for tm in trigger_re.finditer(text):
            raw_tail = text[tm.end() : tm.end() + rules.scan_window]
            boundary = DEFINITION_BOUNDARY_RE.search(raw_tail)
            tail = raw_tail[: boundary.start()] if boundary else raw_tail
            for m in rules.chapter_cite_pattern.finditer(tail):
                slug = _cite_token_to_slug(m.group(1), rules.slug_prefix)
                if slug in reverse_index:
                    cited_slugs.add(slug)
                    if not first_ev:
                        abs_pos = tm.end() + m.start()
                        first_ev = text[max(0, abs_pos - 60) : abs_pos + 100].strip()
            for m in rules.section_cite_pattern.finditer(tail):
                slug = _cite_token_to_slug(m.group(1), rules.slug_prefix)
                if slug in reverse_index:
                    cited_slugs.add(slug)

    if len(cited_slugs) >= 2 and use_target:
        professions = sorted({p for slug in cited_slugs for p in reverse_index[slug]})
        signals.append({
            "target": use_target,
            "kind": "enumerated",
            "professions": professions,
            "cited_slugs": sorted(cited_slugs),
            "evidence": first_ev,
        })

    # Profession-name list enumeration (e.g. Iowa § 147.1(3): "when applied
    # to a physician and surgeon, podiatric physician, ... means a person
    # licensed under this subtitle"). For each trigger occurrence, scan the
    # post-trigger window, split into comma/semicolon-separated terms, and
    # map each term to a canonical profession via professions.yaml.
    for trigger_re in rules.profession_name_trigger_patterns:
        for tm in trigger_re.finditer(text):
            raw_tail = text[tm.end() : tm.end() + rules.scan_window]
            boundary = DEFINITION_BOUNDARY_RE.search(raw_tail)
            tail = raw_tail[: boundary.start()] if boundary else raw_tail
            matched_profs, ev = _match_professions_in_window(tail)
            if len(matched_profs) >= 2 and use_target:
                signals.append({
                    "target": use_target,
                    "kind": "enumerated",
                    "professions": sorted(matched_profs),
                    "cited_slugs": [],  # this enumeration is by name, not slug
                    "evidence": ev or tail[:160].strip(),
                })

    # Range-form enumeration (e.g. CO Article 30: "applies to articles 200 to
    # 315 of this title 12"). When present, enumerate every integer in the
    # range, look each up as a slug, and treat the resulting set as a
    # chapter-target scope assertion. The range pattern is self-anchoring —
    # it doesn't need an "As used in this X" prefix because the phrasing
    # itself is a scope statement.
    if rules.range_chapter_pattern is not None:
        for m in rules.range_chapter_pattern.finditer(text):
            start_n = int(m.group(1))
            end_n = int(m.group(2))
            if end_n < start_n or end_n - start_n > 1000:
                continue  # implausible; skip
            range_slugs = {
                f"{rules.slug_prefix}-{n}" for n in range(start_n, end_n + 1)
            }
            valid = sorted(range_slugs & set(reverse_index.keys()))
            if len(valid) >= 2:
                professions = sorted({p for s in valid for p in reverse_index[s]})
                ev_start = max(0, m.start() - 30)
                signals.append({
                    "target": "chapter",
                    "kind": "enumerated",
                    "professions": professions,
                    "cited_slugs": valid,
                    "evidence": text[ev_start : m.end() + 100].strip(),
                })

    return signals


def _select_scope(
    chap: str, part: str,
    anchors_in_chapter: list[dict],
    rules: StateScopeRules,
    reverse_index: dict[str, list[str]],
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
        for sig in _parse_one_anchor(anchor.get("text", ""), rules, reverse_index):
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


def _load_grouped(state: str) -> dict[tuple[str, str], list[dict]]:
    """Load umbrella_text, dedupe year-versions, and group sections by
    (chapter_slug, part), dropping non-section URLs (banner/landing pages)
    and any chapters explicitly excluded by the state's scope manifest.
    Shared by the rules-based walker and the rules-free skeleton."""
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

    manifest = load_manifest(state)
    if manifest.drop_chapters:
        n_before = sum(len(v) for v in grouped.values())
        chaps_before = {k[0] for k in grouped}
        grouped = {k: v for k, v in grouped.items() if k[0] not in manifest.drop_chapters}
        n_after = sum(len(v) for v in grouped.values())
        actually_dropped = chaps_before & manifest.drop_chapters
        if actually_dropped:
            log.info(
                "[%s] manifest dropped %d sections from %d chapter(s): %s",
                state, n_before - n_after, len(actually_dropped), sorted(actually_dropped),
            )
    return grouped


def _apply_manifest_to_entry(decision: dict, entry: dict) -> None:
    """In-place: fill in scope_source / applies_to / method from a manifest
    decision. Used by both the skeleton and rules-based paths so the manifest
    layer is the single source of truth for hardcoded scope."""
    if decision["kind"] == "universal":
        entry["scope_source"] = "universal"
        entry["scope_target"] = "all_professions"
        entry["scope_evidence"] = "manifest: chapter_universal"
    elif decision["kind"] == "enumerated":
        entry["applies_to_professions"] = list(decision["professions"])
        entry["scope_source"] = "inherited_enumeration"
        entry["scope_target"] = "chapter"
        entry["scope_evidence"] = "manifest: chapter_applies_to"
    entry["scope_method"] = METHOD_MANIFEST


def skeleton_for_state(state: str) -> dict:
    """The walker's output shape for a state with NO scope rules: every section
    structured (same dedup/grouping/anchor detection as the real walker) but
    left `undetermined` — except where a per-state manifest hardcodes a
    decision for the chapter. Pass 3 (LLM fallback) then fills in remaining
    undetermined sections, and the merge works uniformly across ruled and
    unruled states.
    """
    grouped = _load_grouped(state)
    manifest = load_manifest(state)
    out_sections: list[dict] = []
    source_counter: dict[str, int] = defaultdict(int)
    for (chap, part), secs in sorted(grouped.items()):
        manifest_decision = manifest_decision_for(manifest, chap)
        for s in secs:
            entry = {
                "url": s.get("url", ""),
                "label": s.get("label", ""),
                "umbrella_chapter_slug": chap,
                "umbrella_part": part,
                "is_anchor": _is_anchor(s),
                "applies_to_professions": None,
                "scope_source": "undetermined",
                "scope_target": None,
                "scope_evidence": "",
            }
            if manifest_decision is not None:
                _apply_manifest_to_entry(manifest_decision, entry)
            source_counter[entry["scope_source"]] += 1
            out_sections.append(entry)
    return {
        "state": state,
        "section_count": len(out_sections),
        "scope_source_counts": dict(source_counter),
        "triage": [],
        "sections": out_sections,
    }


def assign_for_state(state: str) -> dict:
    rules = STATE_RULES.get(state)
    if rules is None:
        raise SystemExit(
            f"No scope rules for state {state!r}. Add an entry to "
            "pipeline/discover/_scope_rules.py::STATE_RULES."
        )

    reverse_index = build_reverse_index(state)
    if not reverse_index:
        raise SystemExit(f"No profession_index entries for state {state!r}")

    grouped = _load_grouped(state)

    # Drop chapters explicitly excluded in the state's scope rules (e.g.
    # building-safety or admin-procedure chapters pulled in by the discover
    # step that aren't occupational licensing umbrella chapters).
    if rules.excluded_chapter_slugs:
        excluded = set(rules.excluded_chapter_slugs)
        n_before = sum(len(v) for v in grouped.values())
        grouped = {k: v for k, v in grouped.items() if k[0] not in excluded}
        n_after = sum(len(v) for v in grouped.values())
        if n_before != n_after:
            log.info(
                "[%s] excluded %d sections from %d chapter(s): %s",
                state, n_before - n_after, len(excluded), sorted(excluded),
            )

    manifest = load_manifest(state)

    anchors_by_chap: dict[str, list[dict]] = defaultdict(list)
    for (chap, _part), secs in grouped.items():
        for s in secs:
            if _is_anchor(s):
                anchors_by_chap[chap].append(s)

    out_sections: list[dict] = []
    triage: list[dict] = []
    source_counter: dict[str, int] = defaultdict(int)

    for (chap, part), secs in sorted(grouped.items()):
        manifest_decision = manifest_decision_for(manifest, chap)
        if manifest_decision is None:
            scope = _select_scope(chap, part, anchors_by_chap.get(chap, []), rules, reverse_index)
        else:
            # Manifest is authoritative for this chapter — skip the regex walker
            # so the hardcoded decision can't be undone by accidental anchor
            # matching, and so it's auditable as scope_method="manifest".
            scope = {"kind": "manifest", "decision": manifest_decision}
        log.info(
            "[%s] %s / %s: %d sections, %d chapter-anchors → scope=%s%s",
            state, chap, part, len(secs), len(anchors_by_chap.get(chap, [])),
            scope.get("kind"),
            f" (target={scope.get('target')})" if scope.get("kind") not in ("undetermined", "manifest") else "",
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

            if scope["kind"] == "manifest":
                _apply_manifest_to_entry(scope["decision"], entry)
            elif scope["kind"] == "universal":
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
    ap.add_argument(
        "--skeleton", action="store_true",
        help="Emit an all-undetermined skeleton (no scope rules) for LLM-only "
             "states. Implied automatically when the state has no STATE_RULES entry.",
    )
    args = ap.parse_args()

    state = args.state
    if args.skeleton or state not in STATE_RULES:
        if state not in STATE_RULES:
            log.info("[%s] no scope rules — emitting all-undetermined skeleton "
                     "(LLM-fallback territory)", state)
        result = skeleton_for_state(state)
    else:
        result = assign_for_state(state)

    UMBRELLA_SCOPE_DIR.mkdir(parents=True, exist_ok=True)
    out = UMBRELLA_SCOPE_DIR / f"{args.state}.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    print(f"\nWrote {out}")
    print(f"  {result['section_count']} sections")
    print(f"  scope_source counts: {result['scope_source_counts']}")
    print(f"  triage entries: {len(result['triage'])}")


if __name__ == "__main__":
    main()
