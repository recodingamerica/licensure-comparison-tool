"""Aggregate per-state structured extractions into one data.json for the viewer.

Schema is now Evidence-wrapped: each leaf is {value, quote, citation, [unverified]}.
We pass the entire structured record through to the frontend so the modal can
show evidence; for table columns we surface UNIVERSAL fields only (license,
issuing authority, education, post-degree experience, exams, renewal, CE,
reciprocity). Profession-specific fields live in the modal.

Usage:
  python build_frontend.py --profession podiatry
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


# Known interstate licensure compacts: short tag → detection pattern.
# Surfaced as a structured `compacts: list[str]` column on each row so the UI
# can show compact membership without changing the underlying extraction
# schema. Patterns match the verbatim quote text already in the record.
COMPACT_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("NLC",      re.compile(r"\b(?:nurse\s+licensure\s+compact|enhanced\s+nurse\s+licensure(?:\s+compact)?|NLC)\b", re.I)),
    ("IMLC",     re.compile(r"\b(?:interstate\s+medical\s+licensure\s+compact|IMLC)\b", re.I)),
    ("PTC",      re.compile(r"\b(?:physical\s+therapy\s+(?:licensure\s+)?compact|PT\s+compact|PTC)\b", re.I)),
    ("ASLP-IC",  re.compile(r"\b(?:audiology\s+(?:and\s+)?speech[\s-]language\s+(?:pathology\s+)?(?:interstate\s+)?compact|ASLP-?IC)\b", re.I)),
    ("PSY-PACT", re.compile(r"\b(?:psychology\s+inter[\s-]?jurisdictional\s+compact|PSY-?PACT)\b", re.I)),
    ("EMS-C",    re.compile(r"\b(?:emergency\s+medical\s+services\s+personnel\s+licensure\s+(?:interstate\s+)?compact|EMS\s+compact)\b", re.I)),
    ("OT-C",     re.compile(r"\b(?:occupational\s+therapy\s+licensure\s+compact|OT\s+compact)\b", re.I)),
    ("CC",       re.compile(r"\bcounseling\s+compact\b", re.I)),
    ("DDH-C",    re.compile(r"\b(?:dentist\s+(?:and\s+dental\s+hygienist\s+)?compact|dental\s+(?:hygienist\s+)?compact)\b", re.I)),
    ("OD-C",     re.compile(r"\b(?:optometry\s+licensure\s+compact|optometry\s+compact)\b", re.I)),
    ("APRN-C",   re.compile(r"\b(?:advanced\s+practice\s+registered\s+nurse\s+compact|APRN\s+compact)\b", re.I)),
    ("DLC",      re.compile(r"\b(?:dietitian\s+licensure\s+compact|dietitian\s+compact|DLC)\b", re.I)),
]


def _extract_compacts(record: dict) -> list[str]:
    """Walk the extracted record for mentions of known interstate licensure
    compacts. Returns a sorted list of compact short-tags. Surfaces existing
    quote text — no new LLM, no schema change.

    Scope note: this is a pattern-match derivation; a quote describing a compact
    a state has NOT joined would still flag. In practice, the structured records
    only quote compact text from chapters the state actually enacted, so the
    false-positive rate is low. Audit the UI quote modal for confirmation.
    """
    found: set[str] = set()

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
        elif isinstance(node, str):
            for tag, pat in COMPACT_PATTERNS:
                if pat.search(node):
                    found.add(tag)

    walk(record)
    return sorted(found)


from pipeline.paths import STRUCTURED_DIR, DISCOVERED_DIR, TRIMMED_DIR, RESULTS_DIR, MAP_PREP_DIR, CONFIG_DIR
from pipeline._records import record_files
from pipeline._runlog import record_run
import yaml  # noqa: E402 — still needed for publish_options.yaml (out-of-scope for R2)
from pipeline.config.loaders import load_professions

# Publish toggles — the single-parameter off-switch for verified absences.
_PUB_OPTS = yaml.safe_load((CONFIG_DIR / "publish_options.yaml").read_text()) or {}
INCLUDE_VERIFIED_ABSENCES = bool(_PUB_OPTS.get("include_verified_absences", True))
from pipeline.config.states import ALL_STATES
from pipeline.extract.locate_quote import locate_quote_in_section
from pipeline.extract.standard_model import is_evidence_node, iter_evidence
from pipeline.scope_sources import is_universal, is_enumeration
from pipeline.merged_scope import merged_scope_by_url
from pipeline.publish.blob_upload import upload_json
from pipeline.publish._browse_tree import build_tree as _build_browse_tree
from pipeline.publish._justia_clean import clean_justia_text


def _ev_value(node: Any) -> Any:
    """If `node` is Evidence-shaped, return .value; otherwise return as-is."""
    return node["value"] if is_evidence_node(node) else node


# Trailing-title pattern for section-symbol citations: matches a section
# number (with optional dot-separated subsections + letter suffix), then a
# REQUIRED period + space + capital letter = start of an appended title.
# Lets us strip "§ 324. Prohibitions" → "§ 324" while leaving "§ 324.5"
# alone (no space after the dot, no title).
_SECTION_TITLE_TAIL_RE = re.compile(
    r"^(§\s*\d+(?:[.\-:]\d+)*[a-z]?)\.\s+[A-Z].*$",
    re.UNICODE,
)


def normalize_citation(cite: str) -> str:
    """Tidy a citation string for display. Idempotent.

    Strips: bracket wrappers (`[314.031]` → `314.031`), trailing period,
    ` - descriptive tail` (Utah / Nebraska style: `Section 301 - License
    required -- ...` → `Section 301`), and trailing `. Section Title` after a
    `§ N` form (Vermont style: `§ 324. Prohibitions` → `§ 324`).

    Does NOT strip the `UMBRELLA / <chapter>` prefix — that's a deliberate
    marker the section-text lookup uses to route umbrella-context quotes
    back to their source chapter, and it's also useful display info ("this
    quote came from a cross-cutting umbrella chapter").

    Underlying structured records keep the LLM's original citation; this
    normalization only changes what the published JSON ships, so the diff
    between the LLM output and the displayed form is greppable in code.
    """
    if not cite:
        return cite
    s = cite.strip()
    # Preserve the `UMBRELLA / ` prefix but normalize the bit AFTER it.
    umbrella_prefix = ""
    if s.startswith("UMBRELLA / "):
        umbrella_prefix = "UMBRELLA / "
        s = s[len(umbrella_prefix):].strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1].strip()
    if s.endswith("."):
        s = s[:-1].strip()
    # Try the SHORTER separator first: a string with both `Section 301 -
    # License required -- ...` shape resolves to `Section 301` by splitting
    # on the leftmost ` - ` (which doesn't appear as a substring of ` -- `).
    for sep in (" - ", " -- "):
        if sep in s:
            s = s.split(sep, 1)[0].strip()
            break
    m = _SECTION_TITLE_TAIL_RE.match(s)
    if m:
        s = m.group(1).strip()
    return umbrella_prefix + s


def _g(d: dict | None, *path: str) -> Any:
    cur: Any = d
    for k in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur


def _section_evidence_spans(record: dict, text: str) -> list[dict]:
    """For one section's text, find every Evidence node from `record` whose
    quote appears in it, returning a list of {field_path, value, quote,
    spans, unverified} dicts. The frontend uses this to render highlights
    over the section text in the browse view's detail panel.

    Uses the same locate_quote_in_section matcher as _annotate_quote_spans
    — single source of truth. An Evidence quote may match in multiple
    sections; that's fine, both render highlights independently.
    """
    if not text:
        return []
    out: list[dict] = []
    for path, node in iter_evidence(record):
        quote = node.get("quote") or ""
        if not quote:
            continue
        spans = locate_quote_in_section(quote, text)
        if not spans:
            continue
        entry: dict = {
            "field_path": ".".join(str(p) for p in path),
            "value": node.get("value"),
            "quote": quote,
            "spans": [list(p) for p in spans],
            "unverified": bool(node.get("unverified")),
        }
        if "approximate" in node:
            entry["approximate"] = node["approximate"]
        out.append(entry)
    return out


def _build_browse_sections(
    record: dict,
    profession: str,
    practice_sections: list[dict],
    umbrella_state_data: dict | None,
    umb_scope: dict[str, dict],
) -> list[dict]:
    """Per-section data for the /browse/[state]/[prof] view.

    Unlike row.sections (which aggregates umbrella sections by chapter for
    backward-compat with the existing Sheet's "in context" lookup), this is
    one entry per individual section, each tagged with a scope_layer the
    browse view's tree groups by.

    Filters umbrella sections to only those whose scope applies to the
    current profession — universal applies to all; enumerated sections
    include only the ones explicitly applying to this profession.
    """
    out: list[dict] = []

    # Practice-act sections (per-profession). Every such section is the
    # profession's own statute; no scope filter needed.
    for s in practice_sections:
        # Practice-act sections also carry Justia chrome (breadcrumb,
        # citation header, disclaimer) — strip on the way out so the
        # browse view renders just the statute paragraphs.
        text = clean_justia_text(s.get("text") or "")
        if not text:
            continue
        out.append({
            "url": s.get("url"),
            "citation": s.get("citation"),
            "label": s.get("label"),
            "text": text,
            "scope_layer": "practice",
            "applies_to": None,
            "evidence": _section_evidence_spans(record, text),
        })

    # Umbrella sections (individual — not aggregated by chapter).
    for s in (umbrella_state_data or {}).get("sections", []) or []:
        # Same Justia-chrome strip as build_state_browse uses, so the per-
        # profession browse view shows clean section text too.
        text = clean_justia_text(s.get("text") or "")
        url = s.get("url") or ""
        if not text or not url:
            continue
        info = umb_scope.get(url) or {}
        scope_source = info.get("scope_source") or ""
        applies_to = info.get("applies_to_professions")

        if is_universal(scope_source):
            scope_layer = "umbrella_universal"
        elif is_enumeration(scope_source):
            scope_layer = "umbrella_enumeration"
            # Filter: only keep sections that explicitly apply to this prof.
            # applies_to=None means "scope assigner didn't determine" —
            # exclude to avoid noise.
            if not applies_to or profession not in applies_to:
                continue
        else:
            # "undetermined" or empty — skip rather than guess.
            continue

        # Citation for umbrella section: use the section's own label, or fall
        # back to the chapter label. Don't reuse the "UMBRELLA / <chap>"
        # aggregate citation here — we want one entry per section.
        chap_label = (s.get("umbrella_chapter_label") or "").strip()
        label = s.get("label") or chap_label or "umbrella section"

        out.append({
            "url": url,
            "citation": label,
            "label": label,
            "text": text,
            "scope_layer": scope_layer,
            "applies_to": applies_to,
            "evidence": _section_evidence_spans(record, text),
        })

    return out


def _annotate_quote_spans(record: dict, sections: list[dict]) -> tuple[int, int]:
    """For each verified Evidence node, find the cited section's text and
    attach `quote_spans`: a list of (start, end) char offsets into that
    same `text` field the frontend will render. The UI then slices
    directly — no re-derived regex, no Python-vs-TS parity drift.

    The lookup mirrors evidence-row.tsx: try the raw citation, then the
    bracket-stripped form. Unverified nodes are skipped (highlight would
    be misleading), and nodes whose citation we can't pin to a single
    section are left without spans (verifier may still have accepted them
    via the combined chapter+umbrella corpus — see STATUS.md's
    corpus-boundary case; UI shows the quote without a highlight).

    Returns (with_spans, without_spans) across verified nodes.
    """
    by_cite: dict[str, dict] = {}
    for s in sections:
        cite = s.get("citation") or ""
        if not cite:
            continue
        by_cite[cite] = s
        by_cite[f"[{cite}]"] = s

    with_spans = without_spans = 0
    for _, node in iter_evidence(record):
        if node.get("unverified"):
            continue
        cite = node.get("citation") or ""
        sec = by_cite.get(cite) or by_cite.get(cite.strip("[]"))
        text = (sec or {}).get("text") or ""
        spans = locate_quote_in_section(node.get("quote") or "", text) if text else None
        if spans:
            # Pydantic dumps tuples as lists already; be explicit so JSON
            # output is `[[s, e], ...]` either way.
            node["quote_spans"] = [list(p) for p in spans]
            with_spans += 1
        else:
            without_spans += 1
    return with_spans, without_spans


def _count_evidence(record: dict) -> tuple[int, int, int]:
    """Walk record for Evidence-shaped objects, count verified vs unverified
    vs approximate. Approximate is a subset of unverified (the strict
    verifier failed but the fuzzy fallback found a candidate substring)."""
    verified = unverified = approximate = 0
    for _, node in iter_evidence(record):
        if node.get("unverified"):
            unverified += 1
            if node.get("approximate"):
                approximate += 1
        else:
            verified += 1
    return verified, unverified, approximate


def _derive_credential_and_mandatory(lic: dict) -> tuple[str | None, bool | None]:
    """Decompose the legacy single-axis regulatory_model rung into the two
    orthogonal axes the meeting Q1 asked for. If credential_type / is_mandatory
    were extracted directly (newer runs), prefer those; otherwise derive from
    regulatory_model.

    Returns (credential_type_value, is_mandatory_value), each may be None.
    """
    direct_ct = _ev_value(lic.get("credential_type"))
    direct_im = _ev_value(lic.get("is_mandatory"))
    if direct_ct is not None or direct_im is not None:
        return direct_ct, direct_im

    rm_val = _ev_value(lic.get("regulatory_model"))
    if rm_val is None:
        return None, None
    try:
        from pipeline.extract.standard_model import RegulatoryModel, decompose_regulatory_model
        rung = RegulatoryModel(rm_val) if not isinstance(rm_val, RegulatoryModel) else rm_val
        ct, im = decompose_regulatory_model(rung)
        return ct.value, im
    except (ValueError, KeyError):
        return None, None


def hoist_row(record: dict) -> dict:
    """Universal columns. Profession-specific dimensions live in the modal."""
    lic = record.get("licensure") or {}
    verified, unverified, approximate = _count_evidence(record)
    credential_type, is_mandatory = _derive_credential_and_mandatory(lic)
    return {
        "state": record["state"],
        "coverage_gap": False,
        # Provenance: "extracted" (from statute) vs "verified_absence" (research-
        # asserted no-state-license). The UI badges verified_absence rows clearly.
        "data_basis": record.get("source") or "extracted",
        "absence_basis": record.get("basis"),   # local_only / not_regulated / contractor_only
        "absence_note": record.get("note"),
        "license_required": _ev_value(lic.get("license_required")),
        "regulatory_model": _ev_value(lic.get("regulatory_model")),
        "credential_type": credential_type,
        "is_mandatory": is_mandatory,
        "title_protection": _ev_value(lic.get("title_protection")),
        "scope_protection": _ev_value(lic.get("scope_protection")),
        "issuing_authority": _ev_value(lic.get("issuing_authority")),
        "education_degree": _ev_value(_g(lic, "education", "degree_required")),
        "post_degree_duration": _ev_value(_g(lic, "post_degree_experience", "duration")),
        "exams_count": len(lic.get("exams") or []),
        "renewal_years": _ev_value(_g(lic, "renewal", "interval_years")),
        "ce_hours": _ev_value(_g(lic, "continuing_education", "hours_per_period")),
        "ce_period_years": _ev_value(_g(lic, "continuing_education", "period_years")),
        "reciprocity_available": _ev_value(_g(lic, "reciprocity", "available")),
        "compacts": _extract_compacts(record),
        "disciplinary_grounds_count": len(lic.get("disciplinary_grounds") or []),
        # Universal-comparison fields added to match the cross-state schema
        # (see PDF cross-comparison table). Atharv's framework treats these
        # as required universal columns alongside the older ones above.
        "advisory_board_exists": _ev_value(_g(lic, "advisory_board", "exists")),
        "advisory_board_name": _ev_value(_g(lic, "advisory_board", "name")),
        "advisory_board_authority": _ev_value(_g(lic, "advisory_board", "authority")),
        "national_certification": _ev_value(lic.get("national_certification")),
        "national_association": _ev_value(lic.get("national_association")),
        "renewal_fee_usd": _ev_value(lic.get("renewal_fee_usd")),
        "evidence_verified": verified,
        "evidence_unverified": unverified,
        "evidence_approximate": approximate,
        "_full": record,
    }


COVERAGE_REASON_LABELS = {
    "no_chapter_located":              "No {display} chapter found in our scrape",
    "all_sections_dropped_or_repealed":"All sections in the chapter were repealed",
    "extraction_failed":               "LLM extraction failed",
    "no_credential_in_state_law":      "No {display} credential in state law",
}


def stub_row(state: str, profession: str, reason: str, detail: str | None = None) -> dict:
    label = COVERAGE_REASON_LABELS.get(reason, reason).format(
        display=_profession_display(profession).lower()
    )
    return {
        "state": state,
        "coverage_gap": True,
        "coverage_gap_reason": reason,
        "coverage_gap_label": label,
        "coverage_gap_detail": detail,
        "license_required": None,
        "regulatory_model": None,
        "credential_type": None,
        "is_mandatory": None,
        "title_protection": None,
        "scope_protection": None,
        "issuing_authority": None,
        "education_degree": None,
        "post_degree_duration": None,
        "exams_count": 0,
        "renewal_years": None,
        "ce_hours": None,
        "ce_period_years": None,
        "reciprocity_available": None,
        "compacts": [],
        "disciplinary_grounds_count": 0,
        "disciplinary_categories": [],
        "list_field_categories": {},
        "advisory_board_exists": None,
        "advisory_board_name": None,
        "advisory_board_authority": None,
        "national_certification": None,
        "national_association": None,
        "renewal_fee_usd": None,
        "evidence_verified": 0,
        "evidence_unverified": 0,
        "evidence_approximate": 0,
        "_full": {"state": state, "profession": profession},
    }


def build(profession: str, payload_only: bool = False) -> dict:
    """Build a profession's frontend payload.

    payload_only=True skips the expensive per-state browse regeneration
    (`_build_browse_sections` + `_build_browse_tree`) — the CPU hog that
    fuzzy-matches statute text. Use it when only the table/map/tag data
    changed (e.g. a re-bucketing) and the per-state browse blobs in Blob are
    still current. The main payload (table rows + map_prep + tags + quote
    highlight spans) is rebuilt fully; browse files are left untouched.
    """
    structured_dir = STRUCTURED_DIR / profession
    discovered = json.loads((DISCOVERED_DIR / f"{profession}.json").read_text())
    trimmed_dir = TRIMMED_DIR / profession

    have_struct = {p.stem for p in record_files(structured_dir)}
    trimmed_with_text: dict[str, int] = {}
    chapter_urls_by_state: dict[str, list[str]] = {}
    sections_by_state: dict[str, list[dict]] = {}

    umbrella_text_dir = RESULTS_DIR / "umbrella_text"

    # Per-state raw umbrella + scope data so we can build browse_sections.
    practice_sections_by_state: dict[str, list[dict]] = {}
    umbrella_data_by_state: dict[str, dict] = {}
    umb_scope_by_state: dict[str, dict[str, dict]] = {}

    if trimmed_dir.exists():
        for p in record_files(trimmed_dir):
            d = json.loads(p.read_text())
            trimmed_with_text[p.stem] = d.get("total_chars", 0)
            chapter_urls_by_state[p.stem] = d.get("chapter_urls", []) or []
            # Section bodies as the LLM saw them — used for "view in context" panel
            section_list = [
                {"url": s.get("url"), "citation": s.get("citation"),
                 "label": s.get("label"), "text": s.get("text")}
                for s in (d.get("sections") or [])
                if s.get("text")
            ]
            practice_sections_by_state[p.stem] = list(section_list)
            # ALSO include umbrella sections so the UI can highlight quotes the
            # extractor drew from umbrella context. Multiple umbrella section
            # bodies share the same "UMBRELLA / <chapter_label>" citation prefix
            # (that's how extract_state.load_umbrella_text labels them), so
            # concatenate their text under a single ref per chapter.
            umb_path = umbrella_text_dir / f"{p.stem}.json"
            if umb_path.exists():
                umb = json.loads(umb_path.read_text())
                umbrella_data_by_state[p.stem] = umb
                umb_scope_by_state[p.stem] = merged_scope_by_url(p.stem)
                by_chap: dict[str, dict] = {}
                for s in umb.get("sections", []):
                    if not s.get("text"):
                        continue
                    chap_label = (s.get("umbrella_chapter_label") or "")[:60]
                    cite = f"UMBRELLA / {chap_label}"
                    if cite not in by_chap:
                        by_chap[cite] = {
                            "url": s.get("url"),  # first section's URL
                            "citation": cite,
                            "label": f"umbrella context — {chap_label}",
                            "text": s.get("text") or "",
                        }
                    else:
                        by_chap[cite]["text"] += "\n" + (s.get("text") or "")
                section_list.extend(by_chap.values())
            sections_by_state[p.stem] = section_list

    rows: list[dict] = []
    span_with = span_without = 0
    for st in ALL_STATES:
        if st in have_struct:
            rec = json.loads((structured_dir / f"{st}.json").read_text())
            # OFF SWITCH (config/publish_options.yaml): when verified absences are
            # disabled, a research-asserted no-license record falls back to an
            # ordinary coverage gap, exactly as if we'd never asserted it.
            if rec.get("source") == "verified_absence" and not INCLUDE_VERIFIED_ABSENCES:
                rows.append(stub_row(st, profession, "no_credential_in_state_law"))
                continue
            row = hoist_row(rec)
            row["source_chapter_urls"] = chapter_urls_by_state.get(st, [])
            row["sections"] = sections_by_state.get(st, [])
            # Concatenate the row's section bodies into one searchable string.
            # Used by the table's "Statute text" filter — agTextColumnFilter
            # does case-insensitive substring matching against this string,
            # so anything inside any section (per-profession OR umbrella)
            # narrows the table. Stored once per row to keep the matcher
            # cheap. ~50–500 KB per row depending on state size.
            row["section_text_full"] = "\n\n".join(
                s.get("text") or "" for s in row["sections"]
            )
            # Per-individual-section data for the /browse view's hierarchy
            # tree + section detail. Different shape from row.sections (which
            # aggregates umbrella by chapter for the Sheet's existing "in
            # context" lookup). Each browse_section is one node in the tree,
            # tagged with scope_layer + per-section evidence quote spans.
            # Browse regeneration is the per-state CPU hog. Skip it when only
            # the payload (table/map/tag data) changed — the browse blobs in
            # Blob stay current and main() won't re-split/re-upload them.
            if not payload_only:
                row["browse_sections"] = _build_browse_sections(
                    row["_full"],
                    profession,
                    practice_sections_by_state.get(st, []),
                    umbrella_data_by_state.get(st),
                    umb_scope_by_state.get(st, {}),
                )
                # Group browse_sections by scope_layer and build a hierarchy
                # tree per layer (parsed from each section's Justia URL). The
                # /browse/[state]/[prof] view renders these as nested
                # collapsible nodes; flat browse_sections kept alongside for
                # any consumer that still wants a list.
                _chap_labels: dict[str, str] = {}
                umb_state = umbrella_data_by_state.get(st)
                if umb_state:
                    for _s in umb_state.get("sections") or []:
                        _slug = _s.get("umbrella_chapter_slug")
                        _lbl = _s.get("umbrella_chapter_label")
                        if _slug and _lbl and _slug not in _chap_labels:
                            _chap_labels[_slug] = _lbl
                _by_layer: dict[str, list[dict]] = {}
                for _bs in row["browse_sections"]:
                    _by_layer.setdefault(_bs.get("scope_layer") or "practice", []).append(_bs)
                row["browse_groups"] = [
                    {"key": layer, "tree": _build_browse_tree(_by_layer[layer], chapter_label_overrides=_chap_labels)}
                    for layer in ("practice", "umbrella_enumeration", "umbrella_universal")
                    if _by_layer.get(layer)
                ]
            # Attach highlight spans now, against the EXACT section text we're
            # about to publish. Computing on this side (rather than during
            # extract/reverify) avoids any normalization drift between the
            # text the verifier saw and the text the UI will slice.
            w, wo = _annotate_quote_spans(row["_full"], row["sections"])
            span_with += w
            span_without += wo
            rows.append(row)
        else:
            chars = trimmed_with_text.get(st, 0)
            no_cred = _no_credential_states(profession)
            if st in no_cred:
                rows.append(stub_row(st, profession, "no_credential_in_state_law", detail=no_cred[st]))
                continue
            if st not in trimmed_with_text:
                reason = "no_chapter_located"
            elif chars == 0:
                reason = "all_sections_dropped_or_repealed"
            else:
                reason = "extraction_failed"
            rows.append(stub_row(st, profession, reason))

    # Evidence audit summary (across covered states)
    verified = unverified = 0
    for r in rows:
        if r["coverage_gap"]:
            continue
        for _, ev in iter_evidence(r["_full"]):
            if ev.get("unverified"):
                unverified += 1
            else:
                verified += 1

    structured_by_state = {
        r["state"]: r["_full"] for r in rows if not r["coverage_gap"]
    }
    map_prep = _load_map_prep(profession, structured_by_state)

    # Per-state content tags for every per-item-bucketed list field. Lets the
    # UI surface, per state, "Fraud, False Advertising, …" for disciplinary
    # grounds and "Capsulotomy (YAG), Trabeculoplasty, …" for laser procedures,
    # etc. — instead of only a count or a raw joined string. Empty when the
    # per-item bucketing hasn't been run.
    per_item_cats = _load_per_item_categories(profession)
    disc = per_item_cats.get("licensure.disciplinary_grounds", {})
    disc_by_state = disc.get("by_state", {})
    disc_by_state_item = disc.get("by_state_item", {})
    # The discovered list fields live under profession_specific.* — surface them
    # generically so the table can chip-render any of them.
    list_fields = {
        fn: v for fn, v in per_item_cats.items()
        if fn.startswith("profession_specific.")
    }
    for r in rows:
        if r["coverage_gap"]:
            continue
        st = r["state"]
        r["disciplinary_categories"] = disc_by_state.get(st, [])
        r["list_field_categories"] = {
            fn: v["by_state"].get(st, [])
            for fn, v in list_fields.items()
            if v["by_state"].get(st)
        }
        # Annotate each ground with its content bucket so the modal can group
        # grounds by category. Index order matches the per-item assignments.
        item_buckets = disc_by_state_item.get(st, {})
        if item_buckets:
            grounds = (r["_full"].get("licensure") or {}).get("disciplinary_grounds") or []
            for i, g in enumerate(grounds):
                if isinstance(g, dict) and i in item_buckets:
                    g["category"] = item_buckets[i]

    # Expose per-item tag breadth as mappable fields: # of distinct content
    # categories each state falls into for a list field (e.g. how many laser
    # procedure types a state authorizes). The map view renders these as
    # continuous choropleths. Only fields covering ≥2 states are worth a map.
    if map_prep is not None:
        count_fields = []
        for fn, v in per_item_cats.items():
            by_state_count = {
                st: len(cats) for st, cats in v["by_state"].items() if cats
            }
            if len(by_state_count) >= 2:
                count_fields.append(
                    {"field_name": fn, "by_state_count": by_state_count}
                )
        map_prep["per_item_count_fields"] = count_fields

    # Normalize citations in the published payload. We do this AFTER
    # `_annotate_quote_spans` (which uses raw + bracket-variant lookups) and
    # AFTER `_load_map_prep` (which copies citations onto map rows) so the
    # downstream display gets consistent text without breaking the internal
    # citation→section lookup that already ran.
    for r in rows:
        # iter_evidence walks any Evidence-shaped dict in the tree — finds
        # citations under r["_full"]["licensure"], ["scope"], ["profession_specific"],
        # and nested objects like exams[*], disciplinary_grounds[*].
        for _, ev in iter_evidence(r):
            cite = ev.get("citation")
            if cite:
                ev["citation"] = normalize_citation(cite)
        # Section list shipped per row also carries citations — normalize
        # those too so they line up with the Evidence-node citations the
        # frontend uses to match a quote to its section text.
        for s in r.get("sections") or []:
            if s.get("citation"):
                s["citation"] = normalize_citation(s["citation"])
    if map_prep:
        for mr in map_prep.get("rows") or []:
            if mr.get("citation"):
                mr["citation"] = normalize_citation(mr["citation"])

    meta = _profession_meta(profession)
    return {
        "profession": profession,
        "display": meta["display"],
        # Surface the yaml-driven visual metadata so the frontend's homepage
        # picker + browse views can color/abbreviate without hardcoding.
        "abbrev": meta["abbrev"],
        "family": meta["family"],
        "family_color": meta["family_color"],
        "family_label": meta["family_label"],
        "discovered_fields": discovered["fields"],
        "rows": rows,
        "map_prep": map_prep,
        "evidence_summary": {
            "verified": verified,
            "unverified": unverified,
            # How many verified nodes got per-section highlight spans
            # vs. only verified against the combined corpus. The latter
            # show in the UI without a yellow highlight.
            "with_quote_spans": span_with,
            "without_quote_spans": span_without,
        },
    }


def _resolve_evidence(record: dict, dotted: str) -> dict | None:
    """Walk a structured record by dotted path and return the Evidence node
    ({value, quote, citation, ...}) sitting at that path, if any.

    Used to enrich map_prep rows with the verbatim statute quote — the
    normalizer only saw `.value`, so the quote lives on the original record.
    """
    node: Any = record
    for p in dotted.split("."):
        if not isinstance(node, dict):
            return None
        node = node.get(p)
    return node if is_evidence_node(node) else None


_HARMONIZED_CACHE: dict[str, dict] | None = None


def _load_harmonized_universal() -> dict[str, dict]:
    """Cross-profession harmonized universal buckets (#16), keyed by field_name.
    Empty when the harmonize_universal pass hasn't run. Loaded once per process."""
    global _HARMONIZED_CACHE
    if _HARMONIZED_CACHE is None:
        path = MAP_PREP_DIR / "_harmonized" / "universal_buckets.json"
        if path.exists():
            data = json.loads(path.read_text())
            _HARMONIZED_CACHE = {f["field_name"]: f for f in data.get("fields", [])}
        else:
            _HARMONIZED_CACHE = {}
    return _HARMONIZED_CACHE


def _load_map_prep(profession: str, structured_by_state: dict[str, dict]) -> dict | None:
    """Attach the choropleth normalization output (pipeline/map_prep/run.py)
    so the UI can render maps without re-doing the normalization client-side.
    Also enrich each row with the verbatim statute quote + citation pulled
    from the structured record, so the map tooltip can show the source text.

    Returns {"spec": [...mappable FieldSpec...], "rows": [...NormalizedRow+quote...]}
    or None if map_prep hasn't been run for this profession yet.
    """
    src = MAP_PREP_DIR / profession
    spec_path = src / "spec.json"
    rows_path = src / "normalized.json"
    if not (spec_path.exists() and rows_path.exists()):
        return None
    spec = json.loads(spec_path.read_text())
    rows = json.loads(rows_path.read_text())
    # Only ship mappable specs to the UI; not_mappable fields are noise here.
    mappable = [f for f in spec.get("fields", []) if f.get("mappable")]

    enriched_rows: list[dict] = []
    for r in rows.get("rows", []):
        rec = structured_by_state.get(r.get("state"))
        if rec:
            ev = _resolve_evidence(rec, r.get("field_name", ""))
            if ev:
                r = {**r, "quote": ev.get("quote"), "citation": ev.get("citation")}
        enriched_rows.append(r)

    # Pass 3 text-bucket output (pipeline.map_prep.bucket_text). Optional —
    # only the 6 mapped professions have run it so far. Shape: per (field,
    # state) → bucket label, plus per-field bucket_set + rationale.
    text_buckets_path = src / "text_buckets.json"
    text_buckets: dict[str, dict] = {}  # field_name → {bucket_set, rationale, by_state}
    if text_buckets_path.exists():
        tb_raw = json.loads(text_buckets_path.read_text())
        for entry in tb_raw.get("fields", []):
            by_state = {a["state"]: a["bucket"] for a in entry.get("assignments", []) if a.get("bucket")}
            text_buckets[entry["field_name"]] = {
                "bucket_set": entry.get("bucket_set", []),
                "rationale": entry.get("rationale", ""),
                "by_state": by_state,
            }

    # Cross-profession harmonization (#16): for the universal fields harmonized
    # by pipeline.map_prep.harmonize_universal, replace the per-profession buckets
    # with the SHARED label set (this profession's slice) so the same category
    # means the same thing across professions. `harmonized: true` lets the UI flag
    # it. Non-harmonized fields keep their per-profession buckets.
    for field_name, hf in _load_harmonized_universal().items():
        by_state = hf.get("by_profession", {}).get(profession)
        if not by_state:
            continue
        text_buckets[field_name] = {
            "bucket_set": hf.get("bucket_set", []),
            "rationale": hf.get("rationale", ""),
            "by_state": by_state,
            "harmonized": True,
        }

    return {"spec": mappable, "rows": enriched_rows, "text_buckets": text_buckets}


def _load_per_item_categories(
    profession: str,
) -> dict[str, dict]:
    """Per-state content tags for EVERY per-item-bucketed list field, from the
    per-item bucketing pass (pipeline.map_prep.bucket_text --list-fields).

    Each state's individual list elements (disciplinary grounds, laser
    procedures, injections, license tiers, …) were assigned to a content bucket.
    The tag sheet aggregates these across states; here we aggregate the OTHER
    way — per state — so the table can show which categories each state falls
    into instead of only a raw joined string.

    Returns: field_name → {
      "by_state":      state → [{"label": bucket, "count": n}, …] (count desc),
      "by_state_item": state → {item_index: bucket},
    }
    Empty if the per-item pass hasn't been run for this profession.
    """
    path = MAP_PREP_DIR / profession / "text_buckets_per_item.json"
    out: dict[str, dict] = {}
    if not path.exists():
        return out
    raw = json.loads(path.read_text())
    for field_name, field in (raw.get("fields") or {}).items():
        counts: dict[str, dict[str, int]] = {}
        by_state_item: dict[str, dict[int, str]] = {}
        for a in field.get("assignments", []):
            st, bucket = a.get("state"), a.get("bucket")
            if not st or not bucket:
                continue
            per_state = counts.setdefault(st, {})
            per_state[bucket] = per_state.get(bucket, 0) + 1
            idx = a.get("item_index")
            if isinstance(idx, int):
                by_state_item.setdefault(st, {})[idx] = bucket
        by_state: dict[str, list[dict]] = {
            st: [
                {"label": label, "count": n}
                for label, n in sorted(bc.items(), key=lambda kv: (-kv[1], kv[0]))
            ]
            for st, bc in counts.items()
        }
        out[field_name] = {"by_state": by_state, "by_state_item": by_state_item}
    return out


def _no_credential_states(profession: str) -> dict[str, str]:
    """States declared in professions.yaml as having no credential in state
    law for this profession — a verified true negative, not a scrape gap.
    Returns {state: citation/explanation}."""
    try:
        cfg = load_professions()
        return cfg.get(profession, {}).get("no_credential_states") or {}
    except Exception:
        return {}


def _profession_display(profession: str) -> str:
    """Pull a friendly display name from config/professions.yaml; fall back to title-case."""
    try:
        cfg = load_professions()
        return cfg.get(profession, {}).get("display", profession.replace("_", " ").title())
    except Exception:
        return profession.replace("_", " ").title()


def _profession_meta(profession: str) -> dict:
    """All profession metadata the frontend needs to render: display name,
    3-letter abbrev for badges, family/color for the audience-grouping
    visual. Sourced from professions.yaml so adding a new profession only
    means a yaml entry. Falls back to slug-derived defaults when fields
    are absent so the frontend never crashes on missing keys.
    """
    try:
        cfg = load_professions()
    except Exception:
        cfg = {}
    families = cfg.get("_families") or {}
    entry = cfg.get(profession) or {}
    fam_list = entry.get("family") or []
    primary_family = fam_list[0] if fam_list else None
    fam_meta = families.get(primary_family) or {}
    return {
        "key": profession,
        "display": entry.get("display") or profession.replace("_", " ").title(),
        "abbrev": entry.get("abbrev") or profession[:3].upper(),
        "family": primary_family,
        "family_color": fam_meta.get("color"),
        "family_label": fam_meta.get("label"),
    }


def _all_profession_meta() -> list[dict]:
    """Return metadata for every profession in the yaml (excluding the
    _families config block). Used by fetch-blob-data to assemble
    /professions.json with the visual fields the homepage + browse views
    need."""
    try:
        cfg = load_professions()
    except Exception:
        return []
    return [_profession_meta(k) for k in cfg.keys() if not k.startswith("_")]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True)
    ap.add_argument("--deploy", action="store_true",
                    help="After uploading to blob, redeploy the Vercel project so the live site picks up the new data.")
    ap.add_argument("--payload-only", action="store_true",
                    help="Skip browse regeneration (the per-state CPU hog); rebuild only the table/map/tag payload. Use when browse data is unchanged.")
    args = ap.parse_args()

    profession = args.profession.lower()
    payload = build(profession, payload_only=args.payload_only)

    # Split heavy per-section data into separate per-(profession, state) files
    # so the main profile blob stays small. The table view loads the main
    # blob; the /browse route loads only the state it needs. Without this,
    # nursing alone is 67 MB — unacceptable for table-page load.
    data_dir = Path(__file__).resolve().parent / "web" / "public" / "data"
    browse_dir = data_dir / profession / "browse"
    browse_dir.mkdir(parents=True, exist_ok=True)
    browse_total = browse_cached = 0
    for row in payload["rows"]:
        bs = row.pop("browse_sections", None)
        bg = row.pop("browse_groups", None)
        if bs is None and bg is None:
            continue
        st = row["state"]
        section_payload = {
            "state": st,
            "profession": profession,
            "sections": bs or [],
            "groups": bg or [],
        }
        section_body = json.dumps(section_payload, indent=2)
        (browse_dir / f"{st}.json").write_text(section_body)
        _, _skipped = upload_json(f"data/{profession}/browse/{st}.json", section_body)
        browse_cached += int(_skipped)
        browse_total += 1
    print(f"synced {browse_total} per-state browse files "
          f"({browse_total - browse_cached} uploaded, {browse_cached} cached/unchanged)")

    body = json.dumps(payload, indent=2)
    # Mirror to public/data/ so downstream tooling (state_similarity, review CSV)
    # sees the same data the live site does, without round-tripping Vercel Blob.
    local_path = data_dir / f"{profession}.json"
    local_path.write_text(body)
    print(f"wrote {local_path}")
    url, skipped = upload_json(f"data/{profession}.json", body)
    print(f"{'cached' if skipped else 'uploaded'} data/{profession}.json → {url}")
    summary = {
        "covered": sum(1 for r in payload["rows"] if not r["coverage_gap"]),
        "gaps":    sum(1 for r in payload["rows"] if r["coverage_gap"]),
        "fields":  len(payload["discovered_fields"]),
        "evidence": payload["evidence_summary"],
    }
    print(f"summary: {summary}")
    record_run("build_frontend", profession=profession,
               covered=summary.get("covered"), gaps=summary.get("gaps"))

    if args.deploy:
        import subprocess
        web_dir = Path(__file__).resolve().parent / "web"
        print(f"deploying via vercel --prod from {web_dir}")
        r = subprocess.run(["npx", "vercel", "--prod", "--yes"], cwd=web_dir)
        if r.returncode != 0:
            sys.exit(f"vercel deploy failed (exit {r.returncode})")
        print("deployed")


if __name__ == "__main__":
    main()
