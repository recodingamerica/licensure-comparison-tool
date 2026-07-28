"""Section citations must be UNIQUE, because the UI resolves a section by citation.

`sections[citation] = s` in a loop means LAST wins. DE ships the current and the
contingent version of § 1101 (and §§ 1105, 1106, 1121) as two sections with different
text, so whichever copy lost that race became unreachable and every quote living in it
silently stopped highlighting -- 82% of dentistry's unlocatable-but-verified quotes.

It read like the model had paraphrased. It hadn't: the text was verbatim law in the copy
we discarded. We caused the collision by normalizing away the `[Effective until ...]`
tail, which was the only thing telling the copies apart.
"""

from __future__ import annotations

from pipeline.publish.build_frontend import dedupe_section_citations


def test_colliding_citations_are_made_unique_from_the_raw_form():
    sections = [
        {"citation": "§ 1101", "_citation_raw": "§ 1101. Definitions [Effective until fullfilment]",
         "text": "current text"},
        {"citation": "§ 1101", "_citation_raw": "§ 1101. Definitions [Effective upon fullfilment]",
         "text": "contingent text"},
    ]
    assert dedupe_section_citations(sections) == 1
    cites = [s["citation"] for s in sections]
    assert cites[0] == "§ 1101", "the first copy keeps the plain citation evidence will cite"
    assert cites[1] != "§ 1101"
    assert len(set(cites)) == 2


def test_unique_citations_are_left_completely_alone():
    sections = [{"citation": "§ 1101", "text": "a"}, {"citation": "§ 1102", "text": "b"}]
    assert dedupe_section_citations(sections) == 0
    assert [s["citation"] for s in sections] == ["§ 1101", "§ 1102"]


def test_falls_back_to_an_index_when_nothing_distinguishes_them():
    """No raw form and no label -- still must not leave two sections sharing a key."""
    sections = [{"citation": "50-6", "text": "a"}, {"citation": "50-6", "text": "b"}]
    assert dedupe_section_citations(sections) == 1
    assert len({s["citation"] for s in sections}) == 2


def test_three_way_collision_all_become_distinct():
    sections = [
        {"citation": "§ 7", "text": "a"},
        {"citation": "§ 7", "text": "b"},
        {"citation": "§ 7", "text": "c"},
    ]
    assert dedupe_section_citations(sections) == 2
    assert len({s["citation"] for s in sections}) == 3


def test_blank_citations_are_not_treated_as_colliding():
    """Unlabelled sections share the empty string; that is not a collision to fix here."""
    sections = [{"citation": "", "text": "a"}, {"citation": "", "text": "b"}]
    assert dedupe_section_citations(sections) == 0


def test_label_is_used_when_no_raw_citation_was_recorded():
    sections = [
        {"citation": "§ 1105", "label": "§ 1105 Board powers", "text": "a"},
        {"citation": "§ 1105", "label": "§ 1105 Board powers [Effective upon contingency]",
         "text": "b"},
    ]
    assert dedupe_section_citations(sections) == 1
    assert "Effective upon contingency" in sections[1]["citation"]
