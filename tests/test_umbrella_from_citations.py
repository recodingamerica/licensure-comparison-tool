"""Tests for pipeline.discover.umbrella_from_citations — citation-audit → pull-list.

Locks in the two load-bearing pieces:
  - citation_id_from_url: an audit id "A-B" is the last two NUMBERED URL segments,
    leading zeros stripped (works across NM article / GA title-chapter / SD zero-pad).
  - merge_into_umbrella_chapters: adds records, never duplicates an already-present url.
"""

import json

import pipeline.discover.umbrella_from_citations as u


def test_citation_id_from_url():
    cid = u.citation_id_from_url
    assert cid("https://law.justia.com/codes/new-mexico/chapter-61/article-1/") == "61-1"
    assert cid("https://law.justia.com/codes/georgia/title-43/chapter-1/") == "43-1"
    assert cid("https://law.justia.com/codes/south-dakota/title-36/chapter-01/") == "36-1"  # zero-pad
    assert cid("https://law.justia.com/codes/indiana/title-25/article-2-1/") == "25-2"       # first \d of seg
    assert cid("https://law.justia.com/codes/x/only-one-33/") is None                        # needs two


def test_merge_dedups_by_url(tmp_path, monkeypatch):
    monkeypatch.setattr(u, "UMBRELLA_DIR", tmp_path)
    # pre-existing file already has 61-1
    (tmp_path / "NM.json").write_text(json.dumps({
        "state": "NM",
        "umbrella_chapters": [{"url": "http://j/61-1/", "label": "Uniform Licensing"}]}))
    result = {"NM": {"matched": [
        {"url": "http://j/61-1/", "label": "Uniform Licensing", "source": "citation_audit"},  # dup
        {"url": "http://j/61-9/", "label": "Psychology genl", "source": "citation_audit"},     # new
    ], "unmatched": []}}
    written = u.merge_into_umbrella_chapters(result)
    assert written == {"NM": 1}                       # only the new one
    rec = json.loads((tmp_path / "NM.json").read_text())
    urls = [c["url"] for c in rec["umbrella_chapters"]]
    assert urls == ["http://j/61-1/", "http://j/61-9/"]  # no duplicate


def test_merge_skips_states_with_no_matches(tmp_path, monkeypatch):
    monkeypatch.setattr(u, "UMBRELLA_DIR", tmp_path)
    written = u.merge_into_umbrella_chapters({"NM": {"matched": [], "unmatched": ["61-1"]}})
    assert written == {}
    assert not (tmp_path / "NM.json").exists()
