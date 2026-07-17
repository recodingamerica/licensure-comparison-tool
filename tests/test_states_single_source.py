"""config.states is the single source for state codes, names, and Justia slugs.

STATE_SLUG (gap_harvest) and STATE_NAME_MAP (suggest_scope_rules) used to be separate
literals that could drift from config.states.ALL_STATES. They now derive/import from here.
"""

from pipeline.config.states import STATE_NAMES, ALL_STATES, STATE_SLUG


def test_all_fifty_states():
    assert len(STATE_NAMES) == 50
    assert list(STATE_NAMES) == ALL_STATES
    assert set(STATE_SLUG) == set(STATE_NAMES)


def test_slug_is_derived_from_name():
    assert STATE_SLUG["NJ"] == "new-jersey"
    assert STATE_SLUG["NH"] == "new-hampshire"
    assert all(STATE_SLUG[c] == n.lower().replace(" ", "-") for c, n in STATE_NAMES.items())


def test_consumers_reexport_the_same_objects():
    from pipeline.discover.gap_harvest import _common
    from pipeline.discover import suggest_scope_rules
    assert _common.STATE_SLUG is STATE_SLUG
    assert _common.ALL_STATES is ALL_STATES
    assert suggest_scope_rules.STATE_NAME_MAP is STATE_NAMES
