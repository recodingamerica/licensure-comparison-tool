"""audit_mappings flags cells whose committed corpus can't be reproduced by a re-pull:
no index mapping (NO_MAPPING) or sections under no mapped chapter (STRAY_ONLY)."""

import json

import pipeline.eval.audit_mappings as am

CH = "https://law.justia.com/codes/x/title-1/chapter-1/"
CH2 = "https://law.justia.com/codes/x/title-1/chapter-2/"


def _setup(tmp_path, monkeypatch, index_by_state, corpora):
    text = tmp_path / "text"; idx = tmp_path / "index"
    text.mkdir(); idx.mkdir()
    for prof, states in index_by_state.items():
        (idx / f"{prof}.json").write_text(json.dumps(
            {"by_state": {st: {"matched": [{"url": u} for u in urls]} for st, urls in states.items()}}))
    for (prof, state), urls in corpora.items():
        d = text / prof; d.mkdir(exist_ok=True)
        (d / f"{state}.json").write_text(json.dumps({"sections": [{"url": u} for u in urls]}))
    monkeypatch.setattr(am, "TEXT_DIR", text)
    monkeypatch.setattr(am, "PROFESSION_INDEX_DIR", idx)


def test_flags_no_mapping_and_stray_but_not_healthy(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch,
           index_by_state={"med": {"CA": [CH], "WY": [], "TX": [CH, CH2], "NV": [CH]}},
           corpora={
               ("med", "CA"): [CH + "s1", CH + "s2"],                       # healthy
               ("med", "WY"): ["https://law.justia.com/codes/x/title-1/chapter-9/section-1"],  # leaf; empty index -> NO_MAPPING
               ("med", "TX"): ["https://law.justia.com/codes/x/title-9/section-1"],  # under neither chapter
               ("med", "NV"): ["https://law.justia.com/codes/x/title-5/chapter-9/"],  # chapter landing page -> TITLE_STRAY
           })
    found = {(p, s): t for p, s, t, _ in am.audit()}
    assert found.get(("med", "WY")) == "NO_MAPPING"
    assert found.get(("med", "TX")) == "STRAY_ONLY"
    assert found.get(("med", "NV")) == "TITLE_STRAY"
    assert ("med", "CA") not in found  # healthy cell not flagged
