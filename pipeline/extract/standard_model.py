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

from pydantic import BaseModel, Field


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
    """Six-rung ladder, low → high strictness."""
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


class DisciplinaryGround(BaseModel):
    """One ground on which the board may discipline a licensee. Captured as a
    list of these per state — typically 5-15 grounds in any one statute."""
    short_label: str = Field(description="snake_case key, e.g. 'fraud_in_obtaining_license'")
    description: str = Field(description="One-line plain-English description")
    quote: str
    citation: str


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
    quote: str = Field(description="Verbatim phrase mentioning this exam")
    citation: str


# ---------- Top-level base components ----------

class LicensureRequirements(BaseModel):
    license_required: BoolEvidence | None = None
    issuing_authority: StrEvidence | None = None
    age_minimum: IntEvidence | None = None
    moral_character_required: BoolEvidence | None = None
    education: EducationRequirement | None = None
    post_degree_experience: PostDegreeExperience | None = None
    exams: list[Exam] = Field(default_factory=list)
    renewal: Renewal | None = None
    continuing_education: ContinuingEducation | None = None
    reciprocity: Reciprocity | None = None

    # UORF-mapped fields
    regulatory_model: RegulatoryModelEvidence | None = Field(
        default=None,
        description="Which UORF model the state applies to this profession (license / mandatory_cert / registration / etc).",
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
