"""Tests for extract_state.finalize_record — the post-parse step SHARED by the
sync (extract_one) and batch (_parse_and_write) extraction paths (issue #62).

Two things must hold for both backends to publish identical data:
  1. regulatory_model.value is DERIVED from credential_type + scope_protection,
     not the model's free pick.
  2. When that derivation overrides the model's pick, the model's now-orphaned
     quote/citation are cleared and the node is marked `derived` (its supporting
     evidence lives on credential_type + scope_protection). A stale quote must
     never survive under a value it argues against.
"""

from pipeline.extract import extract_state
from pipeline.extract import extract_state_batch


def _record(rm_value, ct_value, sp_value, rm_quote="MODEL PICK QUOTE"):
    """A minimal Evidence-shaped record. The credential_type / scope_protection
    quotes are strings we can plant verbatim in the corpus so they verify."""
    return {
        "licensure": {
            "regulatory_model": {
                "value": rm_value,
                "quote": rm_quote,
                "citation": "1-1",
            },
            "credential_type": {
                "value": ct_value,
                "quote": "the board shall issue a certificate",
                "citation": "1-2",
            },
            "scope_protection": {
                "value": sp_value,
                "quote": "no scope restriction applies",
                "citation": "1-3",
            },
        }
    }


CORPUS = (
    "MODEL PICK QUOTE. the board shall issue a certificate. "
    "no scope restriction applies."
)


def test_override_clears_orphaned_quote_and_marks_derived():
    # credential_type=certification + scope_protection=false → voluntary_certification,
    # overriding the model's "license" pick. The license-supporting quote must go.
    rec = _record("license", "certification", False)
    extract_state.finalize_record(rec, "KS", "emergency_medical_technician", CORPUS)
    rm = rec["licensure"]["regulatory_model"]
    assert rm["value"] == "voluntary_certification"
    assert rm["quote"] is None
    assert rm["citation"] is None
    assert rm["derived"] is True
    # A derived node has no quote to verify, so it must NOT carry an unverified flag.
    assert "unverified" not in rm


def test_no_override_keeps_model_quote():
    # credential_type=license + scope_protection=true → license == model pick.
    # No override, so the model's quote is preserved untouched.
    rec = _record("license", "license", True)
    extract_state.finalize_record(rec, "XX", "medicine", CORPUS)
    rm = rec["licensure"]["regulatory_model"]
    assert rm["value"] == "license"
    assert rm["quote"] == "MODEL PICK QUOTE"
    assert rm["citation"] == "1-1"
    assert rm.get("derived") is not True


def test_finalize_is_idempotent_on_derived_node():
    # Re-running finalize (as the backfill does) over an already-derived record
    # must not re-flag the null-quote node unverified, and must leave it clean.
    rec = _record("license", "certification", True)  # → mandatory_certification
    extract_state.finalize_record(rec, "DE", "emergency_medical_technician", CORPUS)
    first = dict(rec["licensure"]["regulatory_model"])
    extract_state.finalize_record(rec, "DE", "emergency_medical_technician", CORPUS)
    second = rec["licensure"]["regulatory_model"]
    assert first == second
    assert second["value"] == "mandatory_certification"
    assert second["quote"] is None
    assert "unverified" not in second


def test_both_paths_share_one_finalize_function():
    # The whole point of #62: sync and batch must call the SAME function object,
    # so their post-parse processing cannot drift.
    assert extract_state_batch.finalize_record is extract_state.finalize_record


def test_backend_params_are_shared_constants():
    # Both request builders must reference the shared token/temperature constants.
    assert extract_state.MAX_OUTPUT_TOKENS == extract_state_batch.MAX_OUTPUT_TOKENS
    assert extract_state.EXTRACT_TEMPERATURE == extract_state_batch.EXTRACT_TEMPERATURE
