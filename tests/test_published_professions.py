"""`published_professions()` is the ONE answer to "which professions does the site ship."

The bug this guards: `publish/build_state_browse.PROFESSIONS` was a hand-maintained
literal, so adding an occupation meant remembering to edit it. Dietetics got published
and was silently absent from every per-state browse blob — no error, just a view missing
a profession. The list is now derived; these tests keep it that way and keep the three
former copies (handoff_doc, export_data, build_state_browse) from drifting apart again.
"""
import json

from pipeline import paths
from pipeline.config import loaders


def _fake_data_dir(tmp_path, names):
    d = tmp_path / "data"
    d.mkdir()
    for n in names:
        (d / f"{n}.json").write_text(json.dumps({"display": n}))
    return d


def test_intersects_registry_so_artifacts_are_never_professions(tmp_path, monkeypatch):
    """scorecard/tag_sheet/scope_capabilities live in data/ too — an allowlist that
    auto-corrects, rather than a blocklist that rots as new artifacts get added."""
    d = _fake_data_dir(tmp_path, ["optometry", "dietetics", "tag_sheet", "scorecard"])
    monkeypatch.setattr(loaders, "all_profession_ids", lambda: ["optometry", "dietetics"])
    assert paths.published_professions(d) == ["dietetics", "optometry"]


def test_missing_data_dir_is_empty_not_an_error(tmp_path, monkeypatch):
    monkeypatch.setattr(loaders, "all_profession_ids", lambda: ["optometry"])
    assert paths.published_professions(tmp_path / "nope") == []


def test_state_browse_covers_every_published_profession():
    """The regression itself, against the real repo. Fails if anyone re-hardcodes the
    browse list, or hardcodes it and then publishes a profession without updating it."""
    from pipeline.publish import build_state_browse as bsb
    missing = sorted(set(paths.published_professions()) - set(bsb.PROFESSIONS))
    assert not missing, (
        f"published but absent from build_state_browse.PROFESSIONS: {missing}. "
        "That profession ships to the site but is missing from every per-state browse "
        "blob. PROFESSIONS should be derived from published_professions(), not literal."
    )


def test_handoff_and_export_agree_with_the_canonical_list():
    """Three call sites, one answer — they used to be three separate globs."""
    from pipeline.client import handoff_doc, export_data
    canonical = paths.published_professions()
    assert handoff_doc._published() == canonical
    assert export_data._published_professions() == canonical


def test_publish_false_opts_a_profession_out_of_core(tmp_path, monkeypatch):
    """`publish: false` in professions.yaml wins over the state count. public_adjuster
    cleared the >=10 threshold at 11/50 and still looked broken beside 50-state
    neighbours in the scorecard/tag sheet (#121)."""
    struct = tmp_path / "structured"
    for prof in ("optometry", "public_adjuster"):
        d = struct / prof
        d.mkdir(parents=True)
        for i in range(12):
            (d / f"S{i}.json").write_text("{}")
    monkeypatch.setattr(paths, "STRUCTURED_DIR", struct)
    monkeypatch.setattr(loaders, "registry_professions", lambda: {
        "optometry": {"display": "Optometry"},
        "public_adjuster": {"display": "Public Insurance Adjuster", "publish": False},
    })
    assert paths.core_professions() == ["optometry"]


def test_publish_false_beats_a_lingering_payload(tmp_path, monkeypatch):
    """The flag must mean the same thing in BOTH profession sets. It first only filtered
    core_professions(), so public_adjuster vanished from the scorecard while a 6.3 MB
    payload still in Blob kept it in the browse view and the occupation picker — the site
    prebuild pulls every blob down, so the file reappears locally however often you
    delete it (#121)."""
    d = _fake_data_dir(tmp_path, ["optometry", "public_adjuster"])
    monkeypatch.setattr(loaders, "all_profession_ids",
                        lambda: ["optometry", "public_adjuster"])
    monkeypatch.setattr(loaders, "registry_professions", lambda: {
        "optometry": {"display": "Optometry"},
        "public_adjuster": {"display": "Public Insurance Adjuster", "publish": False},
    })
    assert paths.published_professions(d) == ["optometry"]


def test_public_adjuster_is_actually_opted_out_in_the_real_config():
    """The config edit itself, not just the mechanism (#121)."""
    assert "public_adjuster" not in paths.core_professions()
    assert "public_adjuster" not in paths.published_professions()


def test_nobody_recomputes_the_published_data_path():
    """`WEB_DATA_DIR` is the one definition. Nine modules used to hand-build this path
    three different ways; one of them was RELATIVE, so it silently found zero payloads
    whenever it ran from outside the repo root. Import it, don't retype it."""
    import re
    bad = []
    # Only flag path CONSTRUCTION — `"public" / "data"` segment-building, or a Path()
    # literal containing the dir. Prose in docstrings/help text may name it freely.
    pat = re.compile(r'"public"\s*/\s*"data"|Path\([^)]*public/data')
    for f in sorted((paths.PIPELINE_ROOT).rglob("*.py")):
        if f.name == "paths.py" or ".venv" in f.parts or "__pycache__" in f.parts:
            continue
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if pat.search(line):
                bad.append(f"{f.relative_to(paths.REPO_ROOT)}:{i}: {line.strip()}")
    assert not bad, (
        "these recompute the published-data path instead of importing "
        "pipeline.paths.WEB_DATA_DIR:\n  " + "\n  ".join(bad)
    )
