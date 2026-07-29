"""pull_state: year-version dedup must span ALL of a state's chapter rows, not one walk.

An index can carry a year-stamped chapter AND its undated parent (or two editions of the
same chapter) as separate rows — real case: nursing/TX had `/2023/…/subtitle-e/chapter-301/`
alongside the undated `/…/subtitle-e/`, which contains exactly that chapter. Cross-row
de-duplication was an EXACT-url set, and those two urls differ by the year segment, so every
section was fetched twice and both copies were written with the same citation. The UI
resolves a section by citation last-wins, so one copy became unreachable; the corpus shipped
378 sections for 195 sections of law. medicine/TX and dentistry/TX had the same shape (133
and 100 duplicated citations).
"""

from __future__ import annotations

import pipeline.ingest.pull_text as pt

BASE = "https://law.justia.com/codes/texas/occupations-code/title-3/subtitle-e"


def _row(url):
    return {"chapter_url": url, "chapter_label": "Regulation of Nursing", "chapter_slug": "x"}


def _run(monkeypatch, rows, targets_by_url):
    """Drive pull_state with the network stubbed: resolution returns canned targets and
    each fetched section records its url."""
    monkeypatch.setattr(pt, "_resolve_section_targets",
                        lambda corpus, row, url, prof, state: targets_by_url[url])

    def _add(corpus, sec):
        corpus.sections.append(pt.Section(url=sec["url"], label=sec.get("label", ""),
                                          citation="301.001", text="t", text_len=1))
    monkeypatch.setattr(pt, "_fetch_and_add_section", _add)
    return pt.pull_state("TX", "nursing", rows, None)


def test_year_stamped_row_collapses_against_undated_parent(monkeypatch):
    dated = "https://law.justia.com/codes/texas/2023/occupations-code/title-3/subtitle-e/chapter-301/"
    undated = f"{BASE}/"
    targets = {
        dated: [{"url": "https://law.justia.com/codes/texas/2023/occupations-code/title-3/"
                        "subtitle-e/chapter-301/section-301-001/", "label": "", "slug": "s"}],
        undated: [{"url": f"{BASE}/chapter-301/section-301-001/", "label": "", "slug": "s"}],
    }
    corpus = _run(monkeypatch, [_row(dated), _row(undated)], targets)

    urls = [s.url for s in corpus.sections]
    assert len(urls) == 1, f"section fetched once per edition, not deduped: {urls}"
    # the UNVERSIONED url wins, so a stale edition can't shadow current text
    assert "/2023/" not in urls[0]


def test_distinct_sections_across_rows_all_kept(monkeypatch):
    """The dedup must not collapse genuinely different sections from different rows."""
    a, b = f"{BASE}/chapter-301/", f"{BASE}/chapter-303/"
    targets = {
        a: [{"url": f"{a}section-301-001/", "label": "", "slug": "s"}],
        b: [{"url": f"{b}section-303-001/", "label": "", "slug": "s"}],
    }
    corpus = _run(monkeypatch, [_row(a), _row(b)], targets)
    assert len(corpus.sections) == 2


def test_flat_act_sections_sharing_one_url_survive(monkeypatch):
    """IL/PA serve a whole act at ONE url; those targets group under the same canonical
    path and must all be kept (they're split into sections later, not here)."""
    url = "https://law.justia.com/codes/illinois/chapter-225/act-225-ilcs-65/article-50/"
    targets = {url: [{"url": url, "label": "Sec. 50-1", "slug": "a"},
                     {"url": url, "label": "Sec. 50-5", "slug": "a"}]}
    corpus = _run(monkeypatch, [_row(url)], targets)
    # both targets survive the dedup; the exact-url guard then keeps the first
    assert pt._dedupe_year_versions(targets[url]) == targets[url]
    assert len(corpus.sections) == 1
