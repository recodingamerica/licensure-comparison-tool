"""Tests for dedupe_corpora — collapsing Justia year-versioned duplicate sections
in committed corpora. Pure local transform (no fetch); wraps
pull_text._dedupe_year_versions."""

import json

import pipeline.ingest.dedupe_corpora as dc

BASE = "https://law.justia.com/codes/wy"


def _corpus(urls):
    return {"sections": [{"url": u, "citation": u.rstrip("/").rsplit("/", 1)[-1],
                          "text": f"body {u.rstrip('/').rsplit('/', 1)[-1]}"} for u in urls],
            "total_chars": 999}


def test_dedupe_collapses_year_versions():
    # section-101 under 2023 + 2024 + undated -> one copy; section-102 (unique) survives.
    c = _corpus([
        f"{BASE}/2023/title-33/chapter-26/section-101/",
        f"{BASE}/2024/title-33/chapter-26/section-101/",
        f"{BASE}/title-33/chapter-26/section-101/",
        f"{BASE}/title-33/chapter-26/section-102/",
    ])
    nd = dc.dedupe_corpus(c)
    assert nd is not None
    urls = [s["url"] for s in nd["sections"]]
    assert len(urls) == 2
    assert sum("section-101" in u for u in urls) == 1  # collapsed to one
    assert any("section-102" in u for u in urls)       # unique kept
    assert "/2023/" not in " ".join(urls) and "/2024/" not in " ".join(urls)  # undated won
    assert nd["total_chars"] == sum(len(s["text"]) for s in nd["sections"])  # recomputed


def test_no_duplicates_returns_none():
    c = _corpus([f"{BASE}/title-33/chapter-26/section-101/",
                 f"{BASE}/title-33/chapter-26/section-102/"])
    assert dc.dedupe_corpus(c) is None


def test_cli_apply_writes_deduped(tmp_path, monkeypatch):
    td = tmp_path / "text"
    (td / "medicine").mkdir(parents=True)
    p = td / "medicine" / "WY.json"
    p.write_text(json.dumps(_corpus([
        f"{BASE}/2024/title-33/chapter-26/section-101/",
        f"{BASE}/title-33/chapter-26/section-101/",
        f"{BASE}/title-33/chapter-26/section-102/",
    ])))
    monkeypatch.setattr(dc, "TEXT_DIR", td)
    dc.main(["--apply"])
    after = json.loads(p.read_text())
    assert len(after["sections"]) == 2  # the 101 duplicate was collapsed


def test_cli_dry_run_writes_nothing(tmp_path, monkeypatch):
    td = tmp_path / "text"
    (td / "medicine").mkdir(parents=True)
    p = td / "medicine" / "WY.json"
    original = json.dumps(_corpus([
        f"{BASE}/2024/title-33/chapter-26/section-101/",
        f"{BASE}/title-33/chapter-26/section-101/",
    ]))
    p.write_text(original)
    monkeypatch.setattr(dc, "TEXT_DIR", td)
    dc.main([])  # dry-run
    assert p.read_text() == original  # untouched


# --- same-citation duplicates (dedupe_citation_copies, 2026-07-29) -----------------
# 140 duplicate-citation copies measured across published corpora; only the two
# mechanical classes collapse. PA flat acts and Justia subsection pages are LAW,
# not duplicates — they must survive untouched.

def _sec(url, citation, text):
    return {"url": url, "citation": citation, "text": text}


def test_citation_identical_text_collapsed():
    c = {"sections": [
        _sec(f"{BASE}/title-1/section-5/", "1-5", "same body"),
        _sec(f"{BASE}/title-1/other-path/section-5/", "1-5", "same body"),
        _sec(f"{BASE}/title-1/section-6/", "1-6", "unique"),
    ]}
    nd, removed = dc.dedupe_citation_copies(c)
    assert removed == {"identical_text": 1, "edition_pair": 0}
    assert [s["citation"] for s in nd["sections"]] == ["1-5", "1-6"]


def test_citation_edition_pair_keeps_newest_year():
    # podiatry/CO shape: 2022 vs 2023 editions whose paths differ beyond the year,
    # so the year-normalizing dedupe can't see them. Newest edition wins.
    c = {"sections": [
        _sec("https://law.justia.com/codes/colorado/2022/title-12/article-290/part-1/section-12-290-101/",
             "12-290-101", "old edition text"),
        _sec("https://law.justia.com/codes/colorado/2023/title-12/health-care-professions-and-occupations/article-290/part-1/section-12-290-101/",
             "12-290-101", "new edition text"),
    ]}
    nd, removed = dc.dedupe_citation_copies(c)
    assert removed["edition_pair"] == 1
    assert len(nd["sections"]) == 1
    assert "/2023/" in nd["sections"][0]["url"]


def test_citation_pa_flat_acts_untouched():
    # "§ 1" of the 1951 act and of the 1955 act are DIFFERENT LAWS sharing a
    # citation string — deleting either loses statute.
    c = {"sections": [
        _sec("https://www.legis.state.pa.us/WU01/LI/LI/US/HTM/1951/0/0069..HTM", "§ 1", "act of 1951"),
        _sec("https://www.legis.state.pa.us/WU01/LI/LI/US/HTM/1955/0/0376..HTM", "§ 1", "act of 1955"),
    ]}
    nd, removed = dc.dedupe_citation_copies(c)
    assert nd is None and removed == {"identical_text": 0, "edition_pair": 0}


def test_citation_subsection_pages_untouched():
    # public_accountancy/NM shape: section-61-28b-3 vs section-61-28b-3-d-1 both
    # labeled 61-28B-3 with different text — needs triage/disambiguation, not deletion.
    c = {"sections": [
        _sec("https://law.justia.com/codes/new-mexico/chapter-61/article-28b/section-61-28b-3/",
             "61-28B-3", "full section"),
        _sec("https://law.justia.com/codes/new-mexico/chapter-61/article-28b/section-61-28b-3-d-1/",
             "61-28B-3", "subsection page"),
    ]}
    nd, removed = dc.dedupe_citation_copies(c)
    assert nd is None and removed == {"identical_text": 0, "edition_pair": 0}
