"""Shared profession-index accessors — one home for glob/load/matched, replacing the
scattered copies whose guards diverged (some surfaced `_`-files, one could KeyError)."""

import json

from pipeline.config import loaders
from pipeline.config.loaders import all_profession_ids, load_profession_index, matched_for
from pipeline.extract.standard_model import deep_get


def test_all_profession_ids_skips_bookkeeping(tmp_path, monkeypatch):
    for name in ("medicine.json", "nursing.json", "_summary.json", "_candidates.json"):
        (tmp_path / name).write_text("{}")
    monkeypatch.setattr(loaders, "PROFESSION_INDEX_DIR", tmp_path)
    assert all_profession_ids() == ["medicine", "nursing"]        # no _-prefixed


def test_load_profession_index_missing_is_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(loaders, "PROFESSION_INDEX_DIR", tmp_path)
    assert load_profession_index("nope") == {}
    (tmp_path / "medicine.json").write_text(json.dumps({"profession": "medicine"}))
    assert load_profession_index("medicine")["profession"] == "medicine"


def test_matched_for_is_null_safe():
    idx = {"by_state": {"CA": {"matched": [{"url": "u1"}, {"url": "u2"}]}}}
    assert len(matched_for(idx, "CA")) == 2
    assert matched_for(idx, "TX") == []          # state absent
    assert matched_for({}, "CA") == []           # by_state absent — must NOT KeyError
    assert matched_for({"by_state": {"CA": {}}}, "CA") == []   # no matched key


def test_deep_get_bails_on_non_dict():
    assert deep_get({"a": {"b": {"c": 5}}}, "a", "b", "c") == 5
    assert deep_get({"a": 1}, "a", "b") is None   # 1 is not a dict → None, no crash
    assert deep_get(None, "a") is None
