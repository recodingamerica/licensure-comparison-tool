"""Universal Pydantic pieces — fields that exist for essentially every
licensed profession. Every leaf field is wrapped in an Evidence[T] carrier
so each claim is backed by a verbatim quote from the source statute.

Per-profession richness lives in a discovered model that pass-2 composes
alongside this base; those fields use the same Evidence[T] shape.

Concrete Evidence subclasses (StrEvidence, BoolEvidence, ...) are used
instead of a single generic so the JSON schema sent to the LLM stays clean
— LiteLLM/Anthropic don't always handle Pydantic generics gracefully.
"""

from __future__ import annotations

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
