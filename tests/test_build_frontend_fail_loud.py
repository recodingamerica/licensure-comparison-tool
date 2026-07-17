"""A broken professions.yaml must RAISE at publish time, not silently publish fallbacks.

load_professions() reads via safe_load_unique, which raises on a duplicate/malformed key
(the #70 / WA-VA-NV dup-key fail-loud). Four build_frontend helpers used to wrap it in
`except Exception: return {}` — so a corrupt config published a fine-looking site with
title-case names and ZERO verified "no credential" negatives. These now propagate.
"""

import pytest

from pipeline.publish import build_frontend


class _Boom(Exception):
    pass


def _make_load_raise(monkeypatch):
    def boom():
        raise _Boom("duplicate profession key")
    monkeypatch.setattr(build_frontend, "load_professions", boom)


def test_no_credential_states_propagates(monkeypatch):
    _make_load_raise(monkeypatch)
    with pytest.raises(_Boom):
        build_frontend._no_credential_states("dentistry")


def test_profession_display_propagates(monkeypatch):
    _make_load_raise(monkeypatch)
    with pytest.raises(_Boom):
        build_frontend._profession_display("dentistry")


def test_profession_meta_propagates(monkeypatch):
    _make_load_raise(monkeypatch)
    with pytest.raises(_Boom):
        build_frontend._profession_meta("dentistry")


def test_all_profession_meta_propagates(monkeypatch):
    _make_load_raise(monkeypatch)
    with pytest.raises(_Boom):
        build_frontend._all_profession_meta()


def test_valid_config_still_works(monkeypatch):
    # The legitimate per-profession key fallback survives (unknown profession → title-case),
    # only the swallow-the-load-error path is gone.
    monkeypatch.setattr(build_frontend, "load_professions", lambda: {"dentistry": {"display": "Dentistry"}})
    assert build_frontend._profession_display("dentistry") == "Dentistry"
    assert build_frontend._profession_display("nurse_midwifery") == "Nurse Midwifery"  # fallback
    assert build_frontend._no_credential_states("unknown_prof") == {}
