"""A committed TITLE_STRAY corpus (only a container landing page) being replaced by
real leaf sections is an upgrade, not a regression — the guard must not block it."""

from pipeline.ingest.pull_text import _is_regression, _lost_sections


def _sec(url, cite, text):
    return {"url": url, "citation": cite, "text": text}


def test_container_page_replaced_by_real_sections_is_not_regression():
    old = {"sections": [_sec("https://law.justia.com/codes/new-jersey/title-26/chapter-2k/",
                             "Chapter 2K", "Chapter 2K - Emergency Medical Services")],
           "total_chars": 200000}
    new = {"sections": [_sec(f"https://law.justia.com/codes/new-jersey/title-26/section-26-2k-{i}/",
                             f"26:2K-{i}", f"section {i} text") for i in range(1, 89)],
           "total_chars": 150000}
    assert _lost_sections(old, new) == []          # the junk container page isn't "lost"
    assert _is_regression(new, old) is None         # so no regression — the upgrade commits


def test_blob_replaced_by_fewer_char_real_sections_is_not_regression():
    # The live NJ case: the committed corpus is one huge container blob (237k chars); the
    # new pull is real sections totalling FAR fewer chars (blob included nav/boilerplate).
    # new_chars < old_chars*0.5 would wrongly read as a collapse — but the old blob's chars
    # are container junk, so it's an upgrade.
    old = {"sections": [_sec("https://law.justia.com/codes/new-jersey/title-17/chapter-22a/",
                             "Chapter 22A - Insurance Producer Licensing Act", "x" * 237000)],
           "total_chars": 237000}
    new = {"sections": [_sec(f"https://law.justia.com/codes/new-jersey/title-17/section-17-22a-{i}/",
                             f"17:22A-{i}", "s" * 1900) for i in range(1, 35)],
           "total_chars": 65000}
    assert _is_regression(new, old) is None      # blob → real sections commits, not held


def test_genuine_text_collapse_of_real_corpus_still_trips():
    # A real multi-section corpus whose text collapses to <50% (a bad/blocked pull) MUST
    # still be held — the container exemption must not weaken that protection.
    old = {"sections": [_sec(f"https://law.justia.com/x/title-1/section-1-{i}/", f"1-{i}", "t" * 2000)
                        for i in range(1, 21)],
           "total_chars": 40000}
    new = {"sections": [_sec("https://law.justia.com/x/title-1/section-1-1/", "1-1", "t" * 500)],
           "total_chars": 500}
    assert _is_regression(new, old) is not None


def test_real_section_removal_is_still_a_regression():
    old = {"sections": [_sec("https://law.justia.com/x/title-1/section-1/", "1", "a"),
                        _sec("https://law.justia.com/x/title-1/section-2/", "2", "b")],
           "total_chars": 2}
    new = {"sections": [_sec("https://law.justia.com/x/title-1/section-1/", "1", "a")],
           "total_chars": 1}
    assert _is_regression(new, old) is not None     # a genuine section drop still trips
