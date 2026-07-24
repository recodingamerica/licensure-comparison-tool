"""Scope-vocabulary discovery — turn a free-text scope LIST field into a
canonical enumerated vocabulary discovered FROM THE CORPUS (no hardcoding).

This is the discovery half of the "discover the union → per-state matrix"
capability (docs/plans/scope_discovery_productionization.md). For a dimension
anchored by an existing discovered `list[str]` field (e.g. optometry
`laser_procedures_authorized`), we build the UNION of distinct items any state
names — including items that appear only inside a PROHIBITION ("may not perform
laser surgery"), which never show up in an affirmative list value. That union
is what `extract_state` later classifies per state as authorized / prohibited /
not_addressed (see build_profession_specific_model, which reads this file).

Why scan the corpus, not just the extracted list values: for scope fields the
affirmative list is often empty in most states (they prohibit or are silent), so
the values alone under-cover the vocabulary. We derive trigger keywords for the
dimension with the LLM (from the field name/description + whatever example values
DO exist), select statute sentences that mention them, then synthesize the
canonical union. Keywords are model-derived, so nothing about the vocabulary is
hand-written per profession.

Input:  results/discovered/<profession>.json   (which list fields exist)
        results/trimmed/<profession>/<STATE>.json  (corpus to scan; falls back to clean/)
        results/structured/<profession>/<STATE>.json  (example values/quotes, if any)
Output: results/scope_vocab/<profession>.json
  {
    "profession": "optometry",
    "dimensions": [
      {"source_field": "laser_procedures_authorized",
       "matrix_field": "scope__laser_procedures",
       "eval_flavor": "three_state",
       "vocab": ["YAG laser capsulotomy", "selective laser trabeculoplasty", ...],
       "keywords": [...], "rationale": "...", "states_scanned": ["AK", ...]},
      ...
    ]
  }

Run:
  python -m pipeline.discover.scope_vocab --profession optometry
  python -m pipeline.discover.scope_vocab --profession optometry \
      --fields laser_procedures_authorized,minor_surgical_procedures_authorized
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from typing import Literal

from pydantic import BaseModel, Field

from pipeline._env import load_env  # noqa: E402
load_env()

from pipeline._llm import call_structured
from pipeline._records import record_files
from pipeline.extract.model_helpers import is_evidence_node
from pipeline.paths import (
    DISCOVERED_DIR,
    STRUCTURED_DIR,
    TRIMMED_DIR,
    CLEAN_DIR,
    SCOPE_VOCAB_DIR,
    LOGS_DIR,
)
from pipeline.config.loaders import model_for

LOG_PATH = LOGS_DIR / "scope_vocab.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
SCOPE_VOCAB_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("scope_vocab")

# Vocabulary design is the same reasoning quality as schema discovery — use that
# stage's model (Sonnet by default). Model names live only in config/models.yaml.
MODEL = model_for("schema")

# Cap sentences fed to vocab synthesis (prototype-validated ceiling).
_MAX_SNIPPETS = 200
_MAX_SNIPPET_LEN = 450


# ---------- LLM output schemas ----------

class DimensionPlan(BaseModel):
    # No class docstring: with embed_schema it becomes the schema's object-level
    # "description", which the model echoes back as a bogus field.
    eval_flavor: Literal["three_state", "present_absent", "skip"] = Field(
        default="three_state",
        description=(
            "three_state = a scope/procedure dimension where each item can be "
            "authorized, prohibited, or not addressed by a state (e.g. laser "
            "procedures, surgical procedures). present_absent = an enumerable "
            "roster where each item is simply present or absent in a state (e.g. "
            "licensure exemptions, protected titles). skip = free-text, not a "
            "meaningfully enumerable checklist."
        ),
    )
    keywords: list[str] = Field(
        description=(
            "10-30 lowercase words/short phrases whose presence in a statute "
            "sentence signals it is talking about THIS dimension — including the "
            "words a PROHIBITION would use (e.g. 'laser', 'surgery', 'may not "
            "perform', 'incision', 'excision'). Used to select candidate "
            "sentences; err toward recall."
        ),
    )


class VocabItem(BaseModel):
    canonical_name: str = Field(description="Concise, plain-English name for the distinct item")
    aliases: list[str] = Field(default_factory=list, description="Synonyms/variant phrasings seen across states")


class VocabSet(BaseModel):
    items: list[VocabItem]
    rationale: str = Field(default="", description="One sentence on how the union was drawn / notable merges")


# ---------- corpus + value gathering ----------

def _corpus_sections(profession: str, state: str) -> list[dict]:
    for base in (TRIMMED_DIR, CLEAN_DIR):
        p = base / profession / f"{state}.json"
        if p.exists():
            d = json.loads(p.read_text())
            secs = d.get("sections", d) if isinstance(d, dict) else d
            if secs:
                return [s for s in secs if isinstance(s, dict)]
    return []


def _states_with_corpus(profession: str) -> list[str]:
    src = TRIMMED_DIR / profession
    if not src.exists():
        src = CLEAN_DIR / profession
    if not src.exists():
        return []
    return [p.stem for p in record_files(src)]


def _discovered_list_fields(profession: str) -> list[dict]:
    """The discovered `list[...]` field specs — each is a candidate scope dimension."""
    path = DISCOVERED_DIR / f"{profession}.json"
    if not path.exists():
        sys.exit(f"missing discovered schema: {path}")
    data = json.loads(path.read_text())
    return [f for f in data.get("fields", []) if (f.get("type") or "").startswith("list")]


def _field_examples(profession: str, field: str, states: list[str], limit: int = 40) -> list[str]:
    """Example values + quotes for a field across states (may be sparse/empty).
    Feeds the keyword-derivation call so it anchors on real phrasing when present."""
    out: list[str] = []
    for st in states:
        p = STRUCTURED_DIR / profession / f"{st}.json"
        if not p.exists():
            continue
        rec = json.loads(p.read_text())
        node = (rec.get("profession_specific") or {}).get(field)
        if not isinstance(node, dict):
            continue
        val = node.get("value") if is_evidence_node(node) else None
        if isinstance(val, list):
            out.extend(str(v) for v in val if v)
        q = node.get("quote")
        if q:
            out.append(q)
        if len(out) >= limit:
            break
    # dedupe preserving order
    seen: set[str] = set()
    uniq = []
    for s in out:
        k = s.lower()[:120]
        if k not in seen:
            seen.add(k)
            uniq.append(s)
    return uniq


def _select_snippets(profession: str, states: list[str], keywords: list[str]) -> list[str]:
    """State-tagged statute sentences that mention any keyword. Deduped, capped."""
    if not keywords:
        return []
    rx = re.compile("|".join(re.escape(k) for k in keywords), re.I)
    snips: list[str] = []
    for st in states:
        for sec in _corpus_sections(profession, st):
            text = sec.get("text") or sec.get("body") or ""
            for sent in re.split(r"(?<=[.;:])\s+", text):
                sent = sent.strip()
                if sent and len(sent) < _MAX_SNIPPET_LEN and rx.search(sent):
                    snips.append(f"[{st}] {sent}")
    seen: set[str] = set()
    uniq = []
    for s in snips:
        k = re.sub(r"^\[[A-Z]{2}\]\s*", "", s).lower()[:100]
        if k not in seen:
            seen.add(k)
            uniq.append(s)
    return uniq[:_MAX_SNIPPETS]


# ---------- the two LLM passes ----------

_PLAN_SYSTEM = (
    "You are cataloguing how US state practice acts regulate a specific professional-scope "
    "dimension. Given the dimension's field name, description, and example statutory values, "
    "decide (1) how it should be evaluated per state and (2) the keywords that will find every "
    "relevant statute sentence — including sentences that PROHIBIT parts of the dimension, since "
    "prohibitions define the scope just as much as authorizations do."
)

_VOCAB_SYSTEM_TMPL = (
    "Build a controlled vocabulary of the distinct {dim} that US {prof} practice acts address. "
    "You are given relevant sentences drawn from many states. Output the UNION of distinct items "
    "as a canonical enumerated set: merge synonyms and trivial phrasing differences into one entry, "
    "but keep genuinely different items separate. The vocabulary will be applied to EVERY state as a "
    "fixed checklist, so it must include any item that ANY state names — including items that appear "
    "only inside an EXCLUSION or PROHIBITION list (those are in-scope items a state happens to forbid). "
    "Do NOT invent items no sentence supports. Aim for the natural granularity a regulator would use."
)


def _derive_plan(profession: str, field_spec: dict, examples: list[str]) -> DimensionPlan | None:
    user = json.dumps({
        "profession": profession,
        "field_name": field_spec["name"],
        "field_description": field_spec.get("description", ""),
        "example_values_and_quotes": examples[:40],
    }, ensure_ascii=False)
    log.info("[%s/%s] deriving dimension plan (%d examples)", profession, field_spec["name"], len(examples))
    return call_structured(
        model=MODEL, system=_PLAN_SYSTEM, user=user, schema_cls=DimensionPlan,
        embed_schema=True, max_tokens=1500, temperature=None,
        log_prefix=f"[{profession}/{field_spec['name']}/plan]", logger=log,
    )


def _synthesize_vocab(profession: str, dim_label: str, snippets: list[str]) -> VocabSet | None:
    system = _VOCAB_SYSTEM_TMPL.format(dim=dim_label, prof=profession)
    user = f"{dim_label} sentences across states:\n" + "\n".join(snippets)
    log.info("[%s] synthesizing vocab from %d snippets", profession, len(snippets))
    return call_structured(
        model=MODEL, system=system, user=user, schema_cls=VocabSet,
        embed_schema=True, max_tokens=4000, temperature=None,
        log_prefix=f"[{profession}/vocab]", logger=log,
    )


def _matrix_field_name(source_field: str) -> str:
    """Namespaced matrix field so it never collides with the source list field
    and downstream consumers can detect scope matrices by the `scope__` prefix."""
    base = re.sub(r"_(authorized|permitted|allowed)$", "", source_field)
    return f"scope__{base}"


def discover_dimension(profession: str, field_spec: dict, states: list[str]) -> dict | None:
    name = field_spec["name"]
    examples = _field_examples(profession, name, states)
    plan = _derive_plan(profession, field_spec, examples)
    if plan is None:
        log.error("[%s/%s] plan failed — skipping", profession, name)
        return None
    if plan.eval_flavor == "skip":
        log.info("[%s/%s] flavor=skip (not an enumerable checklist)", profession, name)
        return None

    snippets = _select_snippets(profession, states, plan.keywords)
    if len(snippets) < 2:
        log.info("[%s/%s] only %d snippets matched — skipping", profession, name, len(snippets))
        return None

    dim_label = field_spec.get("description") or name.replace("_", " ")
    vocab = _synthesize_vocab(profession, dim_label, snippets)
    if vocab is None or not vocab.items:
        log.error("[%s/%s] vocab synthesis failed/empty — skipping", profession, name)
        return None

    return {
        "source_field": name,
        "matrix_field": _matrix_field_name(name),
        "eval_flavor": plan.eval_flavor,
        "vocab": [it.canonical_name for it in vocab.items],
        "aliases": {it.canonical_name: it.aliases for it in vocab.items if it.aliases},
        "keywords": plan.keywords,
        "rationale": vocab.rationale,
        "states_scanned": states,
    }


def run(profession: str, only_fields: set[str] | None) -> None:
    states = _states_with_corpus(profession)
    if not states:
        sys.exit(f"no trimmed/clean corpus for {profession}")
    field_specs = _discovered_list_fields(profession)
    if only_fields:
        field_specs = [f for f in field_specs if f["name"] in only_fields]
        missing = only_fields - {f["name"] for f in field_specs}
        if missing:
            log.warning("requested fields not found as discovered list fields: %s", ", ".join(sorted(missing)))
    log.info("[%s] %d candidate list-field dimensions over %d states: %s",
             profession, len(field_specs), len(states), ", ".join(f["name"] for f in field_specs))

    dimensions = []
    for fs in field_specs:
        dim = discover_dimension(profession, fs, states)
        if dim is not None:
            dimensions.append(dim)
            log.info("[%s/%s] flavor=%s, %d vocab items", profession, fs["name"],
                     dim["eval_flavor"], len(dim["vocab"]))

    out_path = SCOPE_VOCAB_DIR / f"{profession}.json"
    out_path.write_text(json.dumps({
        "profession": profession,
        "dimensions": dimensions,
    }, indent=2, ensure_ascii=False))
    log.info("[%s] wrote %s — %d scope dimensions", profession, out_path, len(dimensions))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True)
    ap.add_argument("--fields", default="",
                    help="Comma-separated discovered list-field names to restrict to "
                         "(default: every discovered list[str] field).")
    args = ap.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set")

    only = {s.strip() for s in args.fields.split(",") if s.strip()} or None
    run(args.profession.lower(), only)


if __name__ == "__main__":
    main()
