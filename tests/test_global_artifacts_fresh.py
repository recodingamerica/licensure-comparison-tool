"""The cross-profession artifacts must reflect the data currently on disk.

Every per-cell and per-profession stage has a content-hash freshness contract in
provenance.py. The global `fanout` tail — scope matrices, tag sheet, scorecard,
capabilities — is explicitly OUTSIDE it:

    "The global publish `fanout` tail stays OUTSIDE the contract (its freshness is
     'did any profession change', which the runner decides)."

So when the runner doesn't run, or runs before a later re-extract lands, these rot with
nothing able to say so. That happened: the shipped scope matrix predated the 2026-07-29
re-extracts and was wrong in 124 cells across 10 professions. Mississippi showed
optometric laser capsulotomy as PROHIBITED when the extracted record said authorized-
with-certification — a factual error on the site, reported by a user (#122), invisible
to every gate we had.

These builders are deterministic and cheap (scope matrices rebuilds in ~1s), so freshness
needs no stamping machinery: rebuild and compare. A failure here means "publish, don't
debug" — run `python -m pipeline.publish.refresh_all --professions <...>` (or the
individual builder) and ship the result.
"""
import json

import pytest

from pipeline.paths import WEB_DATA_DIR


def _shipped(name: str):
    """The payload as currently published, or None on a fresh clone.

    public/data/ is gitignored and repopulated from Blob by the site prebuild, so its
    absence means "nothing published locally yet," not "stale" — skip rather than fail.
    """
    p = WEB_DATA_DIR / f"{name}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())


def _cells(payload: dict) -> dict:
    """{(profession, row label, state): status} — compares the matrix by meaning rather
    than by JSON layout, so a key reordering or an added display field doesn't read as
    a data change."""
    out = {}
    for prof, body in (payload or {}).items():
        for row in (body or {}).get("rows", []):
            for state, status in (row.get("cells") or {}).items():
                out[(prof, row.get("label"), state)] = status
    return out


def test_shipped_scope_matrix_matches_the_data_on_disk():
    shipped = _shipped("scope_matrices")
    if shipped is None:
        pytest.skip("no scope_matrices.json published locally (fresh clone)")

    from pipeline.publish.build_scope_matrices import build
    rebuilt, _tally = build()

    old, new = _cells(shipped), _cells(rebuilt)
    common = old.keys() & new.keys()
    changed = sorted(k for k in common if old[k] != new[k])
    dropped = sorted(old.keys() - new.keys())
    added = sorted(new.keys() - old.keys())

    def sample(keys, fmt):
        return "\n  ".join(fmt(k) for k in keys[:8]) + ("\n  …" if len(keys) > 8 else "")

    assert not changed, (
        f"{len(changed)} scope-matrix cells disagree with the extracted records — the "
        f"site is showing stale scope data. Rebuild and publish.\n  "
        + sample(changed, lambda k: f"{k[0]} / {k[1]} / {k[2]}: shipped={old[k]!r} data={new[k]!r}")
    )
    assert not dropped and not added, (
        f"scope-matrix shape drifted: {len(dropped)} cells gone, {len(added)} new. "
        f"Rebuild and publish.\n  "
        + sample(dropped or added, lambda k: f"{k[0]} / {k[1]} / {k[2]}")
    )
