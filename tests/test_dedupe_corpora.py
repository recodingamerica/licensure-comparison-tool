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
