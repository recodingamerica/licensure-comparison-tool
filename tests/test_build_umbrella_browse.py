"""Tests for the per-state umbrella browse data generator."""

from __future__ import annotations

import json

import pytest


@pytest.fixture
def fake_data(tmp_path, monkeypatch):
    """Stand up tmp_path-rooted dirs and stub load_merged_scope +
    build_reverse_index so the builder runs deterministically."""
    import pipeline.publish.build_umbrella_browse as B

    text_dir = tmp_path / "umbrella_text"; text_dir.mkdir()
    out_dir = tmp_path / "out"; out_dir.mkdir()
    monkeypatch.setattr(B, "UMBRELLA_TEXT_DIR", text_dir)
    monkeypatch.setattr(B, "OUT_DIR", out_dir)

    merged = {
        "XX": {
            "sections": [
                {"url": "u1", "label": "1.1 Definitions",
                 "umbrella_chapter_slug": "c1",
                 "scope_source": "universal", "applies_to_professions": None},
                {"url": "u2", "label": "1.2 Enumeration",
                 "umbrella_chapter_slug": "c1",
                 "scope_source": "inherited_enumeration",
                 "applies_to_professions": ["podiatry", "nursing"]},
                {"url": "u3", "label": "1.3 Mystery",
                 "umbrella_chapter_slug": "c1",
                 "scope_source": "undetermined", "applies_to_professions": None},
            ]
        }
    }
    (text_dir / "XX.json").write_text(json.dumps({"sections": [
        {"url": "u1", "umbrella_chapter_label": "Chapter 1", "text": "definitions text"},
        {"url": "u2", "umbrella_chapter_label": "Chapter 1", "text": "enum text"},
        {"url": "u3", "umbrella_chapter_label": "Chapter 1", "text": "mystery text"},
    ]}))

    monkeypatch.setattr(B, "load_merged_scope", lambda st: merged.get(st))
    # Three professions the state regulates per reverse_index
    monkeypatch.setattr(B, "build_reverse_index",
                        lambda st: {"chapter-a": ["podiatry"], "chapter-b": ["nursing"], "chapter-c": ["medicine"]})
    return B, out_dir


def test_build_state_umbrella_classifies_each_audience(fake_data):
    B, _ = fake_data
    p = B.build_state_umbrella("XX")
    assert p["state"] == "XX"
    assert p["section_count"] == 3
    assert p["coverage"] == {"universal": 1, "enumerated": 1, "undetermined": 1}
    # one chapter, three sections, audiences mapped right
    assert len(p["chapters"]) == 1
    secs = p["chapters"][0]["sections"]
    by_url = {s["url"]: s for s in secs}
    assert by_url["u1"]["audience"] == "universal" and by_url["u1"]["applies_to"] is None
    assert by_url["u2"]["audience"] == "enumerated" and by_url["u2"]["applies_to"] == ["nursing", "podiatry"]
    assert by_url["u3"]["audience"] == "undetermined" and by_url["u3"]["applies_to"] is None
    # chapter label picked up from umbrella_text
    assert p["chapters"][0]["label"] == "Chapter 1"
    # all_professions is the union across enumerations
    assert p["all_professions"] == ["nursing", "podiatry"]


def test_build_state_umbrella_none_when_no_scope(fake_data, monkeypatch):
    B, _ = fake_data
    monkeypatch.setattr(B, "load_merged_scope", lambda st: None)
    assert B.build_state_umbrella("XX") is None


def test_main_writes_index_with_matrix(fake_data, monkeypatch):
    B, out_dir = fake_data
    # only one state, with universal=1, enumerated names ["podiatry","nursing"]
    monkeypatch.setattr(B, "_states_with_scope", lambda: ["XX"])
    monkeypatch.setattr("sys.argv", ["build_umbrella_browse"])
    B.main()
    assert (out_dir / "XX.json").exists()
    idx = json.loads((out_dir / "_index.json").read_text())
    assert [s["state"] for s in idx["states"]] == ["XX"]
    # state regulates {podiatry, nursing, medicine}; universal counts for all 3,
    # plus the enumeration adds +1 each to podiatry and nursing
    m = idx["matrix"]["XX"]
    assert m["podiatry"] == 2     # 1 universal + 1 enumerated
    assert m["nursing"] == 2      # 1 universal + 1 enumerated
    assert m["medicine"] == 1     # 1 universal (not in the enumeration)
    # professions list is the union across all states' reverse_indexes
    assert set(idx["professions"]) == {"podiatry", "nursing", "medicine"}
