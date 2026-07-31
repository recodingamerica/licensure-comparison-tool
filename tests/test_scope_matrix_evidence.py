"""The Scope view's colours must be backed by the statute behind each cell.

Atharv's spec, from #122: "greys have no statutes, reds have a statute that is a
prohibition, greens have a statute that is permission."

That rule already holds in the extracted data — for optometry, 216 authorized and 449
prohibited items every one carrying a quote, and 1,515 not-addressed items every one
carrying none, with zero violations. What broke was the trip to the screen: a per-item
row named only its PARENT field, so the UI had nothing item-level to show and fell back
to the parent's Evidence. A grey cell then displayed a neighbouring prohibition quote,
and a green "Corneal scraping" cell opened a quote about epilation. The colour and the
panel disagreed, which reads as bad data when the data was right.

build_scope_matrices now carries each item's own quote/citation onto the row, keyed by
state, and OMITS states with no quote — so "no key" IS "no statute," and the invariant
below is checkable on the shipped artifact rather than only in the records.
"""
import pytest

from pipeline.paths import published_professions
from pipeline.publish.build_scope_matrices import build


@pytest.fixture(scope="module")
def matrices():
    payload, _tally = build()
    return payload


def _per_item_rows(matrices):
    """Rows built from a per-item re-extraction — the only ones that carry evidence."""
    for prof, body in matrices.items():
        for row in body.get("rows", []):
            if "evidence" in row:
                yield prof, row


def test_some_rows_actually_carry_evidence(matrices):
    """Guards the guard: if the evidence key ever stops being emitted, the invariant
    test below would pass by iterating nothing."""
    rows = list(_per_item_rows(matrices))
    assert rows, "no scope-matrix row carries per-item evidence — did the builder stop emitting it?"
    assert any(p == "optometry" for p, _ in rows), "optometry is the re-extracted canary; expected rows there"


def test_a_coloured_cell_has_a_statute_and_a_grey_one_does_not(matrices):
    """included/excluded must cite something; not_addressed must not."""
    coloured_without, grey_with = [], []
    for prof, row in _per_item_rows(matrices):
        ev = row.get("evidence") or {}
        for state, status in (row.get("cells") or {}).items():
            has = state in ev and (ev[state].get("quote") or "").strip()
            if status in ("included", "excluded") and not has:
                coloured_without.append(f"{prof} / {row['label']} / {state}: {status} with no statute")
            if status == "not_addressed" and has:
                grey_with.append(f"{prof} / {row['label']} / {state}: not_addressed but cites "
                                 f"{ev[state].get('citation')!r}")

    assert not coloured_without, (
        f"{len(coloured_without)} cells are coloured included/excluded with no statute behind "
        f"them — the Scope view would assert a rule it can't show (#122):\n  "
        + "\n  ".join(coloured_without[:10])
    )
    assert not grey_with, (
        f"{len(grey_with)} cells read 'not addressed' while carrying a quote — grey claims the "
        f"statute is silent (#122):\n  " + "\n  ".join(grey_with[:10])
    )


def test_evidence_only_names_states_the_row_actually_has(matrices):
    """An evidence entry for a state with no cell would render a statute for a square
    that isn't on screen."""
    orphans = [
        f"{prof} / {row['label']} / {state}"
        for prof, row in _per_item_rows(matrices)
        for state in (row.get("evidence") or {})
        if state not in (row.get("cells") or {})
    ]
    assert not orphans, "evidence for states with no cell:\n  " + "\n  ".join(orphans[:10])


def test_published_professions_are_covered_by_the_matrix(matrices):
    """Every published profession should appear, so the Scope tab is never blank for one."""
    missing = [p for p in published_professions() if p not in matrices]
    assert not missing, f"published professions absent from the scope matrix: {missing}"
