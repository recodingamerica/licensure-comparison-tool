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


def test_main_writes_per_profession_files(fake_data, monkeypatch):
    """The /umbrella/profession/<id> view needs per-profession files keyed by
    profession id, with per-state cards. Universal sections count for every
    profession the state regulates; enumerated sections count only for the
    professions on their applies_to list. Undetermined never propagates."""
    B, out_dir = fake_data
    monkeypatch.setattr(B, "_states_with_scope", lambda: ["XX"])
    monkeypatch.setattr("sys.argv", ["build_umbrella_browse"])
    B.main()
    prof_dir = out_dir / "by_profession"
    assert prof_dir.is_dir()
    # one file per profession the state regulates (podiatry/nursing/medicine)
    pids = sorted(p.stem for p in prof_dir.glob("*.json") if not p.stem.startswith("_"))
    assert pids == ["medicine", "nursing", "podiatry"]

    nursing = json.loads((prof_dir / "nursing.json").read_text())
    assert nursing["profession"] == "nursing"
    assert nursing["state_count"] == 1
    assert nursing["directly_enumerated_state_count"] == 1  # XX has a section listing nursing
    # u1 universal, u2 enumerated for [nursing, podiatry] → "multi"
    # (applies_to has 2 entries, more than just nursing alone)
    assert nursing["coverage"] == {"universal": 1, "multi": 1, "single": 0, "unclassified_in_state": 1}
    xx = nursing["states"][0]
    assert xx["state"] == "XX"
    # Undetermined u3 must not appear in the main classified set; it goes into
    # unclassified_chapters so the UI can surface it as honest residual.
    sections = [sec for ch in xx["chapters"] for sec in ch["sections"]]
    by_url = {s["url"]: s for s in sections}
    assert set(by_url) == {"u1", "u2"}
    assert by_url["u1"]["audience_kind"] == "universal"
    assert by_url["u2"]["audience_kind"] == "multi"
    assert xx["coverage"]["unclassified_in_state"] == 1
    unclassified_urls = {sec["url"]
                        for ch in xx["unclassified_chapters"]
                        for sec in ch["sections"]}
    assert unclassified_urls == {"u3"}

    # medicine isn't listed in the enumeration, so it only gets the universal sweep
    medicine = json.loads((prof_dir / "medicine.json").read_text())
    assert medicine["coverage"] == {"universal": 1, "multi": 0, "single": 0, "unclassified_in_state": 1}
    assert medicine["directly_enumerated_state_count"] == 0
    # unclassified residual is shared across professions the state regulates
    assert medicine["states"][0]["coverage"]["unclassified_in_state"] == 1

    # _index.json mirrors per-profession summaries for the picker
    pidx = json.loads((prof_dir / "_index.json").read_text())
    by_prof = {p["profession"]: p for p in pidx["professions"]}
    assert by_prof["medicine"]["state_count"] == 1
    assert by_prof["medicine"]["directly_enumerated_state_count"] == 0
    assert by_prof["nursing"]["directly_enumerated_state_count"] == 1
