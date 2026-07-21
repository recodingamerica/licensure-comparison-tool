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
    import os
    w = tree["write"]
    # healthy: clean newer than text, has structured
    w(tree["text"], "dietetics", "IA", _secs(3))
    w(tree["clean"], "dietetics", "IA", _secs(3))
    w(tree["structured"], "dietetics", "IA", {"foo": 1})
    # NORMAL dedup drop (clean < text) — must NOT be flagged stale
    w(tree["text"], "dietetics", "GA", _secs(10))
    w(tree["clean"], "dietetics", "GA", _secs(7))
    # truly stale: clean mtime older than text mtime
    w(tree["text"], "dietetics", "OH", _secs(5))
    w(tree["clean"], "dietetics", "OH", _secs(5))
    os.utime(tree["clean"] / "dietetics" / "OH.json", (1, 1))
    os.utime(tree["text"] / "dietetics" / "OH.json", (10**9, 10**9))
    # clean dropped everything
    w(tree["text"], "dietetics", "NM", _secs(4))
    w(tree["clean"], "dietetics", "NM", _secs(0))
    # needs clean: text only
    w(tree["text"], "dietetics", "NV", _secs(4))
    # pull error
    w(tree["text"], "hvac", "TX", {"sections": [{"text": "x"}], "errors": ["boom"]})

    rows = ac.audit_sync(ac.index_stages())
    flat = {(r["prof"], r["state"]): r["flags"] for r in rows}
    assert "STALE_CLEAN" in flat[("dietetics", "OH")]
    assert "STALE_CLEAN" not in flat[("dietetics", "GA")]   # normal dedup, not staleness
    assert "CLEAN_EMPTY" in flat[("dietetics", "NM")]
    assert "NEEDS_CLEAN" in flat[("dietetics", "NV")]
    assert "PULL_ERROR" in flat[("hvac", "TX")]
    # the one with structured is not in the extract backlog
    assert "NEEDS_EXTRACT" not in flat[("dietetics", "IA")]
    assert "NEEDS_EXTRACT" in flat[("dietetics", "OH")]


def _sec(url, text_len):
    return {"url": url, "text_len": text_len}


def test_index_only_and_thin_flags(tree):
    w = tree["write"]
    CH = "https://law.justia.com/codes/mississippi/title-73/chapter-21/"
    SEC = "https://law.justia.com/codes/mississippi/title-73/chapter-21/section-73-21-1/"
    # index-only: 1 chapter-page section, tiny text
    w(tree["text"], "pharmacy", "MS", {"sections": [_sec(CH, 900)]})
    # healthy peer: many real sections (gives the profession a high median)
    w(tree["text"], "pharmacy", "CA", {"sections": [_sec(SEC, 4000) for _ in range(40)]})
    w(tree["text"], "pharmacy", "TX", {"sections": [_sec(SEC, 4000) for _ in range(30)]})
    # thin (not index-only): 2 real section-URL pages, but profession median is high
    w(tree["text"], "pharmacy", "NV", {"sections": [_sec(SEC, 3000), _sec(SEC, 3000)]})

    rows = ac.audit_sync(ac.index_stages())
    flat = {(r["prof"], r["state"]): r["flags"] for r in rows}
    assert "INDEX_ONLY" in flat[("pharmacy", "MS")]
    assert "THIN" not in flat[("pharmacy", "MS")]      # index-only takes precedence
    assert "THIN" in flat[("pharmacy", "NV")]
    assert "INDEX_ONLY" not in flat[("pharmacy", "CA")]
    assert "THIN" not in flat[("pharmacy", "CA")]


def test_junk_as_200_flag(tree, tmp_path):
    import json as _json
    w = tree["write"]
    SEC = "https://law.justia.com/codes/x/title-1/chapter-2/section-2-5/"
    w(tree["text"], "pharmacy", "AL", {"sections": [
        {"url": SEC, "text": "Verifying you are human. Just a moment...", "text_len": 40}]})
    rows = ac.audit_sync(ac.index_stages())
    flat = {(r["prof"], r["state"]): r["flags"] for r in rows}
    assert "JUNK_AS_200" in flat[("pharmacy", "AL")]
    # a real section is not flagged
    p = tmp_path / "ok.json"
    p.write_text(_json.dumps({"sections": [{"url": SEC, "text": "The board shall license...", "text_len": 4000}]}))
    assert ac.has_block_page(p) is False


def test_soft_404_navblob_is_flagged(tree, tmp_path):
    """Regression: the Justia soft-404 nav blob ("Justia Legal Resources / Find a
    Lawyer") must flag as JUNK_AS_200 even with NO per-section error field. A stale
    hand-copied _BLOCK_MARKERS mirror once omitted this marker, so 44 committed
    corpora holding the nav blob passed sync as real content. Importing the marker
    set from pull_text (single source of truth) closes that drift."""
    import json as _json
    from pipeline.ingest.pull_text import _BLOCK_MARKERS as PULL_MARKERS
    # the markers used by the audit ARE pull_text's, not a divergent copy
    assert ac._BLOCK_MARKERS is PULL_MARKERS
    assert any("find a lawyer" in m for m in ac._BLOCK_MARKERS)
    navblob = "Justia Legal Resources\nFind a Lawyer\nBankruptcy Lawyers\nBusiness Lawyers"
    w = tree["write"]
    SEC = "https://law.justia.com/codes/x/title-1/chapter-2/statute-act-9-of-1990/"
    w(tree["text"], "pharmacy", "OR", {"sections": [
        {"url": SEC, "text": navblob, "text_len": len(navblob)}]})  # note: no "error" key
    rows = ac.audit_sync(ac.index_stages())
    flat = {(r["prof"], r["state"]): r["flags"] for r in rows}
    assert "JUNK_AS_200" in flat[("pharmacy", "OR")]


def test_index_only_helper(tree, tmp_path):
    import json as _json
    # a real section URL with plenty of text is NOT index-only even if it's the only one
    p = tmp_path / "ok.json"
    p.write_text(_json.dumps({"sections": [
        {"url": "https://law.justia.com/codes/x/title-1/chapter-2/section-2-5/", "text_len": 9000}]}))
    assert ac.is_index_only(p) is False
    p2 = tmp_path / "bad.json"
    p2.write_text(_json.dumps({"sections": [
        {"url": "https://law.justia.com/codes/x/title-1/chapter-2/", "text_len": 800}]}))
    assert ac.is_index_only(p2) is True


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


def _one_suspect(monkeypatch):
    """Drive cmd_gate with a single offline-suspect cell (dietetics/OH, STALE_CLEAN)
    and no drift, so the opt-in tiers have exactly one cell to enrich."""
    monkeypatch.setattr(ac, "index_stages", lambda: {})
    monkeypatch.setattr(ac, "audit_sync",
                        lambda idx: [{"prof": "dietetics", "state": "OH", "flags": ["STALE_CLEAN"]}])
    monkeypatch.setattr(ac, "_drift_one", lambda p, s, o: None)
    monkeypatch.setattr(ac, "_active_official_sources", lambda: set())


def test_gate_check_urls_folds_url_verdict(monkeypatch, capsys):
    import pipeline.eval.verify_urls as vu
    _one_suspect(monkeypatch)
    monkeypatch.setattr(ac, "_drift_index_nodes",
                        lambda p, s: [{"url": "https://law.justia.com/codes/x/"}])
    monkeypatch.setattr(vu, "probe", lambda url: {"verdict": "DEAD_404"})
    rc = ac.cmd_gate(check_urls=True)
    out = capsys.readouterr().out
    assert "URL_DEAD_404" in out and "STALE_CLEAN" in out
    assert rc == 1


def test_gate_check_urls_bounded_to_suspects(monkeypatch):
    """The network tier must only probe already-suspect cells — never a full sweep."""
    import pipeline.eval.verify_urls as vu
    monkeypatch.setattr(ac, "index_stages", lambda: {})
    monkeypatch.setattr(ac, "audit_sync", lambda idx: [])  # no offline suspects
    monkeypatch.setattr(ac, "_drift_one", lambda p, s, o: None)
    monkeypatch.setattr(ac, "_active_official_sources", lambda: set())
    calls = []
    monkeypatch.setattr(vu, "probe", lambda url: calls.append(url) or {"verdict": "STUB"})
    assert ac.cmd_gate(check_urls=True) == 0
    assert calls == []  # nothing suspect → nothing fetched


def test_gate_check_llm_folds_wrong_chapter(monkeypatch, capsys):
    import pipeline.discover.audit_corpus as acx
    _one_suspect(monkeypatch)
    monkeypatch.setattr(acx, "audit_states",
                        lambda prof, states: {s: {"verdict": "wrong_chapter"} for s in states})
    rc = ac.cmd_gate(check_llm=True)
    out = capsys.readouterr().out
    assert "WRONG_CHAPTER" in out
    assert rc == 1


def test_gate_check_llm_correct_corpus_adds_nothing(monkeypatch, capsys):
    import pipeline.discover.audit_corpus as acx
    _one_suspect(monkeypatch)
    monkeypatch.setattr(acx, "audit_states",
                        lambda prof, states: {s: {"verdict": "correct_licensure_text"} for s in states})
    ac.cmd_gate(check_llm=True)
    assert "WRONG_CHAPTER" not in capsys.readouterr().out


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
