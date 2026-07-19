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


def test_lone_stray_container_among_real_leaves_is_not_lost():
    # Utah case (athletic_training/UT): a corpus of real leaf sections PLUS one stray
    # container "section" — the chapter TOC page (".../chapter-40a/", text "Title 58 …
    # Chapter 40a … Part 1 … Part 2") accidentally committed as a section. A cleaner
    # re-pull returns just the real leaves. Dropping the lone stray TOC is an upgrade, so
    # it must NOT count as a lost section (was a false REGRESSION that held the cell).
    base = "https://law.justia.com/codes/utah/title-58/chapter-40a/"
    leaves = [_sec(base + f"part-1/section-{i}/", f"58-40a-{i}", f"real statute text {i}")
              for i in range(1, 12)]
    stray_toc = _sec(base, "2025 Utah Code", "Title 58 Chapter 40a Part 1 Part 2")
    old = {"sections": leaves + [stray_toc], "total_chars": 20000}
    new = {"sections": leaves, "total_chars": 19000}         # cleaner pull, no stray TOC
    assert _lost_sections(old, new) == []                    # the lone stray TOC isn't "lost"
    assert _is_regression(new, old) is None                  # so it commits, not held

def test_real_leaf_loss_alongside_stray_container_still_trips():
    # acupuncture/UT: the corpus has a stray container TOC AND real leaves, and the re-pull
    # drops BOTH the TOC (fine) and a REAL leaf section (a genuine completeness gap). The
    # real-leaf loss must still be caught even though the TOC is exempt.
    base = "https://law.justia.com/codes/utah/title-58/chapter-72/"
    leaves = [_sec(base + f"part-{i}/section-{i}01/", f"58-72-{i}01", f"real statute {i}")
              for i in range(1, 8)]
    stray_toc = _sec(base, "2025 Utah Code", "Title 58 Chapter 72 Part 1 Part 2")
    old = {"sections": leaves + [stray_toc], "total_chars": 20000}
    new = {"sections": leaves[:-1], "total_chars": 17000}    # dropped TOC + one real leaf
    lost = _lost_sections(old, new)
    assert [s["citation"] for s in lost] == ["58-72-701"]    # only the real leaf is lost
    assert _is_regression(new, old) is not None              # held for review — correct

def test_many_container_url_sections_are_protected_not_exempt():
    # The medicine/ND bug: ND inline-split sections legitimately share the chapter
    # (container) URL, but they're REAL. A re-pull of a DIFFERENT chapter (0 citation
    # overlap) must be caught as a regression — not silently committed because the old
    # sections happen to have container URLs. (60 of chapter 43-17 → 11 of 43-17.1.)
    old = {"sections": [_sec("https://law.justia.com/codes/north-dakota/title-43/chapter-43-17/",
                             f"43-17-{i:02d}", f"physicians and surgeons section {i}") for i in range(1, 61)],
           "total_chars": 56000}
    new = {"sections": [_sec("https://law.justia.com/codes/north-dakota/title-43/chapter-43-17-1/",
                             f"43-17.1-{i:02d}", f"investigative panel section {i}") for i in range(1, 12)],
           "total_chars": 52000}
    assert _is_regression(new, old) is not None    # wrong-chapter swap CAUGHT (was blind)


def test_real_section_removal_is_still_a_regression():
    old = {"sections": [_sec("https://law.justia.com/x/title-1/section-1/", "1", "a"),
                        _sec("https://law.justia.com/x/title-1/section-2/", "2", "b")],
           "total_chars": 2}
    new = {"sections": [_sec("https://law.justia.com/x/title-1/section-1/", "1", "a")],
           "total_chars": 1}
    assert _is_regression(new, old) is not None     # a genuine section drop still trips
