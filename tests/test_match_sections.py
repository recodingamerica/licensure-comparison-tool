"""Tests for pipeline.discover.match_sections — the LLM-free section-TITLE matcher.

Locks in the properties that make it a trustworthy "what to pull" signal:
  - a profession pattern in a SECTION TITLE is a hit (what chapter-label match misses)
  - excludes veto a hit
  - a profession is never matched against its OWN corpus (that's not a cross-ref)
  - only the title/citation is searched, never the body (avoids name-drop noise)
"""

import pipeline.discover.match_sections as ms


def test_section_title_extraction_ignores_body():
    sec = {"citation": "38.2-1845.2", "label": "License required of resident public adjusters",
           "text": "A long body that happens to mention barbers and plumbers ..."}
    title = ms._section_title(sec)
    assert "public adjuster" in title.lower()
    assert "barber" not in title.lower()          # body is NOT in the title string


def test_match_corpus_finds_section_nested_profession(monkeypatch):
    # public_adjuster patterns hit an insurance_producer section TITLE
    monkeypatch.setattr(ms, "_professions", lambda: {
        "public_adjuster": {"patterns": ["public adjuster"]},
    })
    monkeypatch.setattr(ms, "corpus_titles", lambda: {
        ("insurance_producer", "VA"): ["38.2-1845.2 License required of resident public adjusters"],
        ("insurance_producer", "GA"): ["33-1 General provisions"],   # no hit
    })
    found = ms.match_corpus(None)
    assert "public_adjuster" in found
    assert "VA:insurance_producer" in found["public_adjuster"]
    assert "GA:insurance_producer" not in found["public_adjuster"]


def test_own_corpus_is_not_a_crossref(monkeypatch):
    # a public_adjuster section title inside the public_adjuster OWN corpus is skipped
    monkeypatch.setattr(ms, "_professions", lambda: {
        "public_adjuster": {"patterns": ["public adjuster"]},
    })
    monkeypatch.setattr(ms, "corpus_titles", lambda: {
        ("public_adjuster", "PA"): ["63-1 Public adjuster licensure"],   # own corpus
    })
    assert ms.match_corpus(None) == {}


def test_excludes_veto_a_hit(monkeypatch):
    monkeypatch.setattr(ms, "_professions", lambda: {
        "nurse_midwifery": {"patterns": ["midwife"], "excludes": ["direct-entry"]},
    })
    monkeypatch.setattr(ms, "corpus_titles", lambda: {
        ("nursing", "CT"): ["19a-1 Direct-entry midwife registration"],   # excluded
        ("nursing", "KS"): ["65-1 Certified nurse midwife license"],      # kept
    })
    found = ms.match_corpus(None)
    assert "KS:nursing" in found["nurse_midwifery"]
    assert "CT:nursing" not in found.get("nurse_midwifery", {})
