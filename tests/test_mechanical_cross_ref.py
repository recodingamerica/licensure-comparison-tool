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


class TestBruteForceLinks:
    def test_best_scoring_sibling_wins(self, monkeypatch):
        # Unlike find_links (first-wins), brute_force_links picks the DENSEST match.
        blank_only = mx.ALL_STATES - {"CA"}
        corpora = {
            ("medicine", "CA"): " ".join(["prosthetist"] * 10),
            ("podiatry", "CA"): " ".join(["prosthetist"] * 40),  # densest
        }
        _patch_corpora(monkeypatch, corpora, have=blank_only)
        links = mx.brute_force_links("prosthetist_orthotist", {}, ["prosthetist"],
                                     ["medicine", "podiatry"], min_score=8)
        assert links == {"CA": ("podiatry", 40)}

    def test_min_score_threshold(self, monkeypatch):
        blank_only = mx.ALL_STATES - {"CA"}
        corpora = {("insurance_producer", "CA"): " ".join(["public adjuster"] * 5)}
        _patch_corpora(monkeypatch, corpora, have=blank_only)
        # 5 hits: passes at min_score 5, fails at 6
        assert mx.brute_force_links("public_adjuster", {}, ["public adjuster"],
                                    ["insurance_producer"], min_score=5)
        assert not mx.brute_force_links("public_adjuster", {}, ["public adjuster"],
                                        ["insurance_producer"], min_score=6)

    def test_self_skipped(self, monkeypatch):
        blank_only = mx.ALL_STATES - {"CA"}
        dense = " ".join(["surgical technologist"] * 20)
        _patch_corpora(monkeypatch, {("surgical_technologist", "CA"): dense}, have=blank_only)
        links = mx.brute_force_links("surgical_technologist", {}, ["surgical technologist"],
                                     ["surgical_technologist", "medicine"], min_score=8)
        assert links == {}

    def test_already_have_state_skipped(self, monkeypatch):
        dense = " ".join(["public adjuster"] * 20)
        _patch_corpora(monkeypatch, {("insurance_producer", "CA"): dense}, have=mx.ALL_STATES)
        links = mx.brute_force_links("public_adjuster", {}, ["public adjuster"],
                                     ["insurance_producer"], min_score=8)
        assert links == {}


class TestLoadPatterns:
    def test_known_profession_has_patterns(self):
        pats = mx.load_patterns("electrician")
        assert isinstance(pats, list) and pats  # non-empty

    def test_unknown_profession_empty(self):
        assert mx.load_patterns("definitely_not_a_profession_xyz") == []


class TestIncompleteOccupations:
    def test_all_complete_returns_empty(self, monkeypatch):
        monkeypatch.setattr(mx, "_have", lambda occ, ov: set(mx.ALL_STATES))
        assert mx.incomplete_occupations({}) == []

    def test_none_covered_returns_patterned_occs(self, monkeypatch):
        monkeypatch.setattr(mx, "_have", lambda occ, ov: set())
        occs = mx.incomplete_occupations({})
        assert "electrician" in occs and "plumbing" in occs
        assert occs == sorted(occs)


class TestWriteCandidateReport:
    def test_writes_rows_and_count(self, tmp_path):
        results = {
            "public_adjuster": {"GA": ("insurance_producer", 82), "TN": ("insurance_producer", 154)},
            "dental_assistant": {"AK": ("dentistry", 35)},
        }
        out = tmp_path / "report.md"
        n = mx.write_candidate_report(results, out, min_score=8)
        assert n == 3
        text = out.read_text()
        assert "3 candidate link(s) across 2 occupation(s)" in text
        assert "| public_adjuster | GA | insurance_producer | 82 |" in text
        assert "| dental_assistant | AK | dentistry | 35 |" in text

    def test_empty_results(self, tmp_path):
        out = tmp_path / "report.md"
        assert mx.write_candidate_report({}, out, min_score=8) == 0
        assert "0 candidate link(s)" in out.read_text()


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
