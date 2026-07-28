"""A highlight pointing at the wrong words is worse than no highlight.

Three separate upstream causes were found producing the same symptom (an unlabelled
section, one citation shared by two versions of a section, a quote the model mis-cited),
so the guard checks the OUTPUT instead of adding a fourth special case: every published
span must actually cover its own quote, resolved exactly the way the UI resolves it
(`sections[citation] = s` in a loop, so LAST-wins, preferring `quote_section`).
"""

from __future__ import annotations

from pipeline.publish.build_frontend import drop_misindexed_spans


def _rec(quote, citation, spans, quote_section=None):
    node = {"value": True, "quote": quote, "citation": citation, "quote_spans": spans}
    if quote_section:
        node["quote_section"] = quote_section
    return {"licensure": {"field": node}}, node


def test_correct_span_is_kept():
    text = "AAA the board may waive the examination BBB"
    rec, node = _rec("the board may waive the examination", "1-1", [[4, 39]])
    assert drop_misindexed_spans(rec, [{"citation": "1-1", "text": text}]) == 0
    assert node["quote_spans"] == [[4, 39]]


def test_span_covering_different_text_is_dropped():
    """The DE/OK shape: offsets that land on unrelated words in the resolved section."""
    text = "the board shall have the power to formulate rules and regulations"
    rec, node = _rec("there is hereby created the Board of Dentistry", "328.15", [[0, 40]])
    assert drop_misindexed_spans(rec, [{"citation": "328.15", "text": text}]) == 1
    assert "quote_spans" not in node


def test_duplicate_citation_resolves_last_wins_like_the_ui():
    """DE ships two versions of § 1101 under one citation. The span indexes into the
    FIRST, but the UI resolves to the LAST -- so it must be dropped."""
    first = {"citation": "§ 1101", "text": "division shall mean the state division of professional regulation"}
    last = {"citation": "§ 1101", "text": "wholly different contingent text about dismissal of patients"}
    rec, node = _rec("division shall mean the state division", "§ 1101", [[0, 37]])
    assert drop_misindexed_spans(rec, [first, last]) == 1
    assert "quote_spans" not in node


def test_quote_section_takes_precedence_over_citation():
    """Umbrella case: the node cites one thing, the span indexes into another, and
    quote_section names which -- so it must be honoured when resolving."""
    cited = {"citation": "147.55", "text": "nothing relevant here at all"}
    actual = {"citation": "UMBRELLA / Chapter 147", "text": "fraud in procuring a license"}
    rec, node = _rec("fraud in procuring a license", "147.55", [[0, 28]],
                     quote_section="UMBRELLA / Chapter 147")
    assert drop_misindexed_spans(rec, [cited, actual]) == 0
    assert node["quote_spans"] == [[0, 28]]


def test_multi_span_quote_is_judged_on_all_spans_together():
    """A quote stored as fragments must be compared as the concatenation, not span[0]."""
    text = "the board may waive XXXX the examination requirement"
    rec, node = _rec("the board may waive the examination requirement", "1-1",
                     [[0, 19], [25, 51]])
    assert drop_misindexed_spans(rec, [{"citation": "1-1", "text": text}]) == 0
    assert len(node["quote_spans"]) == 2


def test_unresolvable_target_is_dropped():
    """No section answers to this citation, so the spans can never render correctly."""
    rec, node = _rec("some quote", "9-9", [[0, 10]])
    assert drop_misindexed_spans(rec, [{"citation": "1-1", "text": "some quote"}]) == 1
    assert "quote_spans" not in node


def test_nodes_without_spans_are_untouched():
    rec, node = _rec("some quote", "1-1", None)
    node.pop("quote_spans")
    assert drop_misindexed_spans(rec, [{"citation": "1-1", "text": "some quote"}]) == 0
