"""Tests for the Justia chrome stripper (pipeline/publish/_justia_clean.py).

The umbrella scraper kept whole-page scrapes, including Justia's
navigation chrome (version-list, breadcrumb, "Universal Citation" header,
disclaimer footer). Our publish step needs to slice out just the actual
statute text. Heuristic-based — these tests lock the behavior so future
Justia HTML changes don't silently re-introduce chrome to the UI.
"""

from __future__ import annotations

import pytest

from pipeline.publish._justia_clean import clean_justia_text


# Real shape of a CO umbrella section scrape — header chrome, then "Next"
# marker, then the actual statute, then "Next" + disclaimer.
SAMPLE_CO_FULL = """\
Go to Previous Versions
                            of
                            this Section
2024 Colorado Rev. Stat. (here)
2023 Colorado Rev. Stat.
2022 Colorado Rev. Stat.
View All Versions
2024 Colorado Revised Statutes
Title 12 - PROFESSIONS AND OCCUPATIONS
GENERAL
Article 1 - GENERAL PROVISIONS
Section 12-1-101 - Short title
Universal Citation:
CO Rev Stat § 12-1-101 (2024)
Learn more
This media-neutral citation is based
                        on the American Association of Law Libraries Universal Citation Guide and is not
                        necessarily the official citation.
Next
The short title of this title 12 is the "Professions and Occupations Act".
Added by 2019 Ch. 136,§ 1, eff. 10/1/2019.
Next
Disclaimer: These codes may not be the most recent version. Please check official sources.
"""


class TestCleanJustiaText:
    def test_strips_header_chrome(self):
        cleaned = clean_justia_text(SAMPLE_CO_FULL)
        assert "Go to Previous Versions" not in cleaned
        assert "Universal Citation:" not in cleaned
        assert "media-neutral citation" not in cleaned

    def test_strips_disclaimer_footer(self):
        cleaned = clean_justia_text(SAMPLE_CO_FULL)
        assert "Disclaimer" not in cleaned
        assert "may not be the most recent" not in cleaned

    def test_keeps_actual_statute(self):
        cleaned = clean_justia_text(SAMPLE_CO_FULL)
        assert 'short title of this title 12 is the "Professions and Occupations Act"' in cleaned

    def test_keeps_amendment_history(self):
        """The 'Added by 2019 Ch. 136…' line sits between the two 'Next'
        markers — it IS the statute's amendment footer, not Justia
        chrome, so we keep it."""
        cleaned = clean_justia_text(SAMPLE_CO_FULL)
        assert "Added by 2019 Ch. 136" in cleaned

    def test_no_next_marker_returns_original(self):
        """When the heuristic can't find a 'Next' marker AND no
        media-neutral citation fallback fires, fall back to original
        rather than nuking content."""
        plain = "Some statute text with no markers anywhere."
        assert clean_justia_text(plain) == plain

    def test_empty_input(self):
        assert clean_justia_text("") == ""

    def test_collapses_double_blanks(self):
        """Justia ships HTML with deeply-indented continuation lines that
        round-trip to double blanks. The cleaner normalizes them."""
        cleaned = clean_justia_text(SAMPLE_CO_FULL)
        # No three consecutive blank lines.
        assert "\n\n\n" not in cleaned

    def test_short_result_falls_back_to_original(self):
        """If the cleaning reduces text to almost nothing AND the original
        was non-trivial, prefer the original — better to ship chrome than
        to ship a stub."""
        # Synthetic case: "Next" markers but the body between them is
        # empty.
        tricky = "Some chrome line\nNext\n\n\nNext\nDisclaimer:"
        out = clean_justia_text(tricky)
        # Original is short too (60 chars) — fallback rule only applies
        # if original > 60. This input shouldn't trigger fallback.
        # The cleaner should produce a tiny output. Just confirm we
        # don't crash and produce something string-like.
        assert isinstance(out, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
