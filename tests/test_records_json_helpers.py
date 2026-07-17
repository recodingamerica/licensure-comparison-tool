"""read_json / load_sections — the one lenient JSON-load, replacing ~a dozen hand-rolled
copies whose error branches disagreed and several of which caught bare Exception.

The load-bearing contract: they swallow a MISSING or CORRUPT file (OSError /
JSONDecodeError) and nothing else. A bug in the caller must still surface.
"""

import json

import pytest

from pipeline._records import read_json, load_sections


def test_read_json_parses_valid(tmp_path):
    p = tmp_path / "x.json"
    p.write_text(json.dumps({"a": 1}))
    assert read_json(p) == {"a": 1}


def test_read_json_missing_returns_default(tmp_path):
    assert read_json(tmp_path / "nope.json") is None
    assert read_json(tmp_path / "nope.json", {}) == {}


def test_read_json_corrupt_returns_default(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{not json")
    assert read_json(p, "FALLBACK") == "FALLBACK"


def test_read_json_does_not_swallow_caller_bugs(tmp_path, monkeypatch):
    # A TypeError/KeyError raised while reading must propagate — the bare-except copies
    # this replaces would have masked it as "file absent → default".
    import pipeline._records as rec

    def boom(_self, *a, **k):
        raise TypeError("caller bug, not a missing file")
    monkeypatch.setattr(rec.Path, "read_text", boom)
    with pytest.raises(TypeError):
        read_json(tmp_path / "x.json")


def test_load_sections_variants(tmp_path):
    good = tmp_path / "c.json"
    good.write_text(json.dumps({"sections": [{"citation": "1-1"}, {"citation": "1-2"}]}))
    assert len(load_sections(good)) == 2

    empty = tmp_path / "e.json"
    empty.write_text(json.dumps({"sections": []}))
    assert load_sections(empty) == []

    nosec = tmp_path / "n.json"
    nosec.write_text(json.dumps({"other": 1}))
    assert load_sections(nosec) == []

    assert load_sections(tmp_path / "missing.json") == []       # missing → []

    listfile = tmp_path / "l.json"
    listfile.write_text(json.dumps([1, 2, 3]))                  # not a dict → []
    assert load_sections(listfile) == []
