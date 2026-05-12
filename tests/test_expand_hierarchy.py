"""Tests for pipeline.discover.expand_hierarchy subtitle detection.

The drill-recursion was buggy through two iterations: first it false-matched
"Chapter 161 -" as a subtitle (label regex too greedy), then it drilled mixed
entry lists indiscriminately. The current version partitions entries by
slug pattern, drills only the subtitle-shaped ones, and pass-through chapters.
Lock in both rules.
"""

import pytest

from pipeline.discover.expand_hierarchy import (
    _SUBTITLE_SLUG_RE,
    _looks_like_subtitle_layer,
    _drill_recursively,
)


def _entry(slug: str, label: str = "") -> dict:
    return {"slug": slug, "label": label or slug, "url": f"https://x/{slug}/"}


class TestSubtitleSlugRegex:
    @pytest.mark.parametrize("slug", [
        "title-1", "title-iv", "title-3-1",
        "subtitle-a", "subtitle-b",
        "division-1", "division-1-1",
        "part-3", "part-3-5",
        "volume-06",
        "subdivision-2",
    ])
    def test_subtitle_shaped_slugs_match(self, slug):
        assert _SUBTITLE_SLUG_RE.match(slug)

    @pytest.mark.parametrize("slug", [
        "chapter-901", "chapter-90", "chapter-161",  # real TX/NC chapters
        "article-28b",                                # NM article
        "section-32-801",                             # AZ section_fallback
        "rs-37-611",                                  # LA section
    ])
    def test_chapter_shaped_slugs_dont_match(self, slug):
        assert not _SUBTITLE_SLUG_RE.match(slug)


class TestLooksLikeSubtitleLayer:
    def test_empty_is_false(self):
        assert not _looks_like_subtitle_layer([])

    def test_all_subtitles_is_true(self):
        entries = [_entry(f"title-{i}") for i in range(1, 6)]
        assert _looks_like_subtitle_layer(entries)

    def test_all_chapters_is_false(self):
        entries = [_entry(f"chapter-{i}") for i in (90, 91, 92, 93, 94)]
        assert not _looks_like_subtitle_layer(entries)

    def test_majority_subtitles_is_true(self):
        # 3 subtitles + 1 chapter — majority
        entries = [_entry("title-1"), _entry("title-2"), _entry("title-3"), _entry("chapter-99")]
        assert _looks_like_subtitle_layer(entries)

    def test_minority_subtitles_is_false(self):
        # 1 subtitle + 3 chapters — not majority
        entries = [_entry("title-1"), _entry("chapter-90"), _entry("chapter-91"), _entry("chapter-92")]
        assert not _looks_like_subtitle_layer(entries)

    def test_does_not_match_on_label_text(self):
        # Regression: previously the label regex caught "Chapter 161 -" and
        # caused infinite drilling on real chapters
        entries = [_entry(f"chapter-{i}", f"Chapter {i} - Whatever") for i in range(161, 166)]
        assert not _looks_like_subtitle_layer(entries)


class TestDrillRecursivelyPartition:
    """Recursion must partition: drill subtitles, keep chapters as-is."""

    def test_pure_chapters_returns_unchanged(self):
        entries = [_entry("chapter-90"), _entry("chapter-91")]
        out = _drill_recursively(entries, depth=0)
        assert out == entries  # no drill happened, identity

    def test_max_depth_cap(self, monkeypatch):
        """Should bail before infinite recursion if subtitles keep regenerating."""
        from pipeline.discover import expand_hierarchy as eh
        call_count = {"n": 0}

        def fake_drill_one(parent):
            call_count["n"] += 1
            return [_entry(f"subtitle-x{call_count['n']}")]

        monkeypatch.setattr(eh, "_drill_one", fake_drill_one)
        entries = [_entry("title-1")]
        _drill_recursively(entries, depth=0, max_depth=3)
        # Should stop at max_depth — would otherwise infinite loop
        assert call_count["n"] <= 5  # small bound; not infinite

    def test_leaf_subtitle_kept_as_chapter(self, monkeypatch):
        """MD bug: title-2 → subtitle-1..7 → (sections, no chapters). The
        subtitles should be retained as chapters, not silently dropped."""
        from pipeline.discover import expand_hierarchy as eh

        def fake_drill_one(parent):
            # Every drill returns nothing — this is what happens at the
            # subtitle-as-section-container leaf level on MD/etc.
            return []

        monkeypatch.setattr(eh, "_drill_one", fake_drill_one)
        entries = [_entry("subtitle-1"), _entry("subtitle-2")]
        out = _drill_recursively(entries, depth=0)
        # Both subtitles should be preserved as chapters (not lost)
        slugs = {e["slug"] for e in out}
        assert slugs == {"subtitle-1", "subtitle-2"}

    def test_parent_titles_kept_after_drilling(self, monkeypatch):
        """MD scenario: 'Title 2 - Accountants' has subtitle children. The
        title-2 entry must survive so its label is available for matching,
        AND the subtitle children should also be present."""
        from pipeline.discover import expand_hierarchy as eh

        def fake_drill_one(parent):
            if parent["slug"] == "title-2":
                return [_entry("subtitle-1", "Subtitle 1 - Defs"),
                        _entry("subtitle-2", "Subtitle 2 - Board")]
            return []

        monkeypatch.setattr(eh, "_drill_one", fake_drill_one)
        entries = [_entry("title-2", "Title 2 - Accountants")]
        out = _drill_recursively(entries, depth=0)
        slugs = {e["slug"] for e in out}
        # title-2 stays (label has 'Accountants'), AND subtitles are pulled in
        assert "title-2" in slugs
        assert "subtitle-1" in slugs
        assert "subtitle-2" in slugs
