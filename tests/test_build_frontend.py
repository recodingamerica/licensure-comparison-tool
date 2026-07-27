"""Tests for build_frontend's credential_type/is_mandatory derivation.

The build_frontend layer derives the orthogonal (credential_type, is_mandatory)
view from the legacy single-axis regulatory_model when the new fields aren't
directly populated. Lock in this back-compat behavior so existing podiatry
data gets the new columns for free.
"""

import pytest

from pipeline.publish import build_frontend as bf
from pipeline.publish.build_frontend import (
    _derive_credential_and_mandatory,
    normalize_citation,
    hoist_row,
)


class TestProvenance:
    def _rec(self, **extra):
        return {"state": "IL", "profession": "electrician",
                "licensure": {"regulatory_model": {"value": "market_forces"}}, **extra}

    def test_extracted_default_basis(self):
        assert hoist_row(self._rec())["data_basis"] == "extracted"

    def test_verified_absence_basis_surfaced(self):
        row = hoist_row(self._rec(source="verified_absence", basis="local_only",
                                  note="No statewide license."))
        assert row["data_basis"] == "verified_absence"
        assert row["absence_basis"] == "local_only"
        assert row["absence_note"] == "No statewide license."
        assert row["coverage_gap"] is False   # still a real row, not a gap


class TestDerivationFromLegacyRegulatoryModel:
    @pytest.mark.parametrize("rm, expected", [
        ("license",                  ("license", True)),
        ("mandatory_certification",  ("certification", True)),
        ("voluntary_certification",  ("certification", False)),
        ("registration",             ("registration", True)),
        ("market_forces",            ("none", False)),
        ("exemption",                ("exemption", None)),
    ])
    def test_each_rung_derives_correctly(self, rm, expected):
        lic = {"regulatory_model": {"value": rm, "quote": "q", "citation": "c"}}
        assert _derive_credential_and_mandatory(lic) == expected

    def test_missing_regulatory_model_returns_none(self):
        assert _derive_credential_and_mandatory({}) == (None, None)

    def test_invalid_regulatory_model_value_returns_none(self):
        lic = {"regulatory_model": {"value": "not_a_real_rung", "quote": "q", "citation": "c"}}
        assert _derive_credential_and_mandatory(lic) == (None, None)


class TestDirectFieldsPreferred:
    """If a future extraction populates credential_type + is_mandatory directly,
    we use those rather than re-deriving from regulatory_model."""

    def test_direct_credential_type_overrides_derivation(self):
        lic = {
            "regulatory_model": {"value": "license", "quote": "q", "citation": "c"},
            "credential_type": {"value": "registration", "quote": "q2", "citation": "c2"},
            "is_mandatory": {"value": False, "quote": "q3", "citation": "c3"},
        }
        assert _derive_credential_and_mandatory(lic) == ("registration", False)

    def test_direct_partial_population(self):
        """If only one of the new fields is populated, the other comes from that
        same record (not from re-deriving regulatory_model)."""
        lic = {
            "regulatory_model": {"value": "license", "quote": "q", "citation": "c"},
            "credential_type": {"value": "license", "quote": "q2", "citation": "c2"},
            # is_mandatory absent
        }
        ct, im = _derive_credential_and_mandatory(lic)
        assert ct == "license"
        assert im is None  # we don't half-derive


class TestNormalizeCitation:
    """`normalize_citation` cleans up the LLM's per-state citation strings
    so the published JSON ships a consistent display form. Idempotent."""

    @pytest.mark.parametrize("raw, want", [
        # Bracketed (KY style)
        ("[314.031]",                            "314.031"),
        ("[34-24-704]",                          "34-24-704"),
        # Trailing period only
        ("32-827.",                              "32-827"),
        ("Section 2474.",                        "Section 2474"),
        # `§ NN. Title` (Vermont style) — strip the title, keep the section
        ("§ 324. Prohibitions; penalties",        "§ 324"),
        ("§ 1721. Definitions",                   "§ 1721"),
        # `§ 324.5` is a sub-section, NOT a title — leave it alone
        ("§ 324.5",                               "§ 324.5"),
        # `Section NN - Title -- ...` (Utah / Nebraska style)
        ("Section 301 - License required -- License classifications.",
         "Section 301"),
        ("Section 302 - Qualifications to practice podiatry.",
         "Section 302"),
        # ` -- ` separator alone
        ("65-2002 -- Definitions",                "65-2002"),
        # UMBRELLA prefix preserved, but body cleaned
        ("UMBRELLA / 38-167 - Boards; designated; change in name; effect.",
         "UMBRELLA / 38-167"),
        # Clean inputs pass through unchanged (idempotent)
        ("311.400",                               "311.400"),
        ("RS 37:912",                             "RS 37:912"),
        ("20-50a",                                "20-50a"),
        # Empty / whitespace
        ("",                                      ""),
        ("   ",                                   ""),
    ])
    def test_normalize(self, raw, want):
        assert normalize_citation(raw) == want

    def test_idempotent(self):
        """Applying twice yields the same result as applying once."""
        for raw in [
            "[314.031]",
            "§ 324. Prohibitions",
            "Section 301 - License required",
            "UMBRELLA / 38-167 - Boards",
        ]:
            once = normalize_citation(raw)
            twice = normalize_citation(once)
            assert once == twice


class TestListItemsGetQuoteSpans:
    """Highlights are computed ONCE, in the build, and passed to the frontend as
    quote_spans. A node the walker skips therefore has no highlight anywhere, and the UI
    cannot recover it — it does not re-search the statute text.

    is_evidence_node requires {value, quote, citation}. A disciplinary ground names its
    value `description` and an exam names it `name`, so neither qualified and every list
    item silently lost its highlight: 0 of 8,059 grounds carried spans against 86% of
    plain fields. Reported for architecture/ID, "violation_of_chapter_or_rules".
    """

    def _record(self):
        return {
            "licensure": {
                # a plain Evidence node — always worked
                "regulatory_model": {
                    "value": "license",
                    "quote": "a license is required to practice architecture",
                    "citation": "54-301",
                },
                # a LIST item: quotes the statute, but calls its value `description`
                "disciplinary_grounds": [
                    {
                        "short_label": "violation_of_chapter_or_rules",
                        "description": "Violating any provisions of this chapter",
                        "quote": "Violating any of the provisions of this chapter",
                        "citation": "54-314",
                        "category": "Statutory or Rule Violation",
                    }
                ],
                "exams": [
                    {"name": "ARE", "quote": "shall pass the examination", "citation": "54-305"}
                ],
            }
        }

    def _sections(self):
        return [
            {"citation": "54-301", "text": "In Idaho a license is required to practice architecture."},
            {"citation": "54-314", "text": "Grounds: Violating any of the provisions of this chapter or rules."},
            {"citation": "54-305", "text": "Each applicant shall pass the examination prescribed."},
        ]

    def test_disciplinary_ground_gets_spans(self):
        rec = self._record()
        bf._annotate_quote_spans(rec, self._sections())
        ground = rec["licensure"]["disciplinary_grounds"][0]
        assert ground.get("quote_spans"), "list item got no highlight — the reported bug"
        s, e = ground["quote_spans"][0]
        assert self._sections()[1]["text"][s:e] == ground["quote"]

    def test_exam_gets_spans(self):
        rec = self._record()
        bf._annotate_quote_spans(rec, self._sections())
        assert rec["licensure"]["exams"][0].get("quote_spans")

    def test_plain_evidence_still_gets_spans(self):
        rec = self._record()
        bf._annotate_quote_spans(rec, self._sections())
        assert rec["licensure"]["regulatory_model"].get("quote_spans")


class TestEveryCoreFieldIsReachableInTheUI:
    """A field the pipeline extracts, quotes and cites — but that no UI row renders — is
    invisible: the table can show its value while its evidence is unreachable anywhere.

    That happened silently to advisory_board.{exists,name,authority}, renewal_fee_usd,
    national_certification and national_association. It was found by accident chasing a
    missing highlight; this finds it on purpose.

    Only CORE (licensure/scope) fields: profession_specific fields render generically from
    the discovered schema, so they can't go missing this way.
    """

    NEST = {"post_degree_experience": "post_degree", "continuing_education": "CE"}

    # Fields that exist in the data and are deliberately NOT given their own Sheet row.
    # Adding one here is a decision to leave data unexposed — state the reason.
    KNOWN_UNEXPOSED = {
        # Structural detail about the board itself rather than a licensing requirement;
        # the Sheet shows issuing_authority instead. See #34 discussion.
        "regulatory_authority.type",
        "regulatory_authority.name",
        "regulatory_authority.umbrella_agency",
        # Non-licensure alternative-regulation signals; no column surfaces them either.
        "alternative_regulation.insurance_required",
        "alternative_regulation.establishment_regulation_required",
        "alternative_regulation.bonding_required",
    }

    def _label(self, path: str) -> str | None:
        if not path.startswith(("licensure.", "scope.")):
            return None
        if path.startswith("scope."):
            return path[len("scope."):]
        rest = path[len("licensure."):]
        if "." not in rest:
            return rest
        group, leaf = rest.split(".", 1)
        return f"{self.NEST.get(group, group)}.{leaf}"

    def test_no_core_field_is_unreachable(self):
        import glob, json, re
        from pathlib import Path

        present: set[str] = set()
        for f in glob.glob("pipeline/results/structured/*/*.json"):
            if f.endswith("_summary.json"):
                continue
            try:
                rec = json.loads(Path(f).read_text())
            except Exception:
                continue

            def walk(node, path=""):
                if isinstance(node, dict):
                    if "value" in node and ("quote" in node or "citation" in node):
                        lb = self._label(path)
                        if lb:
                            present.add(lb)
                        return
                    for k, v in node.items():
                        walk(v, f"{path}.{k}" if path else k)

            walk(rec)

        sheet = Path(
            "pipeline/publish/web/src/components/state-detail-dialog.tsx"
        ).read_text()
        rendered = set(re.findall(r'<EvidenceRow\s+label="([^"]+)"', sheet))

        unreachable = present - rendered - self.KNOWN_UNEXPOSED
        assert not unreachable, (
            "these fields carry extracted, quoted, cited data that NO Sheet row renders — "
            "the table can show the value while its evidence is unreachable: "
            f"{sorted(unreachable)}"
        )
