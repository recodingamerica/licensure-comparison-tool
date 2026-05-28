"""Comprehensive occupation harvester / harmonizer.

Two outputs for human review, both grounded in actual state hierarchy data:

1. **Variants per existing profession** — for every canonical id in
   professions.yaml, the distinct chapter-label wordings matched across
   states (the harmonization map, evidenced not guessed). Useful for
   thickening `patterns` / `enumeration_aliases` from observed wordings.

2. **Candidate new occupations** — chapter labels across all 50 state
   hierarchies that *look* like profession-board / practice-act chapters
   (heuristic) but match NO canonical profession in the current yaml. Grouped
   by the noun phrase that follows "Board of" / "Practice of" / etc., with
   the states they appear in.

Usage:
  python -m pipeline.discover.harvest_occupations
  python -m pipeline.discover.harvest_occupations --min-states 3
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import HIERARCHY_DIR, PROFESSION_INDEX_DIR, RESULTS_DIR  # noqa: E402

OUT_DIR = RESULTS_DIR / "taxonomy_harvest"
OUT_DIR.mkdir(parents=True, exist_ok=True)

log = logging.getLogger("harvest_occupations")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


# Heuristic patterns for "this chapter label names a licensed-profession board
# or practice act." We extract the noun phrase that follows the marker.
_BOARD_PATTERNS = [
    re.compile(r"\bBoard\s+(?:of|for)\s+([A-Z][A-Za-z, &\-/]{3,80})", re.I),
    re.compile(r"\b([A-Z][A-Za-z, &\-/]{3,60})\s+Board\b"),
    re.compile(r"\b([A-Z][A-Za-z, &\-/]{3,60})\s+(?:Practice|Licensing|Licensure)\s+Act\b"),
    re.compile(r"\bPractice\s+(?:of|by)\s+([A-Z][A-Za-z, &\-/]{3,60})", re.I),
    re.compile(r"\bLicensure\s+of\s+([A-Z][A-Za-z, &\-/]{3,60})", re.I),
]
# Phrases that are clearly NOT a profession when extracted (administrative,
# definitional, headers).
_NOISE_PHRASES = {
    "general provisions", "definitions", "general", "administration",
    "the department", "the division", "the state", "appeals", "violations",
    "fees", "discipline", "examination", "examinations", "applicants",
    "appointment", "powers and duties", "professional regulation",
    "professional and occupational regulation", "occupational licensing",
    "occupational regulation", "professional regulation review",
    # Single bare nouns the regex over-extracts from board names like
    # "STATE BOARD OF HEALTH" -> "state", or "Board of Regents" generic refs.
    "state", "health", "examiners", "regents", "education", "agriculture",
    "trustees", "directors", "the board", "commerce", "trade",
}

# Slug prefixes that indicate a CHAPTER-level container (vs. an individual
# section). Hierarchies for states like AZ include section-level entries, and
# "Board of X" in a section title is incidental, not a profession-board.
_CONTAINER_SLUG = re.compile(r"^(chapter|title|article|division|part|subtitle|act)[-_]", re.I)


def _normalize(phrase: str) -> str:
    return re.sub(r"\s+", " ", phrase.strip(" ,.:;-")).lower()


def _extract_candidates(label: str) -> list[str]:
    cands: list[str] = []
    for pat in _BOARD_PATTERNS:
        for m in pat.finditer(label):
            phrase = _normalize(m.group(1))
            if 3 <= len(phrase) <= 80 and phrase not in _NOISE_PHRASES:
                cands.append(phrase)
    return cands


def variants_per_profession() -> dict[str, dict[str, list[str]]]:
    """For each canonical id, distinct chapter labels matched per state."""
    out: dict[str, dict[str, list[str]]] = {}
    for f in sorted(PROFESSION_INDEX_DIR.glob("*.json")):
        if f.stem.startswith("_"):
            continue
        d = json.loads(f.read_text())
        per_state: dict[str, list[str]] = {}
        for st, payload in (d.get("by_state") or {}).items():
            labels = sorted({m.get("label", "").strip()
                             for m in (payload.get("matched") or []) if m.get("label")})
            if labels:
                per_state[st] = labels
        out[f.stem] = per_state
    return out


def candidate_new_occupations(min_states: int) -> list[dict]:
    """Chapter labels across all state hierarchies that look like profession
    boards but match no canonical profession in any current profession_index.
    Grouped by the extracted noun phrase."""
    # All labels already claimed by some profession.
    claimed: set[tuple[str, str]] = set()   # (state, slug)
    for f in PROFESSION_INDEX_DIR.glob("*.json"):
        if f.stem.startswith("_"):
            continue
        d = json.loads(f.read_text())
        for st, payload in (d.get("by_state") or {}).items():
            for m in (payload.get("matched") or []):
                claimed.add((st, m.get("slug", "")))

    # Walk hierarchies; for each unclaimed CHAPTER-level entry, extract
    # candidate phrases. Skip section-level entries (some hierarchies include
    # sections, where "Board of X" in a section title is incidental, not a
    # profession-board chapter).
    by_phrase: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    # Also track which canonical professions already claim a chapter whose
    # extracted phrase matches — those phrases are wording variants for an
    # existing profession (useful to surface separately).
    for f in sorted(HIERARCHY_DIR.glob("*.json")):
        st = f.stem
        d = json.loads(f.read_text())
        for ch in d.get("chapters", []):
            slug = ch.get("slug", "")
            label = ch.get("label", "")
            if not _CONTAINER_SLUG.match(slug):
                continue  # section-level entry — skip
            if (st, slug) in claimed:
                continue
            for phrase in _extract_candidates(label):
                by_phrase[phrase].append((st, slug, label))

    rows: list[dict] = []
    for phrase, hits in by_phrase.items():
        states = sorted({h[0] for h in hits})
        if len(states) < min_states:
            continue
        rows.append({
            "phrase": phrase,
            "n_states": len(states),
            "states": states,
            "examples": [{"state": s, "slug": sl, "label": lab} for s, sl, lab in hits[:6]],
        })
    rows.sort(key=lambda r: -r["n_states"])
    return rows


# Heuristic: a chapter label that's basically a plural profession noun, like
# "Auctioneers" / "Counselors" / "Real Estate Appraisers" / "Cosmetologists".
# Short labels (after stripping the "Chapter N - " prefix) whose noun word
# ends in a person-suffix.
_LABEL_PREFIX_RE = re.compile(r"^(?:Chapter|Title|Article|Division|Part|Subtitle|Act)\s+[\dA-Za-z\.\-]+\s*[:\-—–]\s*", re.I)
_PERSON_SUFFIX_RE = re.compile(r"\b([A-Z][A-Za-z\-]+(?:ers|ors|ists|ians|ants|eers))\b")


def looks_like_profession_label(label: str) -> str | None:
    """Return the profession-noun phrase if the label looks like a plain
    profession-name chapter ('Counselors', 'Auctioneers', 'Real Estate
    Appraisers'); None otherwise."""
    body = _LABEL_PREFIX_RE.sub("", label).strip(" .;:[]")
    # Drop trailing parenthetical / annotation like "[Repealed]"
    body = re.sub(r"\s*\[(?:Repealed|Reserved|Unconstitutional[^\]]*)\]\s*$", "", body, flags=re.I).strip()
    if not body or len(body) > 80:
        return None
    m = _PERSON_SUFFIX_RE.search(body)
    if not m:
        return None
    # If the body IS basically that noun phrase (allowing a leading modifier),
    # treat it as a profession label. Bail on long sentences ("...required by
    # X to do Y...").
    if len(body.split()) > 8:
        return None
    return body


def all_unmatched_chapters() -> dict[str, list[dict]]:
    """Every chapter-level entry in any state hierarchy that's NOT claimed by
    any profession in profession_index — no regex filter, no heuristic.
    The recall ceiling: anything missing must be in here. For human/LLM
    review."""
    claimed: set[tuple[str, str]] = set()
    for f in PROFESSION_INDEX_DIR.glob("*.json"):
        if f.stem.startswith("_"):
            continue
        d = json.loads(f.read_text())
        for st, payload in (d.get("by_state") or {}).items():
            for m in (payload.get("matched") or []):
                claimed.add((st, m.get("slug", "")))
    out: dict[str, list[dict]] = {}
    for f in sorted(HIERARCHY_DIR.glob("*.json")):
        st = f.stem
        d = json.loads(f.read_text())
        unmatched = []
        for ch in d.get("chapters", []):
            slug = ch.get("slug", "")
            if not _CONTAINER_SLUG.match(slug):
                continue
            if (st, slug) in claimed:
                continue
            unmatched.append({"slug": slug, "label": ch.get("label", "")})
        if unmatched:
            out[st] = unmatched
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-states", type=int, default=3,
                    help="Only surface candidate new occupations seen in >= N states (default 3)")
    args = ap.parse_args()

    variants = variants_per_profession()
    candidates = candidate_new_occupations(args.min_states)
    raw_unmatched = all_unmatched_chapters()

    # Second-pass candidates: labels that look like a plain profession-name
    # chapter (plural person-noun like "Auctioneers", "Real Estate Appraisers")
    # but were missed by the Board-of-X regex.
    plural_candidates: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for st, items in raw_unmatched.items():
        for it in items:
            phrase = looks_like_profession_label(it["label"])
            if phrase:
                plural_candidates[phrase.lower()].append((st, it["slug"], it["label"]))
    plural_rows = []
    for phrase, hits in plural_candidates.items():
        states = sorted({h[0] for h in hits})
        if len(states) < args.min_states:
            continue
        plural_rows.append({"phrase": phrase, "n_states": len(states), "states": states,
                            "examples": [{"state": s, "slug": sl, "label": lab} for s, sl, lab in hits[:6]]})
    plural_rows.sort(key=lambda r: -r["n_states"])

    (OUT_DIR / "variants.json").write_text(json.dumps(variants, indent=2, ensure_ascii=False))
    (OUT_DIR / "candidates.json").write_text(json.dumps(candidates, indent=2, ensure_ascii=False))
    (OUT_DIR / "plural_candidates.json").write_text(json.dumps(plural_rows, indent=2, ensure_ascii=False))
    (OUT_DIR / "all_unmatched.json").write_text(json.dumps(raw_unmatched, indent=2, ensure_ascii=False))

    print(f"\n=== Variant summary — existing professions ({len(variants)}) ===")
    print("(distinct chapter-label wordings observed per profession, top 5 widest-reaching)")
    sized = sorted(variants.items(), key=lambda kv: -len(kv[1]))
    for pid, per_state in sized[:8]:
        n_states = len(per_state)
        all_labels = sorted({lab for labs in per_state.values() for lab in labs})
        print(f"  {pid:30}  {n_states:>3} states · {len(all_labels):>3} distinct labels")
        for lab in all_labels[:3]:
            print(f"      e.g. {lab[:90]}")
    print(f"  ...wrote full map to {OUT_DIR/'variants.json'}")

    print(f"\n=== Candidate NEW occupations (board-like, currently unmatched, >= {args.min_states} states) ===")
    for r in candidates[:25]:
        ex = r["examples"][0]
        print(f"  {r['n_states']:>3} states  '{r['phrase']}'  e.g. {ex['state']} {ex['slug']}: {ex['label'][:60]}")
    print(f"  ({len(candidates)} total — full list in {OUT_DIR/'candidates.json'})")

    total_unmatched = sum(len(v) for v in raw_unmatched.values())
    print(f"\n=== Plain-noun profession-label candidates (>= {args.min_states} states) ===")
    print(f"  (labels like 'Auctioneers' / 'Real Estate Appraisers' that the Board-of-X regex missed)")
    for r in plural_rows[:40]:
        ex = r["examples"][0]
        print(f"  {r['n_states']:>3} states  '{r['phrase']}'  e.g. {ex['state']} {ex['slug']}: {ex['label'][:60]}")
    print(f"  ({len(plural_rows)} total — full list in {OUT_DIR/'plural_candidates.json'})")

    print(f"\n=== Recall ceiling: {total_unmatched} unmatched CHAPTER-level entries across "
          f"{len(raw_unmatched)} states ===")
    print(f"  (every chapter-level label not in ANY profession_index — full dump in {OUT_DIR/'all_unmatched.json'})")
    print("  Anything we're missing is in there; most are non-profession (courts, tax, schools, …).")


if __name__ == "__main__":
    main()
