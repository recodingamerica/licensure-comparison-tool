"""poll() must refuse to write a profession whose discovered schema changed after submit.

The batch prompts EMBED the schema as it existed at submit time, so the results carry
that field set forever. If the on-disk schema then changes (2026-07-29: a churned
re-derivation was submitted against, then reverted minutes later), writing the results
puts those states on field names the current schema doesn't have. submit() records a
sha256 per profession; poll() compares and errors that profession's cells instead of
writing them. Pre-guard batches (no schema_shas in metadata) keep working.
"""

from __future__ import annotations

import hashlib
import json
from types import SimpleNamespace

import pytest

import pipeline.extract.extract_state_batch as b


def _fake_client(results):
    """A stand-in Anthropic client: batch already ended, yields `results`."""
    batch = SimpleNamespace(processing_status="ended", request_counts={})
    return SimpleNamespace(
        messages=SimpleNamespace(batches=SimpleNamespace(
            retrieve=lambda bid: batch,
            results=lambda bid: iter(list(results)),
        )))


def _succeeded(custom_id):
    usage = SimpleNamespace(input_tokens=1, output_tokens=1,
                            cache_read_input_tokens=0, cache_creation_input_tokens=0)
    message = SimpleNamespace(content=[SimpleNamespace(type="text", text="{}")], usage=usage)
    return SimpleNamespace(custom_id=custom_id,
                           result=SimpleNamespace(type="succeeded", message=message))


@pytest.fixture
def env(tmp_path, monkeypatch):
    disc = tmp_path / "discovered"
    disc.mkdir()
    (disc / "med.json").write_text(json.dumps({"fields": []}))
    monkeypatch.setattr(b, "DISCOVERED_DIR", disc)
    monkeypatch.setattr(b, "BATCH_DIR", tmp_path)
    written = []
    monkeypatch.setattr(b, "_parse_and_write",
                        lambda cid, msg, classes, model=None: written.append(cid) or
                        dict(zip(("profession", "state"), cid.split("__", 1))))
    return disc, tmp_path, written


def _plant_metadata(batch_dir, schema_shas):
    meta = {"batch_id": "x", "model": "m", "queue": {"med": ["UT"]}}
    if schema_shas is not None:
        meta["schema_shas"] = schema_shas
    (batch_dir / "x.json").write_text(json.dumps(meta))


def test_poll_refuses_profession_whose_schema_changed(env, monkeypatch):
    disc, batch_dir, written = env
    _plant_metadata(batch_dir, {"med": "0" * 64})       # ≠ the file's real sha
    monkeypatch.setattr(b, "_client", lambda: _fake_client([_succeeded("med__UT")]))
    meta = b.poll("x")
    assert written == []                                 # nothing written
    assert meta["written"] == []
    assert meta["errored"] == [{"custom_id": "med__UT",
                                "reason": "schema_changed_since_submit"}]


def test_poll_writes_when_schema_sha_matches(env, monkeypatch):
    disc, batch_dir, written = env
    sha = hashlib.sha256((disc / "med.json").read_bytes()).hexdigest()
    _plant_metadata(batch_dir, {"med": sha})
    monkeypatch.setattr(b, "_client", lambda: _fake_client([_succeeded("med__UT")]))
    meta = b.poll("x")
    assert written == ["med__UT"]
    assert meta["errored"] == []


def test_poll_backcompat_no_recorded_sha_still_writes(env, monkeypatch):
    # Batches submitted before the guard have no schema_shas — they must keep polling.
    disc, batch_dir, written = env
    _plant_metadata(batch_dir, None)
    monkeypatch.setattr(b, "_client", lambda: _fake_client([_succeeded("med__UT")]))
    meta = b.poll("x")
    assert written == ["med__UT"]
    assert meta["errored"] == []


def test_poll_refuses_discarded_batch(env, monkeypatch):
    # A batch marked discarded (e.g. submitted against a schema that was later
    # reverted) must never be pollable by accident — its results would overwrite
    # good re-extractions with known-bad ones.
    disc, batch_dir, written = env
    meta = {"batch_id": "x", "model": "m", "queue": {"med": ["UT"]},
            "discarded": True, "discarded_reason": "churned schema"}
    (batch_dir / "x.json").write_text(json.dumps(meta))
    monkeypatch.setattr(b, "_client", lambda: _fake_client([_succeeded("med__UT")]))
    with pytest.raises(SystemExit) as e:
        b.poll("x")
    assert "DISCARDED" in str(e.value)
    assert written == []


def test_submit_records_schema_shas(env, monkeypatch):
    disc, batch_dir, _ = env
    # Trimmed message + preflight stubbed; capture the metadata submit writes.
    monkeypatch.setattr(b, "run_preflight", lambda q: {"ok": True, "ready": [], "blocked": {}})
    monkeypatch.setattr(b, "format_report", lambda r: "stub")
    monkeypatch.setattr(b, "_build_user_message", lambda s, p: "corpus text")
    fake_batch = SimpleNamespace(id="newbatch", processing_status="in_progress")
    monkeypatch.setattr(b, "_client", lambda: SimpleNamespace(
        messages=SimpleNamespace(batches=SimpleNamespace(create=lambda requests: fake_batch))))
    meta = b.submit({"med": ["UT"]})
    want = hashlib.sha256((disc / "med.json").read_bytes()).hexdigest()
    assert meta["schema_shas"] == {"med": want}
    assert json.loads((batch_dir / "newbatch.json").read_text())["schema_shas"] == {"med": want}
