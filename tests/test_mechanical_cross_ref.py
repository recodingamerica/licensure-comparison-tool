"""Tests for pipeline.discover.mechanical_cross_ref.

The LLM-free sibling cross-ref wires corpus_overrides.yaml when a sibling's
already-pulled corpus densely uses an occupation's LICENSING phrases. Locks in:
  - the density threshold (bare mentions below DENSITY don't trip a link)
  - first qualifying sibling wins (sibling order = preference order)
  - states we already have are skipped; sib == profession is skipped
  - CONFIG has no duplicate keys (the same silent last-wins bug we fixed in YAML
    once dropped a `professional_geology` term here)
"""

import ast
from pathlib import Path

import pipeline.discover.mechanical_cross_ref as mx


def _patch_corpora(monkeypatch, corpora, have):
    """corpora: {(sibling, state): text}; have: set of states already covered."""
    monkeypatch.setattr(mx, "_corpus_text", lambda prof, st: corpora.get((prof, st), ""))
    monkeypatch.setattr(mx, "_have", lambda prof, ov: set(have))


class TestFindLinks:
    def test_dense_sibling_makes_link(self, monkeypatch):
        blank_only = mx.ALL_STATES - {"CA"}
        dense = " ".join(["licensed electrician"] * mx.DENSITY)
        _patch_corpora(monkeypatch, {("construction_trades", "CA"): dense}, have=blank_only)
        links = mx.find_links("electrician", {}, ["licensed electrician"], ["construction_trades"])
        assert links == {"CA": ("construction_trades", mx.DENSITY)}

    def test_below_threshold_no_link(self, monkeypatch):
        blank_only = mx.ALL_STATES - {"CA"}
        sparse = " ".join(["licensed electrician"] * (mx.DENSITY - 1))
        _patch_corpora(monkeypatch, {("construction_trades", "CA"): sparse}, have=blank_only)
        links = mx.find_links("electrician", {}, ["licensed electrician"], ["construction_trades"])
        assert links == {}

    def test_bare_mention_does_not_count(self, monkeypatch):
        # corpus name-drops "electrician" many times but never the licensing phrase
        blank_only = mx.ALL_STATES - {"CA"}
        noise = " ".join(["electrician"] * 100)
        _patch_corpora(monkeypatch, {("construction_trades", "CA"): noise}, have=blank_only)
        links = mx.find_links("electrician", {}, ["licensed electrician"], ["construction_trades"])
        assert links == {}

    def test_first_qualifying_sibling_wins(self, monkeypatch):
        blank_only = mx.ALL_STATES - {"CA"}
        dense = " ".join(["licensed plumber"] * mx.DENSITY)
        corpora = {
            ("construction_trades", "CA"): dense,
            ("hvac", "CA"): dense,
        }
        _patch_corpora(monkeypatch, corpora, have=blank_only)
        links = mx.find_links("plumbing", {}, ["licensed plumber"],
                              ["construction_trades", "hvac"])
        assert links["CA"][0] == "construction_trades"

    def test_already_have_state_skipped(self, monkeypatch):
        # CA is in `have`, so it's never blank → never linked even if dense
        dense = " ".join(["licensed electrician"] * mx.DENSITY)
        _patch_corpora(monkeypatch, {("construction_trades", "CA"): dense}, have=mx.ALL_STATES)
        links = mx.find_links("electrician", {}, ["licensed electrician"], ["construction_trades"])
        assert links == {}

    def test_self_sibling_skipped(self, monkeypatch):
        blank_only = mx.ALL_STATES - {"CA"}
        dense = " ".join(["licensed electrician"] * mx.DENSITY)
        _patch_corpora(monkeypatch, {("electrician", "CA"): dense}, have=blank_only)
        # the only sibling IS the profession → skipped, no link
        links = mx.find_links("electrician", {}, ["licensed electrician"], ["electrician"])
        assert links == {}


class TestConfigIntegrity:
    def test_density_is_positive_int(self):
        assert isinstance(mx.DENSITY, int) and mx.DENSITY > 0

    def test_no_duplicate_config_keys_in_source(self):
        # Runtime CONFIG silently dedupes; parse the source to catch a re-added dup.
        src = Path(mx.__file__).read_text()
        tree = ast.parse(src)
        config_keys = None
        for node in ast.walk(tree):
            # CONFIG: dict[str, dict] = {...}  -> AnnAssign (also accept plain Assign)
            targets = node.targets if isinstance(node, ast.Assign) else (
                [node.target] if isinstance(node, ast.AnnAssign) else [])
            if (targets
                    and any(getattr(t, "id", "") == "CONFIG" for t in targets)
                    and isinstance(getattr(node, "value", None), ast.Dict)):
                config_keys = [k.value for k in node.value.keys if isinstance(k, ast.Constant)]
                break
        assert config_keys is not None, "could not find CONFIG dict literal"
        dupes = {k for k in config_keys if config_keys.count(k) > 1}
        assert not dupes, f"duplicate CONFIG keys: {dupes}"
