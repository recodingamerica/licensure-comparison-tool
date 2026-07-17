"""backfill_index_mappings restores a lost by_state mapping from the corpus's own
chapter_urls (NO_MAPPING cells), and never clobbers an existing mapping."""

import json

import pipeline.discover.backfill_index_mappings as bf
import pipeline.eval.audit_mappings as am

CH = "https://law.justia.com/codes/x/title-1/chapter-1/"


def _setup(tmp_path, monkeypatch):
    text = tmp_path / "text"; idx = tmp_path / "index"
    (text / "electrician").mkdir(parents=True); idx.mkdir()
    # CA: healthy, already mapped; WY: corpus exists but index has NO matched (NO_MAPPING)
    (idx / "electrician.json").write_text(json.dumps({"by_state": {
        "CA": {"matched": [{"url": CH, "label": "keep me"}]},
        "WY": {"matched": []},
    }}))
    (text / "electrician" / "CA.json").write_text(json.dumps(
        {"chapter_urls": [CH], "sections": [{"url": CH + "s1"}]}))
    (text / "electrician" / "WY.json").write_text(json.dumps(
        {"chapter_urls": ["https://law.justia.com/codes/x/title-9/chapter-3/"],
         "sections": [{"url": "https://law.justia.com/codes/x/title-9/chapter-3/s1"}]}))
    for mod in (am, bf):
        monkeypatch.setattr(mod, "TEXT_DIR", text)
        monkeypatch.setattr(mod, "PROFESSION_INDEX_DIR", idx)
    return idx


def test_restores_no_mapping_from_corpus_and_preserves_existing(tmp_path, monkeypatch):
    idx = _setup(tmp_path, monkeypatch)
    bf.main(["--apply"])
    after = json.loads((idx / "electrician.json").read_text())["by_state"]
    # WY mapping restored from the corpus's chapter_urls
    assert after["WY"]["matched"][0]["url"] == "https://law.justia.com/codes/x/title-9/chapter-3/"
    assert after["WY"]["matched"][0]["via"] == "index_backfill"
    # CA's existing mapping untouched
    assert after["CA"]["matched"][0]["label"] == "keep me"


def test_dry_run_writes_nothing(tmp_path, monkeypatch):
    idx = _setup(tmp_path, monkeypatch)
    before = (idx / "electrician.json").read_text()
    bf.main([])  # dry-run
    assert (idx / "electrician.json").read_text() == before
