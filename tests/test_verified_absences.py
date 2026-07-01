"""apply_verified_absences: turn the manifest into market_forces records."""

from __future__ import annotations

import json

import pipeline.extract.apply_verified_absences as av


def test_make_record_shape():
    r = av.make_record("electrician", "IL",
                       {"basis": "local_only", "citation": "65 ILCS 5/11-33-1", "note": "n"})
    assert r["state"] == "IL" and r["profession"] == "electrician"
    assert r["source"] == "verified_absence"        # provenance-marked
    assert r["basis"] == "local_only"
    lic = r["licensure"]
    # the pipeline's existing "no state regulation" representation
    assert lic["regulatory_model"]["value"] == "market_forces"
    assert lic["credential_type"]["value"] == "none"
    assert lic["is_mandatory"]["value"] is False
    assert lic["license_required"]["value"] is False
    # citation carried, quote intentionally empty (no state statute to quote)
    assert lic["regulatory_model"]["citation"] == "65 ILCS 5/11-33-1"
    assert lic["regulatory_model"]["quote"] == ""


def test_does_not_clobber_extracted(tmp_path, monkeypatch):
    monkeypatch.setattr(av, "STRUCTURED_DIR", tmp_path)
    monkeypatch.setattr(av, "MANIFEST", tmp_path / "m.yaml")
    (tmp_path / "m.yaml").write_text(
        "electrician:\n  IL: {basis: local_only, citation: '', note: ''}\n")
    # plant a real extracted record
    (tmp_path / "electrician").mkdir()
    (tmp_path / "electrician" / "IL.json").write_text(json.dumps({"source": "extracted", "state": "IL"}))
    av.apply(None, force=False)
    kept = json.loads((tmp_path / "electrician" / "IL.json").read_text())
    assert kept["source"] == "extracted"   # not overwritten
    # with --force it IS replaced
    av.apply(None, force=True)
    assert json.loads((tmp_path / "electrician" / "IL.json").read_text())["source"] == "verified_absence"


def test_manifest_bases_valid():
    import yaml
    m = yaml.safe_load(av.MANIFEST.read_text())
    valid = {"local_only", "not_regulated", "contractor_only"}
    for prof, states in m.items():
        for st, spec in states.items():
            assert spec["basis"] in valid, f"{prof}/{st} bad basis {spec['basis']}"
