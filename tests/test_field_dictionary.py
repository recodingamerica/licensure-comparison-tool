"""generate_field_dictionary: the methodology-tracks-code generator.

Locks in that the dictionary is built from the live Pydantic model (so it can't
drift): the 6-rung regulatory_model vocabulary and the Evidence example shape
must come straight from the model + a real record.
"""

from __future__ import annotations

import pytest

import pipeline.publish.generate_field_dictionary as gfd

pytestmark = pytest.mark.skipif(
    not (gfd.DISCOVERED_DIR / "dietetics.json").exists(),
    reason="needs the committed dietetics discovered schema",
)


def test_dictionary_tracks_model():
    d = gfd.build_dictionary("dietetics")
    assert d["profession"] == "dietetics"
    groups = {g["group"]: g for g in d["groups"]}
    assert {"licensure", "scope", "profession_specific"} <= set(groups)

    lic = {f["field"]: f for f in groups["licensure"]["fields"]}
    rm = lic["regulatory_model"]
    # the controlled vocabulary is read from the RegulatoryModel enum in code
    assert rm["type"] == "enum"
    assert set(rm["vocabulary"]) == {
        "market_forces", "voluntary_certification", "registration",
        "exemption", "mandatory_certification", "license",
    }
    # description is the model's own (tracks code)
    assert "UORF" in rm["meaning"]


def test_examples_carry_provenance():
    d = gfd.build_dictionary("dietetics")
    lic = {f["field"]: f for f in d["groups"][0]["fields"]}
    ex = lic["license_required"]["example"]
    # a real sampled Evidence object: value + verbatim quote + citation
    assert ex is not None and "value" in ex and "quote" in ex and "citation" in ex


def test_render_md_deterministic():
    d = gfd.build_dictionary("dietetics")
    assert gfd.render_md(d) == gfd.render_md(gfd.build_dictionary("dietetics"))
