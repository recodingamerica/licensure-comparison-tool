"""write_text_atomic / write_json_atomic: a stage output lands whole or not at all —
a crash mid-write can't leave a truncated JSON at a committed stage-output path."""

import json

import pytest

from pipeline._records import write_text_atomic, write_json_atomic


def test_successful_write_lands_full_content_no_temp_leftover(tmp_path):
    p = tmp_path / "sub" / "corpus.json"  # parent created on demand
    write_json_atomic(p, {"sections": [1, 2, 3]})
    assert json.loads(p.read_text()) == {"sections": [1, 2, 3]}
    # no .tmp leftovers in the directory
    assert [x.name for x in p.parent.iterdir()] == ["corpus.json"]


def test_failed_serialization_leaves_original_intact_and_no_temp(tmp_path):
    p = tmp_path / "corpus.json"
    p.write_text('{"good": "old content"}')
    with pytest.raises(TypeError):
        write_json_atomic(p, {"bad": object()})  # not JSON-serializable
    assert p.read_text() == '{"good": "old content"}'          # untouched
    assert sorted(x.name for x in tmp_path.iterdir()) == ["corpus.json"]  # temp cleaned up


def test_failed_mid_write_leaves_original_intact(tmp_path, monkeypatch):
    p = tmp_path / "corpus.json"
    p.write_text("original")
    import os
    real_replace = os.replace
    def boom(src, dst):
        raise OSError("simulated crash before replace")
    monkeypatch.setattr(os, "replace", boom)
    with pytest.raises(OSError):
        write_text_atomic(p, "new content that should never land")
    monkeypatch.setattr(os, "replace", real_replace)
    assert p.read_text() == "original"                          # never truncated
    assert sorted(x.name for x in tmp_path.iterdir()) == ["corpus.json"]  # temp cleaned up


def test_dumps_kwargs_passthrough(tmp_path):
    p = tmp_path / "c.json"
    write_json_atomic(p, {"k": "é"}, ensure_ascii=False, indent=None)
    assert p.read_text() == '{"k": "é"}'
