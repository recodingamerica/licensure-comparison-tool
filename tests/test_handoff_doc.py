"""Guard the handoff-doc counts that feed the README STATUS block.

_published() must count only real professions — never a cross-profession artifact that
also lives in publish/.../data/ (scorecard, tag_sheet, scope_capabilities, …). It once
miscounted a new artifact as a profession because that artifact wasn't added to a hand-kept
blocklist; the fix intersects with the registry, and this test locks that in.
"""

from pipeline.client import handoff_doc as hd


def test_published_counts_only_registry_professions(tmp_path, monkeypatch):
    monkeypatch.setattr(hd, "DATA_DIR", tmp_path)
    # a real published profession alongside the artifacts + a stray file that share the dir
    for name in ("optometry", "scope_capabilities", "scorecard", "tag_sheet",
                 "_skiptest", "not_a_real_profession"):
        (tmp_path / f"{name}.json").write_text("{}")
    assert hd._published() == ["optometry"]   # only the registered profession
