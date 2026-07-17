"""Tests for the pull_text over-broad chapter guard (fast-skip a locator mis-pick
instead of grinding a 900s timeout). The discriminator is label-match: a legitimately
large NAMED chapter is kept; a huge whole-title/department chapter is skipped."""
import pipeline.ingest.pull_text as pt


def test_guard_skips_over_broad_unmatched_chapters(monkeypatch):
    monkeypatch.setattr(pt, "_OVER_BROAD_MAX", 200)
    # huge + label does not name the profession → skip
    assert pt._should_skip_over_broad("athlete_agent",
                                      "State universities and colleges -- regional education", 437)
    assert pt._should_skip_over_broad("public_adjuster", "Insurance Code", 1432)
    assert pt._should_skip_over_broad("insurance_producer", "(parent container)", 2000)


def test_guard_spares_legit_large_named_chapter(monkeypatch):
    monkeypatch.setattr(pt, "_OVER_BROAD_MAX", 200)
    # big but the label names the profession → keep (e.g. medicine's own big chapter)
    assert not pt._should_skip_over_broad("medicine", "Medicine and Surgery", 513)
    assert not pt._should_skip_over_broad("public_adjuster", "Public Adjusters", 300)


def test_guard_ignores_small_chapters(monkeypatch):
    monkeypatch.setattr(pt, "_OVER_BROAD_MAX", 200)
    assert not pt._should_skip_over_broad("athlete_agent", "anything at all", 30)


def test_guard_never_raises_on_unknown_profession(monkeypatch):
    monkeypatch.setattr(pt, "_OVER_BROAD_MAX", 200)
    # unknown profession → no patterns → don't skip (and don't crash)
    assert pt._should_skip_over_broad("not_a_real_profession_xyz", "Some Huge Title", 999) is False


def test_guard_does_not_skip_an_unlabelled_chapter(monkeypatch):
    """An absent label is UNKNOWN relevance, not a mismatch.

    Justia publishes NJ as flat sections under the title — an NJ chapter has a number
    but no name anywhere — so its index rows carry label "". Treating that as
    "doesn't match" skipped medicine/NJ's own 336-section chapter-9 and zeroed the
    cell (446 -> 114 sections). Size/budget still governs; relevance cannot.
    """
    monkeypatch.setattr(pt, "_OVER_BROAD_MAX", 300)
    assert not pt._should_skip_over_broad("medicine", "", 336)
    assert not pt._should_skip_over_broad("chiropractic", "", 336)
    assert not pt._should_skip_over_broad("medicine", "   ", 336)
    assert not pt._should_skip_over_broad("medicine", None, 336)


def test_unlabelled_chapter_covers_corpus_derived_mappings(monkeypatch):
    """The other producer of label-less rows: backfill_index_mappings (#78) writes a
    cell's mapping back from the `chapter_urls` its committed corpus was pulled from,
    also with label "". Those chapters are PROVEN (the corpus came out of them), so a
    label heuristic must never veto them. These three are the real cells whose corpora
    already exceed the ceiling, i.e. the ones that would have zeroed.
    """
    monkeypatch.setattr(pt, "_OVER_BROAD_MAX", 300)
    assert not pt._should_skip_over_broad("electrician", "", 1309)        # electrician/IL
    assert not pt._should_skip_over_broad("polygraph_examiner", "", 333)  # polygraph/CA
    assert not pt._should_skip_over_broad("polygraph_examiner", "", 325)  # polygraph/MA


def test_unlabelled_chapter_still_subject_to_fetch_budget(monkeypatch):
    """The no-label bypass must not defeat the budget test — that one is size-only."""
    monkeypatch.setattr(pt, "_OVER_BROAD_MAX", 300)
    monkeypatch.setattr(pt, "_fetch_budget_max_leaves", lambda: 100)
    assert pt._should_skip_over_broad("medicine", "", 336)
