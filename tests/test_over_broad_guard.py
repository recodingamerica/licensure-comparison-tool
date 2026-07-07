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
