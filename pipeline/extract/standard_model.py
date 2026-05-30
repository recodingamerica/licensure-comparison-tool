"""Universal Pydantic pieces — fields that exist for essentially every
licensed profession. Every leaf field is wrapped in an Evidence[T] carrier
so each claim is backed by a verbatim quote from the source statute.

Per-profession richness lives in a discovered model that pass-2 composes
alongside this base; those fields use the same Evidence[T] shape.

Concrete Evidence subclasses (StrEvidence, BoolEvidence, ...) are used
instead of a single generic so the JSON schema sent to the LLM stays clean
— LiteLLM/Anthropic don't always handle Pydantic generics gracefully.

The regulatory_model / title_protection / scope_protection fields and the
disciplinary_grounds list are aligned with Utah OPLR's "Universal Occupational
Regulation Framework" (UORF) — a six-rung ladder of regulatory strictness.
Knowing where each (state, profession) sits on that ladder is the descriptive
input the prescriptive UORF analysis consumes.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterator

from pydantic import BaseModel, Field


# ---------- Evidence-tree walker ----------

_EVIDENCE_KEYS = frozenset({"value", "quote", "citation"})


def is_evidence_node(node: Any) -> bool:
    """True iff `node` is a dict with the Evidence-carrier shape."""
    return isinstance(node, dict) and _EVIDENCE_KEYS.issubset(node.keys())


def iter_evidence(
    node: Any, path: tuple[str | int, ...] = ()
) -> Iterator[tuple[tuple[str | int, ...], dict]]:
    """Yield (path, evidence_dict) for every Evidence-shaped node in a tree.

    `path` is a tuple of keys/indices from the root to the node, so callers
    that need to know "which field is this Evidence carrying" can read it
    directly. Single point of truth for what counts as an Evidence node —
    the verifier, span annotator, review CSV builder, and repair script all
    walk the same way.
    """
    if isinstance(node, dict):
        if is_evidence_node(node):
            yield path, node
            return
        for k, v in node.items():
            yield from iter_evidence(v, path + (k,))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from iter_evidence(v, path + (i,))


# ---------- Evidence carriers ----------

class StrEvidence(BaseModel):
    value: str
    quote: str = Field(description="Verbatim phrase from the statute supporting `value`")
    citation: str = Field(description="Short citation, e.g. '20-50' or '§ 461.003'")


class BoolEvidence(BaseModel):
    value: bool
    quote: str
    citation: str


class IntEvidence(BaseModel):
    value: int
    quote: str
    citation: str


class StrListEvidence(BaseModel):
    value: list[str]
    quote: str
    citation: str


# ---------- UORF regulatory ladder ----------

class RegulatoryModel(str, Enum):
    """Six-rung UORF ladder, low → high strictness.

    Legacy single-axis representation kept for back-compat with existing
    extracted data. New extractions should also populate `credential_type`
    and `is_mandatory` (see below) — those decompose this rung into two
    orthogonal axes that are easier to filter and that match the meeting
    framing ("license / cert / registry × mandatory / voluntary").
    """
    MARKET_FORCES = "market_forces"
    VOLUNTARY_CERTIFICATION = "voluntary_certification"
    REGISTRATION = "registration"
    EXEMPTION = "exemption"
    MANDATORY_CERTIFICATION = "mandatory_certification"
    LICENSE = "license"


class RegulatoryModelEvidence(BaseModel):
    value: RegulatoryModel = Field(
        description=(
            "Which UORF model the state currently applies to this profession. "
            "license=must be licensed to practice; mandatory_certification=must hold state cert "
            "to claim title or practice scope; registration=must register but no qualification "
            "test; exemption=narrow carve-out from a broader practice act; voluntary_certification="
            "state cert is optional and only protects a title; market_forces=no state regulation."
        ),
    )
    quote: str
    citation: str


# ---------- Orthogonal decomposition: credential type × mandatory? ----------
# Meeting 2026-05-12: "how do we systematically capture whether something is a
# license, certification, or registry; whether it is mandatory or voluntary".
# Splitting the UORF rung into two orthogonal Enums + bools lets downstream
# filter on either axis independently ("all certifications regardless of
# mandatory", "all mandatory regulation regardless of credential shape").

class CredentialType(str, Enum):
    """Shape of the credential the state issues, ignoring whether it's mandatory."""
    NONE = "none"                       # No state-issued credential at all
    REGISTRATION = "registration"        # Practitioner registers; no qualification gate
    CERTIFICATION = "certification"      # State certifies that holder meets standards
    LICENSE = "license"                  # State grants explicit permission to practice
    EXEMPTION = "exemption"              # Narrow carve-out from a broader practice act


class CredentialTypeEvidence(BaseModel):
    value: CredentialType = Field(
        description=(
            "Shape of the state-issued credential for this profession, independent of "
            "whether holding it is mandatory. "
            "license=state grants explicit permission to practice; "
            "certification=state certifies the holder meets qualification standards (may or may "
            "not be required to practice); "
            "registration=practitioner must register on a roster with no qualification test; "
            "exemption=this profession is exempted from a broader practice-act regime; "
            "none=no state credential exists."
        ),
    )
    quote: str
    citation: str


# Mapping the legacy single-axis ladder to (credential_type, is_mandatory).
# Used in tests + as a back-compat derivation when only one is populated.
REGULATORY_MODEL_DECOMPOSITION: dict[RegulatoryModel, tuple[CredentialType, bool | None]] = {
    RegulatoryModel.MARKET_FORCES:          (CredentialType.NONE,          False),
    RegulatoryModel.VOLUNTARY_CERTIFICATION:(CredentialType.CERTIFICATION, False),
    RegulatoryModel.REGISTRATION:           (CredentialType.REGISTRATION,  True),
    RegulatoryModel.EXEMPTION:              (CredentialType.EXEMPTION,     None),
    RegulatoryModel.MANDATORY_CERTIFICATION:(CredentialType.CERTIFICATION, True),
    RegulatoryModel.LICENSE:                (CredentialType.LICENSE,       True),
}


def decompose_regulatory_model(rung: RegulatoryModel) -> tuple[CredentialType, bool | None]:
    """Return (credential_type, is_mandatory) for a UORF rung.

    For EXEMPTION the mandatory question is undefined (the exemption itself
    is the state's decision; what's being exempted from is the broader regime),
    so is_mandatory comes back None.
    """
    return REGULATORY_MODEL_DECOMPOSITION[rung]


class DisciplinaryGround(BaseModel):
    """One ground on which the board may discipline a licensee. Captured as a
    list of these per state — typically 5-15 grounds in any one statute."""
    short_label: str = Field(description="snake_case key, e.g. 'fraud_in_obtaining_license'")
    description: str = Field(description="One-line plain-English description")
    quote: str
    citation: str


# ---------- Regulatory authority structure (meeting Q2) ----------
# Free-text issuing_authority loses structure across states: "State Board of
# Podiatry", "Department of Public Health", "Board within the Division of
# Occupational Licensing within the Department of Commerce" all live in one
# string. Decomposing into name + type + umbrella lets us filter/compare:
# "all states where the issuing authority is a standalone board" vs "all
# states where podiatry is under the medical board" etc.

class AuthorityType(str, Enum):
    """Shape of the regulatory authority that issues credentials."""
    STANDALONE_BOARD = "standalone_board"      # e.g., "State Board of Podiatry"
    SHARED_BOARD = "shared_board"              # covers multiple professions, e.g., "Board of Healing Arts"
    DIVISION_OF_DEPARTMENT = "division"        # e.g., "Division of Occupational Licensing"
    DEPARTMENT = "department"                  # e.g., "Department of Health"
    JOINT = "joint"                            # multiple bodies share regulation
    OTHER = "other"


class AuthorityTypeEvidence(BaseModel):
    value: AuthorityType = Field(
        description=(
            "Classify the issuing authority's structural shape. "
            "standalone_board=the board is dedicated to this one profession (e.g. 'State Board of Podiatry'). "
            "shared_board=the board governs multiple related professions (e.g. 'Board of Healing Arts' covering medicine + osteopathy + podiatry). "
            "division=a named division/office within a larger licensing department. "
            "department=a state cabinet department (e.g., 'Department of Public Health') directly issues credentials with no named board. "
            "joint=two or more authorities share regulation (e.g., a board + a department both involved). "
            "other=structure doesn't fit the above."
        ),
    )
    quote: str
    citation: str


class RegulatoryAuthority(BaseModel):
    """Structured representation of who regulates this profession in this state.
    Populated alongside the legacy free-text issuing_authority for back-compat."""

    name: StrEvidence | None = Field(
        default=None,
        description="Canonical name of the immediate authority (e.g., 'State Board of Podiatry').",
    )
    type: AuthorityTypeEvidence | None = Field(
        default=None,
        description="Structural classification of the immediate authority.",
    )
    umbrella_agency: StrEvidence | None = Field(
        default=None,
        description=(
            "Higher-level agency that contains the immediate authority, if any. "
            "Example: 'Division of Occupations and Professions, Department of Commerce'. "
            "Null for standalone boards that don't sit inside a larger department."
        ),
    )


# ---------- Alternatives to credentialing (Obama 2015 typology) ----------
# Obama 2015 White House report ("Occupational Licensing: A Framework for
# Policymakers") frames bonding, insurance, and establishment-level regulation
# as ALTERNATIVES to occupational credentials. They can also coexist with a
# credential (a state may license a contractor AND require bonding). Captured
# separately from credential_type so a state's full regulatory posture is
# visible. See docs/lit_review/README.md.

class AlternativeRegulation(BaseModel):
    """Non-credential regulatory mechanisms the state imposes for this profession."""

    bonding_required: BoolEvidence | None = Field(
        default=None,
        description=(
            "Does the statute require the practitioner or firm to post a bond "
            "(funds against which consumer claims can be made)? Independent of "
            "whether a credential is also required."
        ),
    )
    insurance_required: BoolEvidence | None = Field(
        default=None,
        description=(
            "Does the statute require the practitioner or firm to carry insurance "
            "(e.g., professional liability, surety insurance)?"
        ),
    )
    establishment_regulation_required: BoolEvidence | None = Field(
        default=None,
        description=(
            "Does the statute regulate the ESTABLISHMENT / FIRM (e.g., facility "
            "license, mandatory inspection of premises) as a route to consumer "
            "protection, independent of any practitioner credential?"
        ),
    )


# ---------- Citation list (no Evidence wrapper — these ARE the citations) ----------

class Citation(BaseModel):
    cite: str
    kind: str | None = None


# ---------- Sub-structures ----------

class EducationRequirement(BaseModel):
    degree_required: StrEvidence | None = None
    accrediting_body: StrEvidence | None = None


class PostDegreeExperience(BaseModel):
    """Residency / supervised practice / apprenticeship — name varies, structure doesn't."""
    required: BoolEvidence | None = None
    duration: StrEvidence | None = Field(
        default=None,
        description="e.g. '24 months', '1 year', '2,000 hours' (free text — units vary)",
    )
    kind: StrEvidence | None = Field(
        default=None,
        description="e.g. 'podiatric residency', 'accounting work experience', 'AXP'",
    )


class ContinuingEducation(BaseModel):
    required: BoolEvidence | None = None
    hours_per_period: IntEvidence | None = None
    period_years: IntEvidence | None = None
    topical_requirements: StrListEvidence | None = Field(
        default=None,
        description="Specific topical CE requirements, e.g. ['1.5 hrs opioid', 'ethics']",
    )


class Renewal(BaseModel):
    interval_years: IntEvidence | None = Field(
        default=None,
        description="Most states are 1 or 2",
    )


class Reciprocity(BaseModel):
    available: BoolEvidence | None = None
    requirements: StrEvidence | None = Field(
        default=None,
        description="Free-form summary",
    )


class Exam(BaseModel):
    name: str
    required: bool = True
    notes: str | None = None
    jurisdiction: str | None = Field(
        default=None,
        description=(
            "Where the exam is administered / who owns it — e.g. 'NBPME (national)', "
            "'state board (in-state)', 'NCLEX-RN (national)'. Use the statute's "
            "language; null if the source doesn't say."
        ),
    )
    permitted_attempts: int | None = Field(
        default=None,
        description="Max attempts allowed before re-qualification. Null if not specified.",
    )
    quote: str = Field(description="Verbatim phrase mentioning this exam")
    citation: str


class AdvisoryBoard(BaseModel):
    """Some states delegate licensure to a generic board (e.g. 'Board of Medical
    Examiners') and add a profession-specific advisory body alongside it. This
    captures whether such an advisory board exists and what authority it has."""
    exists: BoolEvidence | None = Field(
        default=None,
        description=(
            "True if a profession-specific advisory body exists alongside the main "
            "licensing board. False if the licensing board itself is profession-specific "
            "(no separate advisory body needed)."
        ),
    )
    name: StrEvidence | None = Field(
        default=None,
        description="Name of the advisory board, e.g. 'Podiatry Advisory Committee'.",
    )
    authority: StrEvidence | None = Field(
        default=None,
        description=(
            "Authority the advisory board has, in the statute's own words — e.g. "
            "'advisory only', 'rulemaking subject to board approval', 'disciplinary "
            "recommendations'. Free text from the statute."
        ),
    )


# ---------- Top-level base components ----------

class LicensureRequirements(BaseModel):
    license_required: BoolEvidence | None = None
    issuing_authority: StrEvidence | None = None
    regulatory_authority: RegulatoryAuthority | None = Field(
        default=None,
        description=(
            "Structured decomposition of the issuing authority — name, type "
            "(standalone board / shared board / division / department / joint), "
            "and any umbrella agency it sits within. Populated alongside the "
            "legacy free-text issuing_authority for back-compat."
        ),
    )
    age_minimum: IntEvidence | None = None
    moral_character_required: BoolEvidence | None = None
    education: EducationRequirement | None = None
    post_degree_experience: PostDegreeExperience | None = None
    exams: list[Exam] = Field(default_factory=list)
    renewal: Renewal | None = None
    renewal_fee_usd: IntEvidence | None = Field(
        default=None,
        description=(
            "License renewal fee in US dollars (integer). Many statutes leave the "
            "amount to the board's discretion — leave null in that case."
        ),
    )
    continuing_education: ContinuingEducation | None = None
    reciprocity: Reciprocity | None = None

    # Universal fields aligned with Atharv's cross-comparison schema. These
    # round out the universal set so every profession's profile carries the
    # same row labels.
    advisory_board: AdvisoryBoard | None = Field(
        default=None,
        description=(
            "Profession-specific advisory body sitting alongside the main licensing "
            "board, when one exists. Populated for states that delegate licensure "
            "to a generic board and add a specialty advisory committee."
        ),
    )
    national_certification: StrEvidence | None = Field(
        default=None,
        description=(
            "Name of a national CERTIFICATION the state recognizes or requires, "
            "e.g. 'American Board of Podiatric Surgery (ABPS)' or 'National Board "
            "of Podiatric Medical Examiners (NBPME)'. The certifying body, NOT the "
            "association. Null if the statute doesn't reference one."
        ),
    )
    national_association: StrEvidence | None = Field(
        default=None,
        description=(
            "Professional ASSOCIATION the state references (e.g. for accreditation "
            "or CE provider approval) — 'American Podiatric Medical Association "
            "(APMA)', 'American Dental Association (ADA)'. Distinct from the "
            "certifying body. Null if not referenced."
        ),
    )

    # UORF-mapped fields (legacy single-axis rung; new extractions also populate
    # credential_type + is_mandatory below for orthogonal filtering)
    regulatory_model: RegulatoryModelEvidence | None = Field(
        default=None,
        description="Which UORF model the state applies to this profession (license / mandatory_cert / registration / etc).",
    )
    credential_type: CredentialTypeEvidence | None = Field(
        default=None,
        description=(
            "What SHAPE of credential does the state issue, independent of whether holding it is "
            "mandatory? license / certification / registration / exemption / none. Pairs with "
            "is_mandatory to decompose the legacy regulatory_model rung."
        ),
    )
    is_mandatory: BoolEvidence | None = Field(
        default=None,
        description=(
            "Is the credential MANDATORY to practice (or claim the title) in this state? "
            "True if practicing without it is prohibited; False if optional (e.g., voluntary "
            "certification that only protects the title for those who hold it)."
        ),
    )
    title_protection: BoolEvidence | None = Field(
        default=None,
        description=(
            "Does the state restrict use of the profession's title to licensees? "
            "True if unlicensed people may NOT call themselves the protected title (e.g. 'podiatrist', 'CPA')."
        ),
    )
    scope_protection: BoolEvidence | None = Field(
        default=None,
        description=(
            "Does the state restrict practice of the profession's scope to licensees? "
            "True if performing the scope without a license is prohibited (independent of title use)."
        ),
    )
    disciplinary_grounds: list[DisciplinaryGround] = Field(
        default_factory=list,
        description="Grounds on which the board may discipline a licensee. Typical statutes list 5-15.",
    )

    alternative_regulation: AlternativeRegulation | None = Field(
        default=None,
        description=(
            "Non-credential regulatory mechanisms (bonding, insurance, "
            "establishment regulation) imposed by the state. Obama 2015 "
            "framework typology. Independent of credential_type."
        ),
    )

    citations: list[Citation] = Field(default_factory=list)


class ScopeOfPractice(BaseModel):
    """Skeleton only — profession-specific richness lives in the discovered block."""
    definition_quote: StrEvidence | None = Field(
        default=None,
        description="Verbatim statutory definition; quote field repeats the value text.",
    )
    methods_authorized: StrListEvidence | None = Field(
        default=None,
        description="High-level methods, e.g. ['medical','surgical','mechanical']",
    )
    drug_authority: StrEvidence | None = None
    citations: list[Citation] = Field(default_factory=list)
