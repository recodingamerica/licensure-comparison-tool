"""Pass 3 — LLM fallback for umbrella sections the deterministic walker left
`undetermined`.

The walker (`assign_umbrella_scope`) scopes sections it can from citation /
universal-phrasing regex. Some sections genuinely can't be scoped that way —
the umbrella applies implicitly, or the citation format is irregular. This
step asks an LLM to read each such section and decide, grounded in the text:

    universal     → applies to every licensed profession in the state
    specific      → applies to an enumerated set (which professions)
    undetermined  → the text doesn't support a confident call (stays unscoped)

Every decision must carry an evidence quote from the section. No confidence
scores. The LLM may only choose professions from the state's known set.

Output is kept SEPARATE from the walker's, so the deterministic layer stays
auditable and re-runnable:

    umbrella_scope/<ST>.json       walker only (never LLM)
    umbrella_scope_llm/<ST>.json   LLM decisions for previously-undetermined
                                   sections (scope_method = "llm")

`merge_scope(state)` overlays the two for consumers.

Validation: FL § 455 is the canonical trap — "applies only to the regulation
of professions by the department" is DBPR-scoped, NOT universal. Pass 3 must
not call chapter-455 universal. Run `--validate-fl` to check.

Usage:
  python -m pipeline.discover.llm_scope_fallback --state FL
  python -m pipeline.discover.llm_scope_fallback --states FL,TX
  python -m pipeline.discover.llm_scope_fallback --all
  python -m pipeline.discover.llm_scope_fallback --state FL --validate-fl
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, field_validator

from pipeline._env import load_env
load_env()

from pipeline.paths import RESULTS_DIR, LOGS_DIR
from pipeline._records import record_files
from pipeline.scope_sources import is_classified
from pipeline._llm import call_structured
from pipeline.discover._profession_reverse_index import build_reverse_index
from pipeline.config.loaders import model_for

UMBRELLA_TEXT_DIR = RESULTS_DIR / "umbrella_text"
UMBRELLA_SCOPE_DIR = RESULTS_DIR / "umbrella_scope"
UMBRELLA_SCOPE_LLM_DIR = RESULTS_DIR / "umbrella_scope_llm"
LOG_PATH = LOGS_DIR / "llm_scope_fallback.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
UMBRELLA_SCOPE_LLM_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_MODEL = model_for("scope_rules")
MAX_TEXT_PER_SECTION = 2000   # cap section text sent to the model
MAX_SECTIONS_PER_CALL = 12    # batch this many undetermined sections per chapter call

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("LiteLLM").setLevel(logging.WARNING)
log = logging.getLogger("llm_scope_fallback")


# ---------------------------------------------------------------------------
# LLM response schema
# ---------------------------------------------------------------------------

class SectionDecision(BaseModel):
    url: str
    # Pass 3 may only narrow/enumerate or abstain — it never asserts "universal".
    # Universal scope is the deterministic walker's job (explicit "applies to
    # every profession" phrasing); promoting a walker-undetermined section to
    # universal would risk attributing it to professions it doesn't govern
    # (e.g. FL ch-455 is DBPR-only, not all professions).
    scope: Literal["specific", "undetermined"]
    professions: list[str] = []   # only meaningful for "specific"
    evidence: str = ""            # quote from the section justifying the call

    @field_validator("professions", mode="before")
    @classmethod
    def _coerce_none(cls, v):
        return v or []


class ChapterDecisions(BaseModel):
    decisions: list[SectionDecision]


SYSTEM_PROMPT = """\
You assign the SCOPE of individual sections in a state's "umbrella" licensing
statute — the cross-cutting chapters that govern many professions at once.

For each section, decide who it applies to, using ONLY the section's text.
There are exactly two answers:

  specific      The section applies to an ENUMERATED set of professions you can
                name. List them using ONLY the profession ids provided. Use this
                when the text names particular professions, or particular
                practice-act chapters/boards you can map to professions.

  undetermined  You cannot confidently enumerate which professions it applies
                to from the text. PREFER THIS over guessing. It is a valid,
                expected, common answer.

You do NOT decide "applies to everyone / all professions" — that universal
case is handled elsewhere. Your job is only to pick out an enumerated subset
when the text clearly names one, and otherwise abstain.

  - A section being in a "general provisions" or "definitions" chapter tells
    you nothing about scope. Read what it actually says.
  - "the department", "the board", "professions regulated by the department"
    name a SUBSET (a state often has multiple licensing departments). If the
    text names that subset's professions or its practice-act chapters, answer
    specific with those; if you can't enumerate them from the text, answer
    undetermined. Either way, never treat it as applying to all professions.
  - If a section cross-references a list you can't see (e.g. "boards listed in
    s. 20.165"), answer undetermined — don't guess.

Every `specific` decision MUST include an `evidence` field quoting the exact
phrase from the section that names the professions. Do not invent text. Do not
output confidence scores.

Return one decision per section, keyed by the section's url.
"""


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------

def valid_professions(state: str) -> list[str]:
    ri = build_reverse_index(state)
    return sorted({p for ids in ri.values() for p in ids})


def undetermined_sections(state: str) -> list[dict]:
    """Sections the walker left undetermined, joined to their text.

    Returns [{url, label, chapter, text}]. Empty if the state has no walker
    output or nothing undetermined.
    """
    scope_path = UMBRELLA_SCOPE_DIR / f"{state}.json"
    text_path = UMBRELLA_TEXT_DIR / f"{state}.json"
    if not scope_path.exists() or not text_path.exists():
        return []
    scope = json.loads(scope_path.read_text())
    text_by_url = {s.get("url"): s.get("text", "") for s in json.loads(text_path.read_text()).get("sections", [])}
    out = []
    for s in scope.get("sections", []):
        if s.get("scope_source") != "undetermined":
            continue
        out.append({
            "url": s.get("url", ""),
            "label": s.get("label", ""),
            "chapter": s.get("umbrella_chapter_slug", ""),
            "text": text_by_url.get(s.get("url"), ""),
        })
    return out


# ---------------------------------------------------------------------------
# LLM call (per chapter batch)
# ---------------------------------------------------------------------------

def _decide_batch(state: str, sections: list[dict], professions: list[str], model: str) -> list[SectionDecision]:
    blocks = []
    for s in sections:
        text = s["text"][:MAX_TEXT_PER_SECTION]
        blocks.append(f"--- url: {s['url']}\nlabel: {s['label']}\n{text}")
    user = (
        f"State: {state}\n\n"
        f"Valid profession ids (use ONLY these for 'specific'):\n  {', '.join(professions)}\n\n"
        f"Decide the scope of each section below.\n\n" + "\n\n".join(blocks)
    )
    result = call_structured(
        model=model, system=SYSTEM_PROMPT, user=user, schema_cls=ChapterDecisions,
        embed_schema=True, max_tokens=4000, max_retries=2, temperature=None,
        log_prefix=f"[{state}]", logger=log,
    )
    return result.decisions if result else []


def _to_scope_entry(d: SectionDecision, valid: set[str]) -> dict:
    """Map an LLM decision to a merged-scope entry (reusing walker scope_source
    values + scope_method='llm' for provenance). Pass 3 only ever produces
    enumeration or undetermined — never universal."""
    if d.scope == "specific":
        profs = [p for p in d.professions if p in valid]
        if profs:
            return {"url": d.url, "scope_source": "inherited_enumeration",
                    "applies_to_professions": sorted(profs),
                    "scope_evidence": d.evidence, "scope_method": "llm"}
        # claimed specific but no recognizable profession → keep undetermined
    return {"url": d.url, "scope_source": "undetermined", "applies_to_professions": None,
            "scope_evidence": d.evidence, "scope_method": "llm"}


def run_state(state: str, model: str = DEFAULT_MODEL) -> dict | None:
    targets = undetermined_sections(state)
    if not targets:
        log.info("[%s] no undetermined sections — nothing to do", state)
        return None
    valid = valid_professions(state)
    valid_set = set(valid)

    from collections import defaultdict
    by_chap: dict[str, list[dict]] = defaultdict(list)
    for s in targets:
        by_chap[s["chapter"]].append(s)

    log.info("[%s] %d undetermined sections across %d chapters → asking %s",
             state, len(targets), len(by_chap), model)
    entries: list[dict] = []
    for chap, secs in by_chap.items():
        for i in range(0, len(secs), MAX_SECTIONS_PER_CALL):
            batch = secs[i:i + MAX_SECTIONS_PER_CALL]
            decisions = _decide_batch(state, batch, valid, model)
            by_url = {d.url: d for d in decisions}
            for s in batch:
                d = by_url.get(s["url"])
                if d is None:
                    continue  # model omitted it → leave undetermined (no entry)
                entries.append(_to_scope_entry(d, valid_set))

    from collections import Counter
    counts = Counter(e["scope_source"] for e in entries)
    record = {
        "state": state,
        "decided_at": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "n_undetermined_in": len(targets),
        "decision_counts": dict(counts),
        "decisions": entries,
    }
    out = UMBRELLA_SCOPE_LLM_DIR / f"{state}.json"
    out.write_text(json.dumps(record, indent=2, ensure_ascii=False))
    log.info("[%s] wrote %s — decisions: %s", state, out.name, dict(counts))
    return record


# ---------------------------------------------------------------------------
# Merge: overlay LLM decisions onto walker output for consumers
# ---------------------------------------------------------------------------

def merge_scope(state: str) -> dict | None:
    """Walker scope with LLM decisions overlaid (each section tagged with
    scope_method). Delegates to the shared loader so there's one merge."""
    from pipeline.merged_scope import load_merged_scope
    return load_merged_scope(state)


# ---------------------------------------------------------------------------
# Audit: flag LLM enumerations that may be over-inclusions / mis-mappings
# ---------------------------------------------------------------------------

# Evidence that references a chapter/title/article number suggests a cite-based
# mapping (LLM resolved "chapter 474" -> a profession), where the profession
# name legitimately won't appear in the text.
_CITE_IN_EVIDENCE = re.compile(r"chapter|chs?\.|title|article|part\s+\d|\d{2,}", re.I)


def _profession_terms_by_id() -> dict[str, list[str]]:
    from collections import defaultdict
    from pipeline.discover.assign_umbrella_scope import _load_profession_terms
    by_pid: dict[str, list[str]] = defaultdict(list)
    for pid, term, _exc in _load_profession_terms():
        by_pid[pid].append(term)
    return by_pid


def audit_enumerations(state: str) -> list[dict]:
    """Review candidates: LLM enumerations whose assigned profession is NOT
    named anywhere in its chapter's text AND whose evidence cites no
    chapter/number. These are the higher-risk cases — the LLM may have inferred
    a profession from the chapter's overall scope rather than the text.

    Heuristic, not a verdict: grounding is checked against professions.yaml
    terms, so board-name wording the term list doesn't cover (e.g. "State
    Medical Board" for `medicine`) can produce false flags. Use it to direct a
    human spot-check, not to auto-reject.
    """
    from collections import defaultdict
    llm_path = UMBRELLA_SCOPE_LLM_DIR / f"{state}.json"
    text_path = UMBRELLA_TEXT_DIR / f"{state}.json"
    if not (llm_path.exists() and text_path.exists()):
        return []
    by_pid = _profession_terms_by_id()
    chap_text: dict[str, str] = defaultdict(str)
    url_chap: dict[str, str] = {}
    for s in json.loads(text_path.read_text()).get("sections", []):
        c = s.get("umbrella_chapter_slug", "")
        chap_text[c] += " " + (s.get("text") or "").lower()
        url_chap[s.get("url")] = c

    candidates: list[dict] = []
    for e in json.loads(llm_path.read_text()).get("decisions", []):
        if e.get("scope_source") != "inherited_enumeration":
            continue
        if _CITE_IN_EVIDENCE.search(e.get("scope_evidence", "")):
            continue  # cite-based mapping — name legitimately absent
        ctext = chap_text.get(url_chap.get(e.get("url"), ""), "")
        ungrounded = [
            p for p in (e.get("applies_to_professions") or [])
            if not any(t in ctext for t in by_pid.get(p, []))
        ]
        if ungrounded:
            candidates.append({
                "state": state,
                "url": e.get("url"),
                "ungrounded_professions": ungrounded,
                "evidence": e.get("scope_evidence", "")[:140],
            })
    return candidates


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _applied_states_with_undetermined() -> list[str]:
    out = []
    for p in record_files(UMBRELLA_SCOPE_DIR):
        scope = json.loads(p.read_text())
        if any(s.get("scope_source") == "undetermined" for s in scope.get("sections", [])):
            out.append(p.stem)
    return out


def validate_fl() -> None:
    """The FL § 455 trap: chapter-455 sections must NOT be classified universal
    by Pass 3 (they're DBPR-scoped). Reports pass/fail."""
    merged = merge_scope("FL")
    if merged is None:
        print("[validate-fl] no FL scope output", file=sys.stderr)
        return
    c455 = [s for s in merged["sections"] if s.get("umbrella_chapter_slug") == "chapter-455"]
    llm_decided = [s for s in c455 if s.get("scope_method") == "llm"]
    wrong = [s for s in c455 if s.get("scope_source") == "universal"]
    print(f"[validate-fl] chapter-455: {len(c455)} sections, {len(llm_decided)} LLM-decided, "
          f"{len(wrong)} wrongly universal")
    if wrong:
        print("  FAIL — these were called universal (should be specific/undetermined):")
        for s in wrong[:5]:
            print(f"    {s.get('label','')[:60]} | {s.get('scope_evidence','')[:80]}")
    else:
        print("  PASS — chapter-455 not over-classified as universal")


def main() -> None:
    ap = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    target = ap.add_mutually_exclusive_group()
    target.add_argument("--state")
    target.add_argument("--states")
    target.add_argument("--all", action="store_true",
                        help="All applied states that have undetermined sections")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--validate-fl", action="store_true", help="Run the FL § 455 trap check and exit")
    ap.add_argument("--audit", action="store_true",
                    help="Don't call the LLM — report enumeration review candidates "
                         "(professions not grounded in the chapter text, no citation)")
    args = ap.parse_args()

    if args.validate_fl and not (args.state or args.states or args.all):
        validate_fl()
        return

    if args.state:
        targets = [args.state.upper()]
    elif args.states:
        targets = [s.strip().upper() for s in args.states.split(",") if s.strip()]
    elif args.all:
        if args.audit:
            targets = [p.stem for p in record_files(UMBRELLA_SCOPE_LLM_DIR)]
        else:
            targets = _applied_states_with_undetermined()
    else:
        sys.exit("Specify --state / --states / --all (or --validate-fl).")

    if args.audit:
        total = 0
        for st in targets:
            cands = audit_enumerations(st)
            total += len(cands)
            for c in cands:
                leaf = c["url"].rstrip("/").split("/")[-1]
                print(f"{st} {leaf}: {c['ungrounded_professions']} | ev: {c['evidence']}")
        print(f"\n{total} enumeration review candidate(s) across {len(targets)} state(s) "
              f"(heuristic — board-name wording may false-flag; spot-check, don't auto-reject)")
        return

    for st in targets:
        try:
            run_state(st, args.model)
        except Exception:
            log.exception("[%s] crashed", st)

    if args.validate_fl and "FL" in targets:
        validate_fl()


if __name__ == "__main__":
    main()
