"""Tests for pipeline.discover.match_sections — the LLM-free section-TITLE matcher.

Locks in the properties that make it a trustworthy "what to pull" signal:
  - a profession pattern in a SECTION TITLE is a hit (what chapter-label match misses)
  - excludes veto a hit
  - a profession is never matched against its OWN corpus (that's not a cross-ref)
  - only the title/citation is searched, never the body (avoids name-drop noise)
"""

import json

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


# --- hierarchy_targets: what to PULL (parent container of a matched leaf) ---

def test_leaf_section_target_is_its_parent_container(monkeypatch):
    # matched leaf "626.854 Public adjuster" → pull its parent Part VI, not the bare section
    monkeypatch.setattr(ms, "_professions", lambda: {"public_adjuster": {"patterns": ["public adjuster"]}})
    monkeypatch.setattr(ms, "_hierarchy_nodes", lambda st: [
        {"label": "Part VI - Insurance Adjusters", "url": "http://j/part-vi/"},
        {"label": "626.854 - “Public adjuster” defined", "url": "http://j/part-vi/626-854/",
         "parent_chapter_url": "http://j/part-vi/"},
    ])
    t = ms.hierarchy_targets("public_adjuster", "FL")
    assert t == {"http://j/part-vi/": "Part VI - Insurance Adjusters"}  # parent, deduped


def test_named_grouping_target_is_itself(monkeypatch):
    # "Part IX - Athlete Agents" names the profession → pull the part directly
    monkeypatch.setattr(ms, "_professions", lambda: {"athlete_agent": {"patterns": ["athlete agent"]}})
    monkeypatch.setattr(ms, "_hierarchy_nodes", lambda st: [
        {"label": "Part IX - Athlete Agents", "url": "http://j/part-ix/", "parent_chapter_url": "http://j/ch468/"},
    ])
    assert ms.hierarchy_targets("athlete_agent", "FL") == {"http://j/part-ix/": "Part IX - Athlete Agents"}


def test_write_targets_merges_dedups_and_tags(monkeypatch, tmp_path):
    """write_targets (new behavior): creates YAML override entries tagged via='section_match',
    skips urls already in the base index, and calls rebuild_and_write when something was added.
    Does NOT write directly to the index JSON — that's now rebuild_and_write's job.
    """
    # hierarchy_targets returns one new container for FL only
    monkeypatch.setattr(ms, "hierarchy_targets",
                        lambda prof, st: {"http://j/part-vi/": "Part VI"} if st == "FL" else {})

    added: list[dict] = []
    rebuilt: list[str] = []

    def fake_rebuild_index(prof, mapping_overrides=None):
        # Simulate a clean base (no pre-existing match for FL)
        return {"by_state": {"FL": {"matched": []}}}

    def fake_rebuild_and_write(prof):
        rebuilt.append(prof)

    def fake_add_override_entry(profession, state, node):
        added.append({"profession": profession, "state": state, **node})

    monkeypatch.setattr(ms, "rebuild_index", fake_rebuild_index)
    monkeypatch.setattr(ms, "rebuild_and_write", fake_rebuild_and_write)
    monkeypatch.setattr(ms, "add_override_entry", fake_add_override_entry)

    written = ms.write_targets("public_adjuster", ["FL", "GA"])

    # FL got a new target; GA had none
    assert "FL" in written
    assert "GA" not in written
    # add_override_entry was called once for FL with the correct node shape
    assert len(added) == 1
    entry = added[0]
    assert entry["profession"] == "public_adjuster"
    assert entry["state"] == "FL"
    assert entry["url"] == "http://j/part-vi/"
    assert entry["via"] == "section_match"     # tagged correctly
    # rebuild was triggered
    assert rebuilt == ["public_adjuster"]

    # Dedup: if url is already in the base index, it should NOT be added again
    def fake_rebuild_index_with_existing(prof, mapping_overrides=None):
        return {"by_state": {"FL": {"matched": [
            {"url": "http://j/part-vi/", "label": "Part VI"}
        ]}}}

    added2: list = []
    monkeypatch.setattr(ms, "rebuild_index", fake_rebuild_index_with_existing)
    monkeypatch.setattr(ms, "add_override_entry", lambda prof, st, node: added2.append(node))

    written2 = ms.write_targets("public_adjuster", ["FL"])
    assert written2 == {}   # url already in base — nothing written
    assert added2 == []
