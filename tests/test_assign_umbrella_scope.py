"""Regression tests for the umbrella scope walker (assign_umbrella_scope).

Two layers:

1. Unit tests for the leaf-section detector (`LEAF_SECTION_SEG`) and the
   group-key function (`_split_chap_part`). These guard the per-state URL
   shapes Justia uses — section-/statute-/rs-/bare-integer leaves are real
   sections; chapter-/title-/division- landing pages are not.

2. Golden characterization tests over the five validated states (UT, FL, CO,
   IA, WI). They freeze the current `scope_source_counts` so any walker change
   that shifts a known-good state's classification fails loudly. The FL case
   additionally pins the § 455.017 trap: chapter-455 is DBPR-scoped, NOT
   universal, and must stay undetermined (this exact property regressed once
   when an LLM-rules output was committed over the hand-tuned result).

The golden tests read the committed real data (umbrella_text + profession_index)
and skip if it's absent, so they don't fail in a data-less checkout.
"""

from __future__ import annotations

import json

import pytest

import re

from pipeline.scope.assign_umbrella_scope import (
    _split_chap_part,
    _parse_one_anchor,
    assign_for_state,
    UMBRELLA_TEXT_DIR,
)
from pipeline.scope._scope_rules import LEAF_SECTION_SEG, StateScopeRules, ANCHOR_LABEL_RE


# ---------------------------------------------------------------------------
# Unit: LEAF_SECTION_SEG — which last-path-segments count as a leaf section
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("segment", [
    "section-58-1-102",   # UT / FL / CO standard
    "statute-622-005",    # NV / NE
    "rs-37-1",            # LA
    "12-30-101",          # CO bare cite leaf
    "7901",               # NY bare integer
    "section_1",          # underscore variant
    "s-1",                # abbreviated
])
def test_leaf_seg_matches_section_forms(segment):
    assert LEAF_SECTION_SEG.match(segment)


@pytest.mark.parametrize("segment", [
    "chapter-88",
    "chapter-1b",
    "title-58",
    "division-10",
    "part-3",
    "subchapter-4",
    "article-130-1",      # NY uses this as a banner/landing leaf, not a section
])
def test_leaf_seg_rejects_container_landings(segment):
    assert not LEAF_SECTION_SEG.match(segment)


# ---------------------------------------------------------------------------
# Unit: _split_chap_part — group key (chapter_slug, part) or None
# ---------------------------------------------------------------------------

def _sec(url, slug):
    return {"url": url, "umbrella_chapter_slug": slug}


def test_split_keeps_section_leaf():
    s = _sec("https://law.justia.com/codes/utah/title-58/chapter-1/section-58-1-102/", "chapter-1")
    assert _split_chap_part(s) == ("chapter-1", "NO_PART")


def test_split_keeps_statute_leaf():
    # Fix A: NV-style statute- leaf under a real chapter must be kept.
    s = _sec("https://law.justia.com/codes/nevada/chapter-622/statute-622-005/", "chapter-622")
    assert _split_chap_part(s) == ("chapter-622", "NO_PART")


def test_split_keeps_rs_leaf():
    # Fix A: LA-style rs- leaf (section-level umbrella, slug == leaf) kept.
    s = _sec("https://law.justia.com/codes/louisiana/revised-statutes/title-37/rs-37-1/", "rs-37-1")
    assert _split_chap_part(s) == ("rs-37-1", "NO_PART")


def test_split_drops_chapter_landing_page():
    # Banner/landing page (last segment is a container) — not a section.
    s = _sec("https://law.justia.com/codes/utah/title-58/chapter-88/", "chapter-88")
    assert _split_chap_part(s) is None


def test_split_extracts_part_token():
    s = _sec("https://law.justia.com/codes/utah/title-58/chapter-4/part-2/section-58-4-201/", "chapter-4")
    assert _split_chap_part(s) == ("chapter-4", "2")


def test_split_none_without_slug():
    assert _split_chap_part({"url": "https://x/section-1/"}) is None


def test_split_none_empty_url():
    assert _split_chap_part({"url": "", "umbrella_chapter_slug": "chapter-1"}) is None


# ---------------------------------------------------------------------------
# Unit: ANCHOR_LABEL_RE — "Application of chapter" is a scope anchor
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("label", [
    "18.235.020 - Application of chapter—Director's authority—Disciplinary authority.",
    "Application of this chapter",
    "Application of chapter",
    "Sec. 3. Application of the chapter",
])
def test_anchor_matches_application_of_chapter(label):
    assert ANCHOR_LABEL_RE.search(label)


@pytest.mark.parametrize("label", [
    "Application for a license",      # process, not scope
    "Application requirements",
    "Application fee",
    "Renewal application",
])
def test_anchor_rejects_application_for_license(label):
    assert not ANCHOR_LABEL_RE.search(label)


# ---------------------------------------------------------------------------
# Unit: _parse_one_anchor citation resolution (dotted vs dash slugs)
# ---------------------------------------------------------------------------

def test_parse_anchor_resolves_dotted_cites_to_dash_slugs():
    # WA cites chapters as "18.22" / "18.108" but reverse-index slugs are
    # dash-joined ("chapter-18-22"). The walker must normalize the dotted
    # cite token to the dash slug, else the cites never resolve.
    rules = StateScopeRules(
        universal_patterns=(),
        trigger_patterns=(re.compile(r"licensed\s+under\b", re.I),),
        chapter_cite_pattern=re.compile(r"\bchapter\s+(\d+\.\d+)\b", re.I),
        section_cite_pattern=re.compile(r"\b(\d+\.\d+)\.\d+\b", re.I),
    )
    reverse_index = {"chapter-18-22": ["podiatry"], "chapter-18-108": ["massage_therapy"]}
    text = (
        "As used in this chapter: a person licensed under chapter 18.22 or "
        "chapter 18.108 means a credential holder."
    )
    signals = _parse_one_anchor(text, rules, reverse_index)
    enum = [s for s in signals if s["kind"] == "enumerated"]
    assert enum, "expected an enumerated signal from the two dotted cites"
    assert set(enum[0]["professions"]) == {"podiatry", "massage_therapy"}


def test_parse_anchor_optional_group_does_not_crash():
    # An LLM-proposed cite pattern with an OPTIONAL group 1 can match with
    # group(1) == None — the walker must skip it, not crash on .lower() (NM).
    rules = StateScopeRules(
        universal_patterns=(),
        trigger_patterns=(re.compile(r"licensed\s+under\b", re.I),),
        chapter_cite_pattern=re.compile(r"\bchapter(?:\s+(\d+))?\b", re.I),  # optional group
        section_cite_pattern=re.compile(r"\b(\d+)\.\d+", re.I),
    )
    reverse_index = {"chapter-456": ["x"]}
    text = "licensed under chapter and also chapter 456."
    # Must not raise; the bare "chapter" (group 1 None) is skipped.
    signals = _parse_one_anchor(text, rules, reverse_index)
    assert isinstance(signals, list)


def test_parse_anchor_dash_cites_unaffected():
    # States that already use dash/letter tokens (UT "31b", FL "456") must be
    # unchanged by dot normalization.
    rules = StateScopeRules(
        universal_patterns=(),
        trigger_patterns=(re.compile(r"licensed\s+under\b", re.I),),
        chapter_cite_pattern=re.compile(r"\bchapter\s+(\d+[a-z]?)\b", re.I),
        section_cite_pattern=re.compile(r"\bsection\s+58-(\d+[a-z]?)-", re.I),
    )
    reverse_index = {"chapter-456": ["x"], "chapter-457": ["y"]}
    text = "licensed under chapter 456 or chapter 457."
    signals = _parse_one_anchor(text, rules, reverse_index)
    enum = [s for s in signals if s["kind"] == "enumerated"]
    assert enum and set(enum[0]["professions"]) == {"x", "y"}


# ---------------------------------------------------------------------------
# Golden: freeze scope_source_counts for the five validated states
# ---------------------------------------------------------------------------

GOLDEN_COUNTS = {
    "UT": {"anchor_universal": 3, "universal": 50, "inherited_enumeration": 14, "anchor_enumeration": 2},
    # FL Ch 455 sections (62) moved from undetermined → inherited_enumeration
    # via pipeline/config/state_scope/FL.yaml on 2026-05-28. Manifest applies
    # the DBPR-only enumeration (canonical FL trap — Ch 455 is DBPR-only, not
    # universal). FL --validate-fl still passes since the manifest fires
    # before Pass 3, so the LLM never touches Ch 455 sections.
    "FL": {"anchor_enumeration": 3, "inherited_enumeration": 160},
    # CO previously had 153 undetermined sections — all from Title 10 (Insurance
    # Code) Articles 1-2, which our profession taxonomy doesn't cover. They
    # were dropped via pipeline/config/state_scope/CO.yaml on 2026-05-28. The
    # rest of CO's classification is unchanged from the original golden.
    "CO": {"anchor_universal": 8, "universal": 23, "anchor_enumeration": 14, "inherited_enumeration": 20},
    "IA": {"anchor_enumeration": 2, "inherited_enumeration": 117, "anchor_universal": 1, "universal": 19},
    "WI": {"anchor_enumeration": 17, "inherited_enumeration": 182},  # 2026-07-02 uncapped umbrella re-pull
    "MO": {"inherited_enumeration": 170, "anchor_enumeration": 16},  # 2026-07-02 uncapped umbrella re-pull
    # Batch-applied 2026-05-27 from validated proposals (7 clean + 9 high-yield).
    "WV": {"anchor_universal": 4, "universal": 47, "undetermined": 1},
    "TN": {"inherited_enumeration": 106, "anchor_enumeration": 12},  # 2026-07-01: ch-1 uncapped 50->118 sections
    "NM": {"anchor_universal": 2, "universal": 43},
    "HI": {"anchor_universal": 3, "universal": 36, "inherited_enumeration": 4, "anchor_enumeration": 1},
    # Golden counts below were updated 2026-05-28 after adding per-state scope
    # manifests at pipeline/config/state_scope/<ST>.yaml. Each affected state's
    # universal count grew or undetermined count shrank because the manifest
    # marks cross-cutting chapters (criminal-background, military portability,
    # general provisions, occupational-licensing audit) as universal that the
    # walker regex didn't pick up. See feedback_state_scope_manifests.md.
    "GA": {"anchor_universal": 4, "universal": 41},                          # +5 univ (ch-2 audit), 0 undet
    "SC": {"universal": 29, "anchor_universal": 1},
    "ID": {"undetermined": 3, "anchor_enumeration": 1, "inherited_enumeration": 6, "anchor_universal": 2, "universal": 12},
    "TX": {"inherited_enumeration": 195, "anchor_universal": 14, "universal": 156},  # 2026-07-02 uncapped umbrella re-pull     # +80 enum (TX subtitle-a + ch-101 + ch-112 → health)
    "WA": {"inherited_enumeration": 72, "anchor_enumeration": 7, "universal": 21, "anchor_universal": 2},  # +45 enum (ch-18-130 health)
    "MD": {"anchor_universal": 7, "universal": 74},  # 2026-07-02 uncapped umbrella re-pull                           # +8 univ (title-2-5 military), 0 undet
    "OR": {"universal": 27, "inherited_enumeration": 131, "anchor_enumeration": 11},  # 2026-07-02 uncapped umbrella re-pull  # +25 univ (ch-670 generally), 0 undet
    "IN": {"universal": 345, "inherited_enumeration": 353, "anchor_enumeration": 15},  # 2026-07-01: article-0.5+1 uncapped 100->715 sections
    "MT": {"universal": 70, "anchor_universal": 6, "inherited_enumeration": 42},  # 2026-07-01: ch-1 uncapped 50->76 sections
    "CT": {"universal": 63, "anchor_universal": 3},                           # +25 univ (ch-141 + 414b), 0 undet
    "NV": {"anchor_universal": 2, "universal": 37, "inherited_enumeration": 70},  # 2026-07-02 uncapped umbrella re-pull  # -27 undet (622a drop) +50 enum (ch-629 health)
    "SD": {"universal": 45, "anchor_universal": 3, "inherited_enumeration": 26, "undetermined": 10},  # 2026-07-01: uncapped; ch-26b (10 sec) undetermined — needs manifest scope decision (U2)
}


@pytest.mark.parametrize("state,expected", GOLDEN_COUNTS.items())
def test_golden_scope_source_counts(state, expected):
    if not (UMBRELLA_TEXT_DIR / f"{state}.json").exists():
        pytest.skip(f"no committed umbrella_text for {state}")
    result = assign_for_state(state)
    assert result["scope_source_counts"] == expected


def test_skeleton_all_undetermined_drops_landing_pages(tmp_path, monkeypatch):
    import pipeline.scope.assign_umbrella_scope as W
    monkeypatch.setattr(W, "UMBRELLA_TEXT_DIR", tmp_path)
    (tmp_path / "ZZ.json").write_text(json.dumps({"sections": [
        {"url": "https://x/codes/zz/title-1/chapter-1/section-1-1/", "label": "Definitions",
         "umbrella_chapter_slug": "chapter-1", "text": "t"},
        {"url": "https://x/codes/zz/title-1/chapter-1/statute-1-2/", "label": "Scope",
         "umbrella_chapter_slug": "chapter-1", "text": "t"},
        {"url": "https://x/codes/zz/title-1/chapter-1/", "label": "2025 Code",  # landing page
         "umbrella_chapter_slug": "chapter-1", "text": "t"},
    ]}))
    r = W.skeleton_for_state("ZZ")
    # landing page dropped (leaf 'chapter-1' isn't a section); 2 real sections kept
    assert r["scope_source_counts"] == {"undetermined": 2}
    assert all(s["scope_source"] == "undetermined" for s in r["sections"])
    assert {s["url"].rstrip("/").split("/")[-1] for s in r["sections"]} == {"section-1-1", "statute-1-2"}


def test_skeleton_empty_when_no_sections(tmp_path, monkeypatch):
    import pipeline.scope.assign_umbrella_scope as W
    monkeypatch.setattr(W, "UMBRELLA_TEXT_DIR", tmp_path)
    (tmp_path / "ZZ.json").write_text(json.dumps({"sections": [
        {"url": "https://x/codes/zz/title-1/chapter-1/", "label": "2025 Code",
         "umbrella_chapter_slug": "chapter-1", "text": "t"},  # only a landing page
    ]}))
    r = W.skeleton_for_state("ZZ")
    assert r["section_count"] == 0 and r["scope_source_counts"] == {}


def test_fl_chapter_455_never_universal():
    """§ 455.017 is DBPR-scoped, NOT universal. chapter-455 must never carry
    a universal/anchor_universal scope_source — the FL trap that regressed
    in commit b61e800. The valid classifications are:
      - undetermined        (walker default before any manifest)
      - inherited_enumeration with DBPR-only applies_to (manifest path)
    Universal would over-attribute the chapter to DOH health professions
    (medicine, nursing, etc.) which Ch 455 doesn't govern.
    """
    if not (UMBRELLA_TEXT_DIR / "FL.json").exists():
        pytest.skip("no committed umbrella_text for FL")
    result = assign_for_state("FL")
    sources_455 = [
        s["scope_source"] for s in result["sections"]
        if s["umbrella_chapter_slug"] == "chapter-455"
    ]
    assert sources_455, "expected chapter-455 sections in FL umbrella_text"
    assert all(src not in ("universal", "anchor_universal") for src in sources_455), \
        "Ch 455 cannot be classified as universal — it's DBPR-only"
