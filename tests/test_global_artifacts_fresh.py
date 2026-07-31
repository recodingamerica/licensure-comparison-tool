"""The cross-profession artifacts must reflect the data currently on disk.

Every per-cell and per-profession stage has a content-hash freshness contract in
provenance.py. The global `fanout` tail — scope matrices, tag sheet, scorecard,
capabilities — is explicitly OUTSIDE it:

    "The global publish `fanout` tail stays OUTSIDE the contract (its freshness is
     'did any profession change', which the runner decides)."

So when the runner doesn't run, or runs before a later re-extract lands, these rot with
nothing able to say so. All four had: the scope matrix was wrong in 124 cells across 10
professions (Mississippi showed optometric laser capsulotomy as PROHIBITED when the
record said authorized-with-certification — a factual error on a public page, reported
by a user, #122); the scorecard disagreed in 9 cells; the tag sheet's data differed by
~114 KB; and three of them still carried an occupation retired in #121.

These builders are deterministic and cheap — the whole set rebuilds in about five
seconds — so freshness needs no stamping machinery: rebuild and compare. A failure here
means "publish, don't debug": run `python -m pipeline.publish.refresh_all` (or the named
builder) and ship the result.

Two things the comparison has to allow for:
  - `generated_at` changes every run and means nothing; it is stripped.
  - capabilities is built FROM the tag sheet on disk, so a stale tag sheet propagates.
    Rebuild in fanout order (the runner already does) rather than one at a time.
"""
import json

import pytest

from pipeline.paths import WEB_DATA_DIR, core_professions


def _strip(payload):
    """Drop build stamps that differ on every run and carry no data."""
    if isinstance(payload, dict):
        return {k: v for k, v in payload.items() if k != "generated_at"}
    return payload


def _norm(payload) -> str:
    return json.dumps(_strip(payload), sort_keys=True)


def _shipped(name: str):
    """The payload as currently published, or None on a fresh clone.

    public/data/ is gitignored and repopulated from Blob by the site prebuild, so its
    absence means "nothing published locally yet," not "stale" — skip rather than fail.
    """
    p = WEB_DATA_DIR / f"{name}.json"
    return json.loads(p.read_text()) if p.exists() else None


def _rebuild(name: str):
    """Rebuild one artifact from the records currently on disk."""
    if name == "scope_matrices":
        from pipeline.publish.build_scope_matrices import build
        return build()[0]
    if name == "tag_sheet":
        from pipeline.publish.build_tag_sheet import build_payload
        return build_payload(core_professions())
    if name == "scorecard":
        from pipeline.publish.cross_comparison_scorecard import build_payload
        return build_payload()
    if name == "scope_capabilities":
        from pipeline.publish.build_scope_capabilities import build
        return build()
    raise AssertionError(f"no rebuild wired for {name}")


ARTIFACTS = ["scope_matrices", "tag_sheet", "scorecard", "scope_capabilities"]


@pytest.mark.parametrize("name", ARTIFACTS)
def test_shipped_artifact_matches_the_data_on_disk(name):
    shipped = _shipped(name)
    if shipped is None:
        pytest.skip(f"no {name}.json published locally (fresh clone)")

    rebuilt = _rebuild(name)
    if _norm(shipped) == _norm(rebuilt):
        return

    # Say something more useful than "they differ" — name the professions that moved,
    # since that's what tells you which re-extract went unpublished.
    detail = ""
    # Compare the STRIPPED payloads here too, or the message blames `generated_at` —
    # the one key we deliberately ignore.
    s, r = _strip(shipped), _strip(rebuilt)
    if isinstance(s, dict) and isinstance(r, dict):
        gone = sorted(set(s) - set(r))
        added = sorted(set(r) - set(s))
        changed = sorted(
            k for k in set(s) & set(r)
            if json.dumps(s[k], sort_keys=True) != json.dumps(r[k], sort_keys=True)
        )
        parts = []
        if gone:
            parts.append(f"only in shipped: {gone[:8]}")
        if added:
            parts.append(f"only in rebuilt: {added[:8]}")
        if changed:
            parts.append(f"differing keys: {changed[:8]}")
        detail = "\n  " + "\n  ".join(parts) if parts else ""

    pytest.fail(
        f"{name}.json disagrees with the records on disk — the site is serving stale "
        f"cross-profession data. Rebuild and publish it.{detail}"
    )


def test_state_browse_index_covers_the_professions_it_should():
    """`data/state/` is 191 MB across 50 blobs — far too slow to rebuild-and-compare, so
    check its 16 KB index instead.

    build_state_browse includes a profession in a state's blob exactly when that cell has
    both a structured record and a trimmed corpus, and writes the resulting set into
    states.json. So the index is a cheap, faithful proxy for coverage: this morning it
    said 12 professions where it should have said 13, because dietetics was missing from
    every state blob AND from the statute-dictionary picker that reads this file.

    Cheap enough to keep honest without parsing the blobs themselves.
    """
    from pipeline.paths import WEB_PUBLIC_DIR, STRUCTURED_DIR, TRIMMED_DIR, published_professions
    from pipeline.config.loaders import is_absence_record

    def _browse_ships(prof: str, state: str) -> bool:
        """Mirror build_state_browse's inclusion rule: structured + trimmed both
        present, and the record is not a verified absence (whose corpus, where it
        has one, is the local-enabling hook rather than the profession's own law).

        Deliberately NOT named _shipped — that is a module-level helper with a
        different signature, used elsewhere in this file."""
        struct = STRUCTURED_DIR / prof / f"{state}.json"
        if not struct.exists() or not (TRIMMED_DIR / prof / f"{state}.json").exists():
            return False
        return not is_absence_record(json.loads(struct.read_text()))

    index_path = WEB_PUBLIC_DIR / "states.json"
    if not index_path.exists():
        pytest.skip("no states.json published locally (fresh clone)")

    published = published_professions()
    problems = []
    for entry in json.loads(index_path.read_text()):
        state = entry["state"]
        listed = set(entry.get("professions") or [])
        expected = {p for p in published if _browse_ships(p, state)}
        if listed != expected:
            missing, extra = sorted(expected - listed), sorted(listed - expected)
            problems.append(f"{state}: missing={missing} unexpected={extra}")

    assert not problems, (
        f"{len(problems)} states' browse coverage disagrees with the records on disk. A "
        f"missing profession is invisible in /browse and in the statute-dictionary picker. "
        f"Re-run `python -m pipeline.publish.build_state_browse`.\n  "
        + "\n  ".join(problems[:10])
    )


def _cells(payload: dict) -> dict:
    """{(profession, row label, state): status} — compares the scope matrix by meaning
    rather than JSON layout, so a key reordering or an added display field doesn't read
    as a data change."""
    out = {}
    for prof, body in (payload or {}).items():
        for row in (body or {}).get("rows", []):
            for state, status in (row.get("cells") or {}).items():
                out[(prof, row.get("label"), state)] = status
    return out


def test_scope_matrix_cells_agree_cell_by_cell():
    """The scope matrix gets a sharper check than the generic one: name the exact
    (profession, row, state) cells whose STATUS disagrees, since those are the ones a
    reader would act on. This is the check that would have caught #122."""
    shipped = _shipped("scope_matrices")
    if shipped is None:
        pytest.skip("no scope_matrices.json published locally (fresh clone)")

    old, new = _cells(shipped), _cells(_rebuild("scope_matrices"))
    changed = sorted(k for k in old.keys() & new.keys() if old[k] != new[k])
    assert not changed, (
        f"{len(changed)} scope-matrix cells disagree with the extracted records — the "
        f"site is showing stale scope data. Rebuild and publish.\n  "
        + "\n  ".join(
            f"{p} / {label} / {st}: shipped={old[(p, label, st)]!r} data={new[(p, label, st)]!r}"
            for p, label, st in changed[:8]
        )
        + ("\n  …" if len(changed) > 8 else "")
    )
