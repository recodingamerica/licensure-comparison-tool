"""audit_corpus on a tiny synthetic results-tree.

Covers the sync flags (STALE_CLEAN, NEEDS_CLEAN, PULL_ERROR, NEEDS_EXTRACT) and
the backlog classification (raw_empty / postclean_empty / ready) + queue split
(extract_ready vs needs_schema_first).
"""

from __future__ import annotations

import json

import pytest

import pipeline.eval.corpus_status as ac


@pytest.fixture
def tree(tmp_path, monkeypatch):
    text = tmp_path / "text"
    clean = tmp_path / "clean"
    structured = tmp_path / "structured"
    discovered = tmp_path / "discovered"
    config = tmp_path / "config"
    for d in (text, clean, structured, discovered, config):
        d.mkdir()
    (config / "corpus_overrides.yaml").write_text(yaml_dump({"hvac": {}}))

    monkeypatch.setattr(ac, "TEXT_DIR", text)
    monkeypatch.setattr(ac, "CLEAN_DIR", clean)
    monkeypatch.setattr(ac, "STRUCTURED_DIR", structured)
    monkeypatch.setattr(ac, "DISCOVERED_DIR", discovered)
    monkeypatch.setattr(ac, "CONFIG_DIR", config)
    monkeypatch.setattr(ac, "STAGE_DIRS", {
        "text": text, "clean": clean, "trimmed": tmp_path / "trimmed", "structured": structured,
    })

    def write(stage_dir, prof, state, record):
        d = stage_dir / prof
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{state}.json").write_text(json.dumps(record))

    return {"text": text, "clean": clean, "structured": structured,
            "discovered": discovered, "write": write}


def yaml_dump(d):
    import yaml
    return yaml.safe_dump(d)


def _secs(n):
    return {"sections": [{"text": "x"} for _ in range(n)]}


def test_sync_flags(tree):
    w = tree["write"]
    # healthy: text==clean, has structured
    w(tree["text"], "dietetics", "IA", _secs(3))
    w(tree["clean"], "dietetics", "IA", _secs(3))
    w(tree["structured"], "dietetics", "IA", {"foo": 1})
    # stale clean: counts mismatch
    w(tree["text"], "dietetics", "OH", _secs(5))
    w(tree["clean"], "dietetics", "OH", _secs(2))
    # needs clean: text only
    w(tree["text"], "dietetics", "NV", _secs(4))
    # pull error
    w(tree["text"], "hvac", "TX", {"sections": [{"text": "x"}], "errors": ["boom"]})

    rows = ac.audit_sync(ac.index_stages())
    flat = {(r["prof"], r["state"]): r["flags"] for r in rows}
    assert any(f.startswith("STALE_CLEAN") for f in flat[("dietetics", "OH")])
    assert "NEEDS_CLEAN" in flat[("dietetics", "NV")]
    assert "PULL_ERROR" in flat[("hvac", "TX")]
    # the one with structured is not in the extract backlog
    assert "NEEDS_EXTRACT" not in flat[("dietetics", "IA")]
    assert "NEEDS_EXTRACT" in flat[("dietetics", "OH")]


def test_backlog_classification(tree):
    w = tree["write"]
    # ready: text>0, clean>0, no structured
    w(tree["text"], "dietetics", "IA", _secs(3))
    w(tree["clean"], "dietetics", "IA", _secs(2))
    # raw empty: 0 text sections
    w(tree["text"], "dietetics", "OH", _secs(0))
    # post-clean empty: text>0, clean==0
    w(tree["text"], "dietetics", "NV", _secs(4))
    w(tree["clean"], "dietetics", "NV", _secs(0))

    raw, postclean, ready = ac.classify_backlog(ac.index_stages())
    assert ("dietetics", "OH") in raw
    assert ("dietetics", "NV") in postclean
    assert [(p, s) for (p, s, _n) in ready] == [("dietetics", "IA")]


def test_write_queues_splits_on_schema(tree, tmp_path):
    w = tree["write"]
    # dietetics has a discovered schema → extract_ready
    w(tree["text"], "dietetics", "IA", _secs(3))
    w(tree["clean"], "dietetics", "IA", _secs(2))
    (tree["discovered"] / "dietetics.json").write_text(json.dumps({"discovered_fields": []}))
    # ghost has none → needs_schema_first
    w(tree["text"], "ghost", "UT", _secs(3))
    w(tree["clean"], "ghost", "UT", _secs(2))

    outdir = tmp_path / "queues"
    rc = ac.cmd_backlog(str(outdir))
    assert rc == 0
    er = json.loads((outdir / "extract_ready.json").read_text())
    ns = json.loads((outdir / "needs_schema_first.json").read_text())
    assert er == {"dietetics": ["IA"]}
    assert ns == {"ghost": ["UT"]}
