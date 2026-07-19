"""clean_text.clean_justia must strip Justia's annotation apparatus + version-nav.

Colorado's (and New Mexico's) Justia section pages append an editorial apparatus
after the statute — case-law ANNOTATIONS, "Research References & Practice Aids",
a "Hierarchy Notes:" breadcrumb, "State Notes" — and Colorado's pages carry a
"Go to Other Versions … View All Versions" year-list nav. None of it is statute.
Regressed 2026-07-18 when a CO re-pull injected this chrome into the raw corpus and
clean_text (which had no pattern for it) let it reach extraction. These lock the fix.
"""

from __future__ import annotations

from pipeline.ingest.clean_text import clean_justia


# A real-shape Colorado section: statute, a Source history line, then the apparatus.
CO_CHROME = """\
The purpose of this article 105 is to protect the public's health, safety, and welfare.
History
Source: L. 2019: Entire title R&RE with relocations,(HB 19-1172), ch. 136, p. 819, § 1, effective October 1.
Annotations
Research References & Practice Aids
Hierarchy Notes:
C.R.S. Title 12
C.R.S. Title 12, Art. 105
State Notes
Notes
Editor's note:
This section is similar to former § 12-8-102 as it existed prior to 2019.
ANNOTATION
Constitutional regulation.
That barber and beauty shops can constitutionally be regulated is not questioned. People v. Taylor, 189 Colo. 202, 540 P.2d 320 (1975)."""

# New Mexico uses the all-caps "ANNOTATIONS" header for the same apparatus.
NM_CHROME = """\
The board shall adopt rules. Laws 1979, ch. 362, § 5; 1987, ch. 282, § 7; 2017, ch. 107, § 3.
ANNOTATIONS
Cross references.
— For registration fee, see 61-15-4E NMSA 1978."""


class TestAnnotationApparatus:
    def test_strips_co_apparatus_keeps_statute_and_source(self):
        out = clean_justia(CO_CHROME)
        assert out.startswith("The purpose of this article 105")
        assert "Source: L. 2019" in out          # legislative source line kept
        for chrome in ("Annotations", "Research References & Practice Aids",
                       "Hierarchy Notes", "State Notes", "ANNOTATION", "People v. Taylor"):
            assert chrome not in out, chrome

    def test_strips_nm_all_caps_apparatus(self):
        out = clean_justia(NM_CHROME)
        assert out.startswith("The board shall adopt rules")
        assert "Laws 1979" in out                # history kept
        assert "ANNOTATIONS" not in out
        assert "Cross references" not in out

    def test_go_to_other_versions_nav_stripped(self):
        text = ("Go to Other Versions of The Colorado Rev. Stat.\n"
                "2025 Colorado Rev. Stat.\n2024 Colorado Rev. Stat.\n"
                "View All Versions\nThe operative statute text is here.")
        out = clean_justia(text)
        assert "Go to Other Versions" not in out
        assert "2025 Colorado Rev. Stat." not in out
        assert "The operative statute text is here." in out

    def test_lowercase_annotation_in_prose_is_not_truncated(self):
        # The markers are title-case/all-caps on their own line; a lowercase mention
        # of "annotation" mid-sentence must NOT trigger truncation.
        text = "The registry annotation shall be maintained by the board at all times."
        assert clean_justia(text) == text

    def test_plain_statute_unchanged(self):
        text = "A person shall not practice cosmetology without a license issued under this article."
        assert clean_justia(text) == text
