"""Silent-swallow sites made loud: a swallowed failure is now logged, not invisible,
while the safe fallback / skip behaviour is unchanged."""

import logging

import pipeline.config.loaders as loaders


def test_corpus_profession_for_warns_on_unreadable_professions_yaml(tmp_path, monkeypatch, caplog):
    # A malformed professions.yaml (duplicate key -> YAMLError) used to be swallowed
    # silently, disabling parent_corpus redirection. Now it warns AND keeps the
    # safe fallback (the profession's own corpus).
    (tmp_path / "professions.yaml").write_text("medicine:\n  a: 1\nmedicine:\n  b: 2\n")
    monkeypatch.setattr(loaders, "CONFIG_DIR", tmp_path)
    with caplog.at_level(logging.WARNING):
        result = loaders.corpus_profession_for("dental_hygienist")
    assert result == "dental_hygienist"  # unchanged safe fallback
    assert any("parent_corpus redirect disabled" in r.message for r in caplog.records)
