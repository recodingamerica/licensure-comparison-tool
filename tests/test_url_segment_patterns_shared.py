"""The Justia URL-segment classifiers have ONE definition, imported everywhere.

Each of these was a hand-copied duplicate that drifted (discover._extract's SECTION_SEG
was missing the canonical `\\d{3,}` branch, so a bare 3-digit section segment was a
section to the walker but not to the hierarchy builder). Pin identity so a future copy
re-introduces a test failure, not a silent divergence.
"""

from pipeline.ingest import _section_patterns as sp
from pipeline.discover import _extract
from pipeline.ingest import pull_text
from pipeline.eval import audit_mappings


def test_section_seg_is_the_shared_object_everywhere():
    assert _extract.SECTION_SEG is sp.SECTION_SEG
    assert pull_text.SECTION_SEG is sp.SECTION_SEG


def test_intermediate_seg_is_the_shared_object_everywhere():
    assert _extract.INTERMEDIATE_SEG is sp.INTERMEDIATE_SEG
    assert pull_text.INTERMEDIATE_SEG is sp.INTERMEDIATE_SEG


def test_bare_three_digit_segment_classifies_as_a_section():
    # The branch discover._extract used to lack — the whole point of the drift fix.
    assert sp.SECTION_SEG.match("311")           # the branch _extract lacked
    assert sp.SECTION_SEG.match("42a-1")         # \d+[a-z]?[-:.]\d form
    assert not sp.SECTION_SEG.match("chapter-5")


def test_is_title_root_shared_by_narrow_and_repair():
    from pipeline.discover.gap_harvest import narrow
    from pipeline.discover import repair_nj_mappings  # noqa: F401 — imports is_title_root
    assert sp.is_title_root("https://law.justia.com/codes/utah/title-58/")
    assert sp.is_title_root("https://law.justia.com/codes/utah/title-58a.5/")   # odd slug
    assert not sp.is_title_root("https://law.justia.com/codes/utah/title-58/chapter-1/")
    assert not sp.is_title_root("https://law.justia.com/codes/utah/title-58/section-1-5/")
    assert narrow.whole_title("https://law.justia.com/codes/utah/title-58/")     # via shared fn


def test_container_segment_shared_and_correct():
    assert audit_mappings.container_segment is sp.container_segment
    assert sp.container_segment("https://law.justia.com/codes/x/title-1/chapter-29/")
    assert not sp.container_segment(
        "https://law.justia.com/codes/x/title-1/section-1-5/")
    # Must NOT flag real sections nested under IL act / ND chapter act structures.
    assert not sp.container_segment(
        "https://law.justia.com/codes/illinois/chapter-225/act-225-ilcs-80/section-80-5/")
