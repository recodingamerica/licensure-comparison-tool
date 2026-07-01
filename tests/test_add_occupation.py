"""Tests for pipeline.discover.add_occupation.corpus_plan — the completeness planner.

The planner is what stops the tool from silently shipping an "80%-ok" occupation.
It sorts every state into three buckets from four on-disk sources:
  extract-now  = own corpus  |  global parent_corpus  |  per-state corpus_override
  review-first = density-scan sibling links NOT already covered (need a human OK)
  needs-pull   = no text anywhere
These lock in that available text is never dropped, a density hit already covered by
a parent isn't re-surfaced, and an unreviewed link stays a candidate (not extractable).
"""

import pipeline.discover.add_occupation as add

# add_occupation imports mechanical_cross_ref via the `discover` top-level shim
# (sys.path.insert), so patch the exact module object it bound — NOT the one under
# `pipeline.discover.*`, which is a distinct object under this dual-import setup.
xref = add.xref


def _setup(monkeypatch, own_by_prof, overrides, density):
    """own_by_prof: {profession: [states]} on disk; overrides: full corpus_overrides
    dict; density: what brute_force_links returns ({state: (sibling, score)})."""
    monkeypatch.setattr(add, "_parent_states", lambda p: sorted(own_by_prof.get(p, [])))
    monkeypatch.setattr(add, "_load_overrides", lambda: overrides)
    monkeypatch.setattr(xref, "_all_occupations", lambda: ["insurance_producer", "medicine"])
    monkeypatch.setattr(xref, "brute_force_links", lambda *a, **k: density)


def test_three_buckets_from_mixed_sources(monkeypatch):
    # own PA/TX + per-state override GA + a fresh density candidate NY
    _setup(monkeypatch,
           own_by_prof={"public_adjuster": ["PA", "TX"]},
           overrides={"public_adjuster": {"GA": "insurance_producer"}},
           density={"NY": ("insurance_producer", 12)})
    plan = add.corpus_plan("public_adjuster", ["public adjuster"], None)
    assert plan["extractable"] == {"PA", "TX", "GA"}
    assert set(plan["candidates"]) == {"NY"}
    assert "NY" not in plan["extractable"]          # candidate is NOT auto-extractable
    assert plan["blank"] == set(xref.ALL_STATES) - {"PA", "TX", "GA", "NY"}


def test_density_hit_already_covered_by_parent_is_not_a_candidate(monkeypatch):
    # global parent 'medicine' covers CO/TX; density also scores CO — must not double-count
    _setup(monkeypatch,
           own_by_prof={"osteopathic_medicine": [], "medicine": ["CO", "TX"]},
           overrides={},
           density={"CO": ("medicine", 20), "NY": ("medicine", 15)})
    plan = add.corpus_plan("osteopathic_medicine", ["osteopathic physician"], "medicine")
    assert {"CO", "TX"} <= plan["extractable"]      # via parent
    assert "CO" not in plan["candidates"]           # not re-surfaced as a candidate
    assert set(plan["candidates"]) == {"NY"}


def test_no_text_anywhere_is_all_blank(monkeypatch):
    # the genuinely-standalone case: nothing on disk, nothing found → all blank
    _setup(monkeypatch, own_by_prof={}, overrides={}, density={})
    plan = add.corpus_plan("brand_new_thing", ["brand new"], None)
    assert plan["extractable"] == set()
    assert plan["candidates"] == {}
    assert plan["blank"] == set(xref.ALL_STATES)


def test_own_corpus_alone_is_extractable_without_parent(monkeypatch):
    # regression: a standalone profession with already-pulled corpus must extract,
    # not dead-end at "needs Justia pull" (the public_adjuster bug this fixes).
    _setup(monkeypatch,
           own_by_prof={"public_adjuster": ["CT", "OH", "WI"]},
           overrides={},
           density={})
    plan = add.corpus_plan("public_adjuster", ["public adjuster"], None)
    assert plan["extractable"] == {"CT", "OH", "WI"}
    assert plan["candidates"] == {}
