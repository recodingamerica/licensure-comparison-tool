"""Tests for the browse-tree builder + helpers (pipeline/publish/_browse_tree.py).

The browse view's left-pane hierarchy is derived from each section's
Justia URL. Justia's path structure varies by state (CO uses /article-/,
UT uses /chapter-/, AZ uses /title-/chapter-/section-/, CA inserts
year prefixes, etc.) and the build_tree function has to handle the lot
correctly without losing or duplicating sections. These tests lock the
shape so a future URL-format change in one state can't silently break
the others.
"""

from __future__ import annotations

import pytest

from pipeline.publish._browse_tree import (
    build_tree,
    normalize_section_label,
    parse_hierarchy,
)


# ─── parse_hierarchy ─────────────────────────────────────────────────────

class TestParseHierarchy:
    def test_co_section_with_article_and_part(self):
        url = "https://law.justia.com/codes/colorado/title-12/article-290/part-1/section-12-290-101/"
        assert parse_hierarchy(url) == [
            ("title", "title-12"),
            ("article", "article-290"),
            ("part", "part-1"),
            ("section", "section-12-290-101"),
        ]

    def test_ut_section_uses_chapter(self):
        url = "https://law.justia.com/codes/utah/title-58/chapter-1/section-58-1-101/"
        assert parse_hierarchy(url) == [
            ("title", "title-58"),
            ("chapter", "chapter-1"),
            ("section", "section-58-1-101"),
        ]

    def test_az_section_chapter_no_part(self):
        url = "https://law.justia.com/codes/arizona/title-32/chapter-19/section-32-851/"
        assert parse_hierarchy(url) == [
            ("title", "title-32"),
            ("chapter", "chapter-19"),
            ("section", "section-32-851"),
        ]

    def test_year_prefix_skipped(self):
        """CA URLs sometimes carry a year between codes/ and title-."""
        url = "https://law.justia.com/codes/colorado/2023/title-12/article-1/section-12-1-101/"
        assert parse_hierarchy(url) == [
            ("title", "title-12"),
            ("article", "article-1"),
            ("section", "section-12-1-101"),
        ]

    def test_intermediate_general_skipped(self):
        """Some CO URLs have a 'general' segment that isn't a hierarchy level."""
        url = "https://law.justia.com/codes/colorado/title-12/general/article-1/section-12-1-101/"
        assert parse_hierarchy(url) == [
            ("title", "title-12"),
            ("article", "article-1"),
            ("section", "section-12-1-101"),
        ]

    def test_chapter_index_no_section(self):
        """URLs that end at chapter level (no section-X) parse with no section leaf."""
        url = "https://law.justia.com/codes/california/code-bpc/division-2/chapter-4/"
        path = parse_hierarchy(url)
        # No "title-" or "section-" — only "chapter-" is recognized.
        assert ("chapter", "chapter-4") in path
        assert not any(level == "section" for level, _ in path)

    def test_empty_url(self):
        assert parse_hierarchy("") == []

    def test_unrecognized_url(self):
        assert parse_hierarchy("https://example.com/foo/bar") == []


# ─── normalize_section_label ─────────────────────────────────────────────

class TestNormalizeSectionLabel:
    def test_strips_section_prefix(self):
        assert normalize_section_label("Section 1600.") == "§ 1600"

    def test_strips_lowercase_section_prefix(self):
        assert normalize_section_label("section 1600.") == "§ 1600"

    def test_keeps_decimal_subsection(self):
        assert normalize_section_label("Section 1601.1") == "§ 1601.1"

    def test_naked_number_gets_section_sign(self):
        assert normalize_section_label("1601.1") == "§ 1601.1"

    def test_preserves_descriptive_tail(self):
        assert normalize_section_label("Section 1600. Composition of board") == \
            "§ 1600 — Composition of board"

    def test_dashed_identifier(self):
        assert normalize_section_label("Section 32-851") == "§ 32-851"

    def test_non_numeric_leaves_as_is(self):
        # No numeric identifier — fall back to bare label.
        assert normalize_section_label("Definitions") == "Definitions"

    def test_empty(self):
        assert normalize_section_label("") == ""


# ─── build_tree ──────────────────────────────────────────────────────────

def _sec(url: str, citation: str = "", label: str = "", text: str = "stub") -> dict:
    """Test helper — minimal section shape build_tree consumes."""
    return {"url": url, "citation": citation, "label": label, "text": text}


class TestBuildTree:
    def test_single_section_builds_one_path(self):
        forest = build_tree([
            _sec(
                "https://law.justia.com/codes/colorado/title-12/article-1/section-12-1-101/",
                citation="12-1-101",
                label="Section 12-1-101 - Short title",
            ),
        ])
        assert len(forest) == 1
        title = forest[0]
        assert title["level"] == "title"
        assert title["slug"] == "title-12"
        assert len(title["children"]) == 1
        article = title["children"][0]
        assert article["level"] == "article"
        assert article["slug"] == "article-1"
        assert len(article["children"]) == 1
        section = article["children"][0]
        assert section["level"] == "section"
        # Label is normalized.
        assert section["label"].startswith("§ 12-1-101")

    def test_siblings_under_same_branch(self):
        forest = build_tree([
            _sec("https://law.justia.com/codes/colorado/title-12/article-1/section-12-1-101/"),
            _sec("https://law.justia.com/codes/colorado/title-12/article-1/section-12-1-102/"),
        ])
        assert len(forest) == 1
        article = forest[0]["children"][0]
        assert {c["slug"] for c in article["children"]} == {
            "section-12-1-101", "section-12-1-102",
        }

    def test_year_prefixed_duplicates_collapse(self):
        """Same section reached via 2022/, 2023/, no-prefix URLs — one leaf."""
        forest = build_tree([
            _sec("https://law.justia.com/codes/colorado/2022/title-12/article-1/section-12-1-101/"),
            _sec("https://law.justia.com/codes/colorado/2023/title-12/article-1/section-12-1-101/"),
            _sec("https://law.justia.com/codes/colorado/title-12/article-1/section-12-1-101/"),
        ])
        leaves = forest[0]["children"][0]["children"]
        assert len(leaves) == 1
        assert leaves[0]["slug"] == "section-12-1-101"

    def test_chapter_index_pages_skipped(self):
        """URLs that don't resolve to a section level are filtered out.
        Without this, "2025 California Code" leaves the chapter TOC page
        appears as a fake section in the tree."""
        forest = build_tree([
            _sec("https://law.justia.com/codes/california/code-bpc/division-2/chapter-4/",
                 citation="2025 California Code",
                 label="2025 California Code"),
            _sec("https://law.justia.com/codes/california/code-bpc/division-2/chapter-4/article-1/section-1600/"),
        ])
        # Only the real section makes it in.
        def leaves(nodes):
            out = []
            for n in nodes:
                if n["level"] == "section":
                    out.append(n)
                else:
                    out.extend(leaves(n["children"]))
            return out
        all_leaves = leaves(forest)
        assert len(all_leaves) == 1
        assert "section-1600" in all_leaves[0]["slug"]

    def test_chapter_label_override_applied(self):
        """Umbrella chapter labels from professions.yaml's umbrella_chapter_label
        override the slug-derived defaults."""
        forest = build_tree(
            [_sec("https://law.justia.com/codes/colorado/title-12/article-1/section-12-1-101/")],
            chapter_label_overrides={"article-1": "Article 1 - GENERAL PROVISIONS"},
        )
        article = forest[0]["children"][0]
        assert article["label"] == "Article 1 - GENERAL PROVISIONS"

    def test_section_carries_its_payload(self):
        """The leaf node has a `section` field pointing back to the input dict
        so the frontend detail pane can render text/evidence/etc."""
        sec_in = _sec(
            "https://law.justia.com/codes/colorado/title-12/article-1/section-12-1-101/",
            citation="12-1-101",
            text="The short title…",
        )
        forest = build_tree([sec_in])
        leaf = forest[0]["children"][0]["children"][0]
        assert leaf["section"] is sec_in

    def test_empty_input(self):
        assert build_tree([]) == []

    def test_children_sorted(self):
        """Within a parent, children come back in stable slug order."""
        forest = build_tree([
            _sec("https://law.justia.com/codes/colorado/title-12/article-3/section-12-3-101/"),
            _sec("https://law.justia.com/codes/colorado/title-12/article-1/section-12-1-101/"),
            _sec("https://law.justia.com/codes/colorado/title-12/article-2/section-12-2-101/"),
        ])
        title = forest[0]
        assert [c["slug"] for c in title["children"]] == [
            "article-1", "article-2", "article-3",
        ]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
