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
