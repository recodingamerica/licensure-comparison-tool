"""Tests for collect_section_targets depth handling (Change 1).

Two scenarios:
  A) 3-deep nesting fully collected with default max_depth=6 (would have been
     cut at the old max_depth=2, returning nothing from the third level).
  B) depth_capped signal fires when nesting exceeds a test-lowered max_depth,
     the collected sections so far are still returned, and a WARNING is logged.

We mock extract_child_links and fetch directly (not the HTML parser) to avoid
coupling the tests to URL-path-filter internals.
"""

from __future__ import annotations

import pytest

import pipeline.ingest.pull_text as pt
from pipeline.ingest.pull_text import collect_section_targets

# ─── helpers ─────────────────────────────────────────────────────────────────

BASE = "https://law.justia.com/codes/teststate/title-99/chapter-10/"
SUB1 = f"{BASE}subchapter-1/"
SUB2 = f"{SUB1}subpart-1/"
SEC1 = f"{SUB2}section-99-1/"
SEC2 = f"{SUB2}section-99-2/"

SUBCHAP1 = {"url": SUB1, "label": "Subchapter 1", "slug": "subchapter-1"}
SUBPART1 = {"url": SUB2, "label": "Subpart 1", "slug": "subpart-1"}
SECTION1 = {"url": SEC1, "label": "Section 99-1", "slug": "section-99-1"}
SECTION2 = {"url": SEC2, "label": "Section 99-2", "slug": "section-99-2"}


def _noop_fetch(url):
    return 200, "<html/>", None


def _noop_sleep():
    pass


def _child_link_map(mapping: dict):
    """Return a fake extract_child_links that uses url→(sections, intermediates) mapping."""
    def fake(html, url):
        return mapping.get(url, ([], []))
    return fake


# ─── Test A: 3-deep nesting fully collected ──────────────────────────────────

class TestDeepNestingFullyCollected:
    """A chapter→subchapter→subpart→sections tree (3 recursive hops) must be
    fully collected with max_depth=6 (the new default).

    Under the old default of max_depth=2:
      depth 0 → intermediates=[subchapter-1]          → recurse (depth 0 < 2)
      depth 1 → intermediates=[subpart-1]             → recurse (depth 1 < 2)
      depth 2 → intermediates=[subpart-1 child]       → STOP (depth 2 >= 2)
    Result: depth_capped, zero sections.

    With max_depth=6 the walk continues to depth 2 where leaves are found."""

    def test_three_deep_returns_all_sections(self, monkeypatch):
        mapping = {
            BASE:  ([], [SUBCHAP1]),      # depth 0: one intermediate
            SUB1:  ([], [SUBPART1]),      # depth 1: one deeper intermediate
            SUB2:  ([SECTION1, SECTION2], []),  # depth 2: two leaf sections
        }
        monkeypatch.setattr(pt, "fetch", _noop_fetch)
        monkeypatch.setattr(pt, "polite_sleep", _noop_sleep)
        monkeypatch.setattr(pt, "extract_child_links", _child_link_map(mapping))

        sections, err = collect_section_targets(
            BASE, "Chapter 10", "chapter-10", depth=0, max_depth=6
        )
        assert err is None
        slugs = {s["slug"] for s in sections}
        assert slugs == {"section-99-1", "section-99-2"}

    def test_old_depth2_cap_would_have_missed_sections(self, monkeypatch):
        """With max_depth=2, depth=2 still has intermediates → depth_capped fired."""
        # At depth 2 we return another intermediate, not leaf sections
        deeper_inter = {"url": f"{SUB2}subsubpart/", "label": "Subsubpart", "slug": "subpart-2"}
        mapping = {
            BASE:  ([], [SUBCHAP1]),
            SUB1:  ([], [SUBPART1]),
            SUB2:  ([], [deeper_inter]),  # depth 2 still has intermediates → cap
        }
        monkeypatch.setattr(pt, "fetch", _noop_fetch)
        monkeypatch.setattr(pt, "polite_sleep", _noop_sleep)
        monkeypatch.setattr(pt, "extract_child_links", _child_link_map(mapping))

        sections, err = collect_section_targets(
            BASE, "Chapter 10", "chapter-10", depth=0, max_depth=2
        )
        assert err is not None
        assert "depth_capped" in err
        assert sections == []


# ─── Test B: depth_capped signal properties ──────────────────────────────────

class TestDepthCappedSignal:
    """When nesting exceeds max_depth the function must return a non-None error
    string containing 'depth_capped', emit a WARNING, and not lose sections
    already collected from sibling branches that resolved successfully."""

    def test_error_string_contains_depth_capped(self, monkeypatch):
        # depth 0 → intermediate, depth 1 >= max_depth=1 still has intermediate → cap
        mapping = {
            BASE:  ([], [SUBCHAP1]),
            SUB1:  ([], [SUBPART1]),
        }
        monkeypatch.setattr(pt, "fetch", _noop_fetch)
        monkeypatch.setattr(pt, "polite_sleep", _noop_sleep)
        monkeypatch.setattr(pt, "extract_child_links", _child_link_map(mapping))

        _, err = collect_section_targets(
            BASE, "Chapter 10", "chapter-10", depth=0, max_depth=1
        )
        assert err is not None
        assert "depth_capped" in err

    def test_warning_logged_on_cap(self, monkeypatch, caplog):
        mapping = {
            BASE:  ([], [SUBCHAP1]),
            SUB1:  ([], [SUBPART1]),
        }
        monkeypatch.setattr(pt, "fetch", _noop_fetch)
        monkeypatch.setattr(pt, "polite_sleep", _noop_sleep)
        monkeypatch.setattr(pt, "extract_child_links", _child_link_map(mapping))

        with caplog.at_level("WARNING", logger="pull_text"):
            collect_section_targets(
                BASE, "Chapter 10", "chapter-10", depth=0, max_depth=1
            )

        assert any("depth_capped" in r.message for r in caplog.records)

    def test_sections_from_good_branch_returned_when_sibling_is_capped(self, monkeypatch):
        """If branch A yields leaf sections and sibling branch B hits the depth cap,
        the sections from branch A must still be returned.

        Tree (max_depth=2):
          depth 0 → [subchapter-1, subchapter-2]
          subchapter-1 (depth 1) → [section-99-1]        ← resolved
          subchapter-2 (depth 1) → [subpart-1]           ← intermediate
            subpart-1   (depth 2) → [sub-subpart-x]      ← depth_capped
        """
        sub2 = {"url": f"{BASE}subchapter-2/", "label": "Subchapter 2", "slug": "subchapter-2"}
        sub2_inter = {"url": f"{BASE}subchapter-2/subpart-1/", "label": "Subpart 1", "slug": "subpart-1"}
        sub2_deeper = {"url": f"{BASE}subchapter-2/subpart-1/sub-subpart-x/",
                       "label": "Sub-Subpart X", "slug": "sub-subpart-x"}
        mapping = {
            BASE:                   ([], [SUBCHAP1, sub2]),
            SUB1:                   ([SECTION1], []),          # branch A: has leaves
            sub2["url"]:            ([], [sub2_inter]),        # branch B: intermediate
            sub2_inter["url"]:      ([], [sub2_deeper]),       # depth 2: still intermediate → cap
        }
        monkeypatch.setattr(pt, "fetch", _noop_fetch)
        monkeypatch.setattr(pt, "polite_sleep", _noop_sleep)
        monkeypatch.setattr(pt, "extract_child_links", _child_link_map(mapping))

        sections, err = collect_section_targets(
            BASE, "Chapter 10", "chapter-10", depth=0, max_depth=2
        )
        # Branch A's section must survive even though branch B was capped
        slugs = {s["slug"] for s in sections}
        assert "section-99-1" in slugs, f"Expected section-99-1 in {slugs}"


# ─── Test C: config wires the default ────────────────────────────────────────

class TestDefaultMaxDepthFromLimits:
    """The module-level SECTION_WALK_MAX_DEPTH should equal 6 from limits.yaml
    and be used as the default argument for collect_section_targets."""

    def test_limits_yaml_value_is_six(self):
        from pipeline.config.loaders import load_limits
        assert load_limits()["pull"]["section_walk_max_depth"] == 6

    def test_module_constant_is_six(self):
        assert pt.SECTION_WALK_MAX_DEPTH == 6
