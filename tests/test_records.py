"""record_files: sorted, skips _-prefixed, tolerates a missing dir."""

from __future__ import annotations

from pipeline._records import record_files


def test_skips_underscore_and_sorts(tmp_path):
    for name in ["OH.json", "IA.json", "_summary.json", "_candidates.json", "CA.json"]:
        (tmp_path / name).write_text("{}")
    (tmp_path / "notes.txt").write_text("x")  # non-json ignored
    got = [p.name for p in record_files(tmp_path)]
    assert got == ["CA.json", "IA.json", "OH.json"]


def test_missing_dir_is_empty(tmp_path):
    assert list(record_files(tmp_path / "nope")) == []
