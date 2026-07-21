"""ETL: load pipeline/results/ into Postgres.

Five tables get refreshed by this script (see docs/POSTGRES_PLAN.md
and pipeline/publish/db/migrations/):

  1. documents          — title / chapter / section tree per state
  2. evidence           — every Evidence-shaped node (state, profession, field_path, value, quote, citation)
  3. state_profession_profile — flat per-(state, profession) summary row
  4. discovered_fields  — per-profession LLM-discovered field catalog
  5. practice_acts      — profession ↔ document join
  6. umbrella_applies_to — umbrella document ↔ profession join, with scope_source

`professions` is seeded by migration 0001 and isn't re-touched here.

Idempotent. Re-running re-upserts via natural keys; nothing is deleted.

Usage:
  python -m pipeline.publish.db.load --all
  python -m pipeline.publish.db.load --profession podiatry
  python -m pipeline.publish.db.load --all --dry-run
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from typing import Any, Iterable

import psycopg
from psycopg import sql
from psycopg.rows import dict_row

# Make sibling modules importable.
from pipeline._env import load_env
load_env()

from pipeline.extract.model_helpers import iter_evidence
from pipeline.extract.locate_quote import (
    normalize_for_match,  # unused, but kept for symmetry with build_frontend
)
from pipeline.publish.build_frontend import (
    _ev_value,
    _derive_credential_and_mandatory,
    _extract_compacts,
    normalize_citation,
)
from pipeline.paths import (
    HIERARCHY_DIR,
    PROFESSION_INDEX_DIR,
    DISCOVERED_DIR,
    STRUCTURED_DIR,
    TRIMMED_DIR,
    RESULTS_DIR,
)
from pipeline.scope_sources import is_classified, professions_for
from pipeline.merged_scope import load_merged_scope
from pipeline._records import record_files
from pipeline.ingest._section_patterns import canonical_year_url

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("db.load")

UMBRELLA_TEXT_DIR = RESULTS_DIR / "umbrella_text"

PROFESSIONS = [
    "podiatry", "nursing", "medicine", "dentistry", "optometry", "public_accountancy",
]


# ─── Helpers ──────────────────────────────────────────────────────────────

def slug_from_url(url: str) -> str:
    """Last non-empty path segment of a Justia-style URL.

    Justia URLs look like
        https://law.justia.com/codes/arizona/title-32/chapter-19/section-32-851/
    so the slug we use as a hierarchy node id is `section-32-851`. Stripped
    of any trailing /.
    """
    path = url.rstrip("/")
    if "/" not in path:
        return path
    return path.rsplit("/", 1)[-1]


def title_chapter_section_from_url(url: str) -> tuple[str | None, str | None, str | None]:
    """Walk a Justia URL and pull out the (title, chapter, section) slugs.

    Returns None for missing components. Examples:
      https://law.justia.com/codes/arizona/title-32/section-32-851/
        → ('title-32', None, 'section-32-851')
      https://law.justia.com/codes/kentucky/chapter-311/section-311-380/
        → (None, 'chapter-311', 'section-311-380')
      https://law.justia.com/codes/arizona/title-32/chapter-19/section-32-851/
        → ('title-32', 'chapter-19', 'section-32-851')
    """
    title = chapter = section = None
    for part in url.rstrip("/").split("/"):
        if part.startswith("title-"):
            title = part
        elif part.startswith("chapter-") or part.startswith("act-"):
            chapter = part
        elif part.startswith("section-") or part.startswith("statute-") or part.startswith("rs-"):
            section = part
    return title, chapter, section


def _conn() -> psycopg.Connection:
    url = os.environ.get("DATABASE_URL")
    if not url:
        sys.exit("DATABASE_URL not set (check .env)")
    return psycopg.connect(url, row_factory=dict_row)


def _profession_ids(cur) -> dict[str, int]:
    cur.execute("SELECT id, key FROM professions")
    return {row["key"]: row["id"] for row in cur.fetchall()}


def _state_corpus(profession: str, state: str) -> dict | None:
    p = TRIMMED_DIR / profession / f"{state}.json"
    return json.loads(p.read_text()) if p.exists() else None


def _state_structured(profession: str, state: str) -> dict | None:
    p = STRUCTURED_DIR / profession / f"{state}.json"
    return json.loads(p.read_text()) if p.exists() else None


def _umbrella_text(state: str) -> dict | None:
    p = UMBRELLA_TEXT_DIR / f"{state}.json"
    return json.loads(p.read_text()) if p.exists() else None


def _umbrella_scope(state: str) -> dict | None:
    # Merged view: walker scope with Pass-3 LLM decisions overlaid, so the DB
    # links umbrella sections the LLM enumerated too (see pipeline/merged_scope).
    return load_merged_scope(state)


# ─── Documents ────────────────────────────────────────────────────────────

def upsert_documents_for_state(
    cur, state: str, professions_to_load: list[str], profession_ids: dict[str, int]
) -> dict[tuple[str, str], int]:
    """Upsert title / chapter / section rows for one state across all the
    professions we're loading. Returns a {(state, hierarchy_path): doc_id}
    map so the evidence + join inserts can FK back into it.

    Build order: title → chapter → section, so parent_id is always known
    when a child inserts. hierarchy_path is materialized as the slug chain.
    """
    titles: dict[str, dict] = {}    # slug → {url, label}
    chapters: dict[str, dict] = {}  # slug → {url, label, title_slug}
    sections: list[dict] = []       # {url, label, citation, text, title_slug, chapter_slug, profession, is_umbrella}

    # Per-profession trimmed sections (these are the substantive ones the
    # LLM saw + we let the evidence join back into).
    for prof in professions_to_load:
        corpus = _state_corpus(prof, state)
        if not corpus:
            continue
        for sec in corpus.get("sections", []):
            url = sec.get("url") or ""
            title_slug, chapter_slug, section_slug = title_chapter_section_from_url(url)
            if not section_slug:
                # Fall back to the last URL segment when nothing matched our
                # known prefixes. Better than dropping the row.
                section_slug = slug_from_url(url) or sec.get("citation", "") or sec.get("label", "")[:60]
            if title_slug and title_slug not in titles:
                # Title label is the parent of the section's chapter; we don't
                # always have a separate label for it. Use the slug as label.
                titles[title_slug] = {"url": None, "label": title_slug}
            if chapter_slug and chapter_slug not in chapters:
                chapters[chapter_slug] = {
                    "url": None, "label": chapter_slug, "title_slug": title_slug,
                }
            sections.append({
                "url": url,
                "label": sec.get("label") or section_slug,
                "citation": normalize_citation(sec.get("citation") or ""),
                "text": sec.get("text") or "",
                "title_slug": title_slug,
                "chapter_slug": chapter_slug,
                "section_slug": section_slug,
                "profession": prof,
                "is_umbrella": False,
            })

    # Umbrella sections (cross-cutting chapters per state, profession-agnostic).
    umb_data = _umbrella_text(state)
    if umb_data:
        for sec in umb_data.get("sections", []):
            url = sec.get("url") or ""
            chap_label = sec.get("umbrella_chapter_label", "") or "umbrella"
            chap_slug = f"umbrella:{slug_from_url(chap_label or url) or 'unknown'}"
            section_slug = slug_from_url(url) or sec.get("label", "")[:60]
            if chap_slug not in chapters:
                chapters[chap_slug] = {
                    "url": None, "label": chap_label, "title_slug": None,
                }
            sections.append({
                "url": url,
                "label": sec.get("label") or section_slug,
                "citation": normalize_citation(sec.get("citation") or ""),
                "text": sec.get("text") or "",
                "title_slug": None,
                "chapter_slug": chap_slug,
                "section_slug": section_slug,
                "profession": None,
                "is_umbrella": True,
            })

    doc_ids: dict[tuple[str, str], int] = {}

    # 1) titles
    for title_slug, t in titles.items():
        h_path = f"/{title_slug}"
        doc_ids[(state, h_path)] = _upsert_document(
            cur, state, parent_id=None, level="title", h_path=h_path,
            url=t["url"], label=t["label"], citation=None, text=None, is_umbrella=False,
        )

    # 2) chapters (some chapters may have no title parent — fine; parent_id=NULL)
    for chap_slug, c in chapters.items():
        parent_id = None
        if c["title_slug"]:
            parent_id = doc_ids.get((state, f"/{c['title_slug']}"))
        h_path = f"/{c['title_slug']}/{chap_slug}" if c["title_slug"] else f"/{chap_slug}"
        doc_ids[(state, h_path)] = _upsert_document(
            cur, state, parent_id=parent_id, level="chapter", h_path=h_path,
            url=c["url"], label=c["label"], citation=None, text=None,
            is_umbrella=chap_slug.startswith("umbrella:"),
        )

    # 3) sections
    for s in sections:
        chap_part = s["chapter_slug"] or "_no_chapter"
        parent_h = (
            f"/{s['title_slug']}/{chap_part}" if s["title_slug"]
            else f"/{chap_part}"
        )
        parent_id = doc_ids.get((state, parent_h))
        h_path = f"{parent_h}/{s['section_slug']}"
        # Two professions may both list the same section URL (umbrella → not
        # an issue; per-profession sections rarely overlap). Use the URL +
        # slug pair, dedup later by hierarchy_path.
        doc_ids[(state, h_path)] = _upsert_document(
            cur, state, parent_id=parent_id, level="section", h_path=h_path,
            url=s["url"], label=s["label"], citation=s["citation"],
            text=s["text"], is_umbrella=s["is_umbrella"],
        )

    return doc_ids


def _upsert_document(
    cur, state, parent_id, level, h_path, url, label, citation, text, is_umbrella
) -> int:
    cur.execute(
        """
        INSERT INTO documents
            (state, parent_id, hierarchy_level, hierarchy_path,
             url, citation, label, text, is_umbrella)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (state, hierarchy_path) DO UPDATE SET
            parent_id      = EXCLUDED.parent_id,
            url            = EXCLUDED.url,
            citation       = EXCLUDED.citation,
            label          = EXCLUDED.label,
            text           = EXCLUDED.text,
            is_umbrella    = EXCLUDED.is_umbrella
        RETURNING id
        """,
        (state, parent_id, level, h_path, url, citation, label, text, is_umbrella),
    )
    return cur.fetchone()["id"]


# ─── Evidence ─────────────────────────────────────────────────────────────

def _value_to_text(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, list):
        return ", ".join(str(x) for x in v)
    return str(v)


def upsert_evidence_for_state(
    cur, profession: str, state: str, profession_id: int,
    doc_ids: dict[tuple[str, str], int],
) -> int:
    structured = _state_structured(profession, state)
    if structured is None:
        return 0

    # Build citation → document_id lookup over THIS state's documents.
    cur.execute(
        "SELECT id, citation FROM documents WHERE state=%s AND citation IS NOT NULL",
        (state,),
    )
    cite_to_doc: dict[str, int] = {}
    for row in cur.fetchall():
        cite_to_doc[row["citation"]] = row["id"]

    inserted = 0
    for path, node in iter_evidence(structured):
        field_path = ".".join(str(p) for p in path)
        value = node.get("value")
        quote = node.get("quote") or ""
        citation = normalize_citation(node.get("citation") or "")
        unverified = bool(node.get("unverified"))
        section_id = cite_to_doc.get(citation)

        cur.execute(
            """
            INSERT INTO evidence
                (state, profession_id, section_id, field_path,
                 value_text, value_jsonb, quote, citation, unverified)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (state, profession_id, field_path) DO UPDATE SET
                section_id  = EXCLUDED.section_id,
                value_text  = EXCLUDED.value_text,
                value_jsonb = EXCLUDED.value_jsonb,
                quote       = EXCLUDED.quote,
                citation    = EXCLUDED.citation,
                unverified  = EXCLUDED.unverified
            """,
            (
                state, profession_id, section_id, field_path,
                _value_to_text(value), json.dumps(value), quote, citation, unverified,
            ),
        )
        inserted += 1
    return inserted


# ─── Profile rows ─────────────────────────────────────────────────────────

def upsert_profile_row(cur, profession: str, state: str, profession_id: int) -> bool:
    record = _state_structured(profession, state)
    if record is None:
        return False
    lic = record.get("licensure") or {}
    credential_type, is_mandatory = _derive_credential_and_mandatory(lic)
    # Verified/unverified counts mirror what build_frontend computes.
    v = u = 0
    for _, ev in iter_evidence(record):
        if ev.get("unverified"):
            u += 1
        else:
            v += 1

    ab = lic.get("advisory_board") or {}
    cur.execute(
        """
        INSERT INTO state_profession_profile (
            state, profession_id, coverage_gap,
            license_required, regulatory_model, credential_type, is_mandatory,
            title_protection, scope_protection, issuing_authority,
            education_degree, post_degree_duration, exams_count,
            renewal_years, ce_hours, ce_period_years, reciprocity_available,
            compacts, disciplinary_grounds_count,
            advisory_board_exists, national_certification, national_association, renewal_fee_usd,
            evidence_verified, evidence_unverified
        ) VALUES (
            %s, %s, FALSE,
            %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s,
            %s, %s, %s, %s,
            %s, %s
        )
        ON CONFLICT (state, profession_id) DO UPDATE SET
            license_required       = EXCLUDED.license_required,
            regulatory_model       = EXCLUDED.regulatory_model,
            credential_type        = EXCLUDED.credential_type,
            is_mandatory           = EXCLUDED.is_mandatory,
            title_protection       = EXCLUDED.title_protection,
            scope_protection       = EXCLUDED.scope_protection,
            issuing_authority      = EXCLUDED.issuing_authority,
            education_degree       = EXCLUDED.education_degree,
            post_degree_duration   = EXCLUDED.post_degree_duration,
            exams_count            = EXCLUDED.exams_count,
            renewal_years          = EXCLUDED.renewal_years,
            ce_hours               = EXCLUDED.ce_hours,
            ce_period_years        = EXCLUDED.ce_period_years,
            reciprocity_available  = EXCLUDED.reciprocity_available,
            compacts               = EXCLUDED.compacts,
            disciplinary_grounds_count = EXCLUDED.disciplinary_grounds_count,
            advisory_board_exists  = EXCLUDED.advisory_board_exists,
            national_certification = EXCLUDED.national_certification,
            national_association   = EXCLUDED.national_association,
            renewal_fee_usd        = EXCLUDED.renewal_fee_usd,
            evidence_verified      = EXCLUDED.evidence_verified,
            evidence_unverified    = EXCLUDED.evidence_unverified
        """,
        (
            state, profession_id,
            _ev_value(lic.get("license_required")),
            _ev_value(lic.get("regulatory_model")),
            credential_type,
            is_mandatory,
            _ev_value(lic.get("title_protection")),
            _ev_value(lic.get("scope_protection")),
            _ev_value(lic.get("issuing_authority")),
            _ev_value(((lic.get("education") or {}).get("degree_required"))),
            _ev_value(((lic.get("post_degree_experience") or {}).get("duration"))),
            len(lic.get("exams") or []),
            _ev_value(((lic.get("renewal") or {}).get("interval_years"))),
            _ev_value(((lic.get("continuing_education") or {}).get("hours_per_period"))),
            _ev_value(((lic.get("continuing_education") or {}).get("period_years"))),
            _ev_value(((lic.get("reciprocity") or {}).get("available"))),
            _extract_compacts(record),
            len(lic.get("disciplinary_grounds") or []),
            _ev_value(ab.get("exists")),
            _ev_value(lic.get("national_certification")),
            _ev_value(lic.get("national_association")),
            _ev_value(lic.get("renewal_fee_usd")),
            v, u,
        ),
    )
    return True


# ─── Discovered fields ────────────────────────────────────────────────────

def upsert_discovered_fields(cur, profession: str, profession_id: int) -> int:
    p = DISCOVERED_DIR / f"{profession}.json"
    if not p.exists():
        return 0
    d = json.loads(p.read_text())
    inserted = 0
    for f in d.get("fields", []):
        cur.execute(
            """
            INSERT INTO discovered_fields
                (profession_id, name, category, description, type, sample_quote, sample_state)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (profession_id, name) DO UPDATE SET
                category     = EXCLUDED.category,
                description  = EXCLUDED.description,
                type         = EXCLUDED.type,
                sample_quote = EXCLUDED.sample_quote,
                sample_state = EXCLUDED.sample_state
            """,
            (
                profession_id,
                f.get("name"),
                f.get("category"),
                f.get("description"),
                f.get("type"),
                f.get("sample_quote"),
                f.get("sample_state"),
            ),
        )
        inserted += 1
    return inserted


# ─── Practice acts + umbrella applies-to ─────────────────────────────────

def link_umbrella_applies_to(
    cur, state: str, profession_ids: dict[str, int],
) -> int:
    """For every umbrella section in this state, link it to the professions
    it applies to per umbrella_scope/<STATE>.json. The deterministic
    scope assigner already did the per-section profession classification;
    we're just copying that into a join table."""
    scope = _umbrella_scope(state)
    if scope is None:
        return 0

    # Build url-canonical → doc_id lookup over THIS state's umbrella docs.
    cur.execute(
        "SELECT id, url FROM documents WHERE state=%s AND is_umbrella=TRUE AND hierarchy_level='section'",
        (state,),
    )
    url_to_doc: dict[str, int] = {}
    for row in cur.fetchall():
        # Canonicalize the URL (strip year prefix) — shared with extract/discover.
        canonical = canonical_year_url(row["url"] or "")
        url_to_doc[canonical] = row["id"]
        url_to_doc[row["url"] or ""] = row["id"]

    inserted = 0
    for entry in scope.get("sections", []):
        src = entry.get("scope_source")
        if not is_classified(src):
            continue
        section_url = entry.get("url") or ""
        doc_id = url_to_doc.get(section_url)
        if doc_id is None:
            # Try canonicalized form.
            doc_id = url_to_doc.get(canonical_year_url(section_url))
        if doc_id is None:
            continue

        applies = professions_for(src, entry.get("applies_to_professions"), profession_ids.keys())

        for prof_key in applies:
            pid = profession_ids.get(prof_key)
            if pid is None:
                continue
            cur.execute(
                """
                INSERT INTO umbrella_applies_to (document_id, profession_id, scope_source)
                VALUES (%s, %s, %s)
                ON CONFLICT (document_id, profession_id) DO UPDATE SET
                    scope_source = EXCLUDED.scope_source
                """,
                (doc_id, pid, src),
            )
            inserted += 1
    return inserted


# ─── Orchestration ────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--profession", help="One profession key (e.g. podiatry)")
    g.add_argument("--all", action="store_true", help="Load all 6 professions")
    ap.add_argument("--states", default="", help="Comma-separated state subset")
    ap.add_argument("--dry-run", action="store_true", help="Roll back instead of committing")
    args = ap.parse_args()

    target = PROFESSIONS if args.all else [args.profession]
    only_states = (
        [s.strip().upper() for s in args.states.split(",") if s.strip()]
        if args.states else None
    )

    with _conn() as conn:
        with conn.cursor() as cur:
            profession_ids = _profession_ids(cur)

            # Umbrella linking is state-scoped; run once after document load.
            # Track which states we've loaded so we know which to umbrella-link.
            states_loaded: set[str] = set()

            for prof in target:
                # Determine the state list for this profession.
                if only_states is not None:
                    states = only_states
                else:
                    states = [p.stem for p in record_files(STRUCTURED_DIR / prof)]

                pid = profession_ids.get(prof)
                if pid is None:
                    log.warning("[%s] not in DB — skipping", prof)
                    continue

                ev_count = profile_count = 0
                for st in states:
                    upsert_documents_for_state(cur, st, [prof], profession_ids)
                    ev_count += upsert_evidence_for_state(cur, prof, st, pid, {})
                    if upsert_profile_row(cur, prof, st, pid):
                        profile_count += 1
                    states_loaded.add(st)
                fields_count = upsert_discovered_fields(cur, prof, pid)

                log.info(
                    "[%s] %d states · %d evidence · %d profile · %d discovered",
                    prof, len(states), ev_count, profile_count, fields_count,
                )

            # Umbrella linking pass — one row per (umbrella_doc, profession).
            umb_links = 0
            for st in sorted(states_loaded):
                umb_links += link_umbrella_applies_to(cur, st, profession_ids)
            log.info("umbrella_applies_to: %d links across %d states", umb_links, len(states_loaded))

            if args.dry_run:
                conn.rollback()
                log.info("dry-run: rolled back")
            else:
                conn.commit()
                log.info("committed")


if __name__ == "__main__":
    main()
