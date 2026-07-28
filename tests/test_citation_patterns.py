"""Per-state label->citation patterns (config/state_structure.yaml `_citation_patterns`).

One regex cannot serve every state. The default's separator class had no comma, so KS/NE
sections numbered with an embedded comma (50-6,100 / 38-1,125) matched only up to the
comma: all 65 of Kansas's 50-6,1xx sections collapsed to the single citation "50-6",
leaving them both unaddressable and colliding with each other, so no quote citing them
could ever highlight.

The fix is per-state patterns in config -- and these tests pin the two ways that can go
wrong: the override must fix its own state, and the DEFAULT must not move for anyone else.
"""

from __future__ import annotations

import pytest

from pipeline.ingest.pull_text import short_citation


@pytest.mark.parametrize("label,expected", [
    ("50-6,100 Arbitration of disputes.", "50-6,100"),
    ("50-6,129 Exemptions.", "50-6,129"),
    ("65-16,101 Statewide electronic logging system.", "65-16,101"),
    ("50-626 Unconscionable acts and practices.", "50-626"),   # no comma: still fine
])
def test_kansas_comma_numbered_sections(label, expected):
    assert short_citation(label, "KS") == expected


def test_nebraska_comma_numbered_sections():
    assert short_citation("38-1,125 - Credential holder except pharmacist.", "NE") == "38-1,125"


@pytest.mark.parametrize("state,label,expected", [
    # The default must stay UNANCHORED: these states prefix the number, and anchoring it
    # re-cited 15,138 sections across 363 cells with the entire label.
    ("IL", "Sec. 4.5. Opioid antagonists.", "4.5"),
    ("NV", 'NRS 577.010 - Definitions.', "577.010"),
    ("UT", "Section 20-50. - Podiatric medicine defined.", "20-50"),
    ("AK", "08.36.234 Licensing by credentials.", "08.36.234"),
    ("SC", "Section 40-65-230,40-65-240.", "40-65-230"),   # a RANGE: take the first only
])
def test_default_pattern_is_unchanged_for_other_states(state, label, expected):
    assert short_citation(label, state) == expected


def test_unknown_state_falls_back_to_the_default():
    assert short_citation("Section 20-50. - Podiatric medicine defined.", "ZZ") == "20-50"
    assert short_citation("Section 20-50. - Podiatric medicine defined.", None) == "20-50"


def test_label_without_a_citation_returns_the_label():
    """Never invent one -- PA labels are whole prose sentences."""
    label = "Appropriation.--The sum of $27,500 for the fiscal year"
    assert short_citation(label, "PA") == label[:60]
    # and the comma-permitting KS pattern must not grab the dollar amount either
    assert short_citation(label, "KS") == label[:60]
