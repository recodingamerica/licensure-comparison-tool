"""Gap loop — audit each record's EMPTY fields against OUR OWN text and route them.

The signal is self-grounded: for every schema field a record didn't fill, an LLM
reasons ONLY over the text we have and classifies it
  - answerable_missed : the value IS in our text, extraction missed it  → re-extract
  - not_in_text       : real, but absent from our corpus (lives in a chapter/source
                        we didn't pull, e.g. the administrative rules) → corpus wishlist
  - genuinely_na      : the state doesn't regulate this                → leave empty (correct)

So a "gap" never penalizes us for info outside the corpus; it becomes either a cheap
re-extract or a concrete "go fetch THIS" instruction. The aggregate wishlist across
states is the highest-leverage coverage signal (it's what told us the answers live in
the administrative rules). See docs/runbooks/automation_handoff_assessment.md.

Run:
  pipeline/.venv/bin/python -m pipeline.discover.gap_loop --profession dental_hygienist --states UT
  pipeline/.venv/bin/python -m pipeline.discover.gap_loop --profession optometry            # all states
  pipeline/.venv/bin/python -m pipeline.discover.gap_loop --profession optometry summary     # roll up the wishlist
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

from pydantic import BaseModel

from pipeline._env import load_env
load_env()

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _llm import call_structured, usage_summary  # noqa: E402
from paths import RESULTS_DIR  # noqa: E402

DISCOVERED = RESULTS_DIR / "discovered"
STRUCTURED = RESULTS_DIR / "structured"
TRIMMED = RESULTS_DIR / "trimmed"
OUT = RESULTS_DIR / "gap_audit"
MODEL = "claude-sonnet-4-6"


class Verdict(BaseModel):
    field: str
    classification: str        # answerable_missed | not_in_text | genuinely_na
    quote: str | None = None   # verbatim, only for answerable_missed
    likely_source: str | None = None  # for not_in_text: where it'd live (e.g. "administrative rules")
    reasoning: str = ""


class Audit(BaseModel):
    verdicts: list[Verdict]


SYSTEM = """You audit GAPS in a statute extraction. You get the FULL source statute text
for an occupation in one state and a list of fields that came back EMPTY. For each empty
field, reason ONLY over the text provided — never outside knowledge — and classify:
- answerable_missed: the answer IS present in this text and was missed. Give the verbatim quote.
- not_in_text: not in this text, but it is a real regulatable thing that lives in a source
  we likely didn't pull. Set likely_source to where (e.g. "administrative rules",
  "a separate interstate-compact statute", "the renewal/CE chapter").
- genuinely_na: this text shows the state does not regulate this / it does not apply.
Be strict: only answerable_missed if you can quote it from the provided text."""


def _schema_fields(o, out=None):
    out = {} if out is None else out
    if isinstance(o, dict):
        nm = o.get("field_name") or (o.get("name") if (o.get("description") or o.get("prompt")) else None)
        if nm:
            out[nm] = o.get("description") or o.get("prompt") or ""
        for v in o.values():
            _schema_fields(v, out)
    elif isinstance(o, list):
        for x in o:
            _schema_fields(x, out)
    return out


def _filled(record: dict) -> set[str]:
    out = set()
    for grp in ("licensure", "scope", "profession_specific"):
        for k, v in (record.get(grp) or {}).items():
            if isinstance(v, dict) and v.get("value") not in (None, "", []):
                out.add(k)
    return out


def audit_state(profession: str, state: str, sf: dict) -> Audit | None:
    rec_fp = STRUCTURED / profession / f"{state}.json"
    trim_fp = TRIMMED / profession / f"{state}.json"
    if not rec_fp.exists() or not trim_fp.exists():
        return None
    record = json.loads(rec_fp.read_text())
    gaps = {k: d for k, d in sf.items() if k not in _filled(record)}
    if not gaps:
        print(f"  {state}: no gaps")
        return Audit(verdicts=[])
    text = "\n\n".join(s.get("text", "") for s in json.loads(trim_fp.read_text()).get("sections", []) if s.get("text"))
    user = (f"OCCUPATION: {profession} ({state})\n\nEMPTY FIELDS:\n"
            + "\n".join(f"- {k}: {v[:90]}" for k, v in gaps.items())
            + f"\n\nSOURCE TEXT:\n{text[:60000]}")
    res = call_structured(model=MODEL, system=SYSTEM, user=user, schema_cls=Audit,
                          embed_schema=True, log_prefix=f"[{state}]")
    if res is None:
        print(f"  {state}: audit failed — skipping"); return None
    OUT.joinpath(profession).mkdir(parents=True, exist_ok=True)
    (OUT / profession / f"{state}.json").write_text(res.model_dump_json(indent=1))
    c = Counter(v.classification for v in res.verdicts)
    print(f"  {state}: {len(res.verdicts)} gaps → {dict(c)}")
    return res


def summary(profession: str) -> None:
    """Roll the per-state audits into a coverage wishlist + re-extract list."""
    wishlist: dict[str, dict] = defaultdict(lambda: {"states": set(), "sources": Counter()})
    reextract: dict[str, set] = defaultdict(set)
    for fp in sorted((OUT / profession).glob("*.json")):
        st = fp.stem
        for v in json.loads(fp.read_text()).get("verdicts", []):
            if v["classification"] == "not_in_text":
                w = wishlist[v["field"]]
                w["states"].add(st)
                if v.get("likely_source"):
                    w["sources"][v["likely_source"]] += 1
            elif v["classification"] == "answerable_missed":
                reextract[st].add(v["field"])
    print(f"\n=== {profession}: corpus wishlist (fields absent from our text, by # states) ===")
    for f, w in sorted(wishlist.items(), key=lambda kv: len(kv[1]["states"]), reverse=True)[:20]:
        src = w["sources"].most_common(1)[0][0] if w["sources"] else "?"
        print(f"  {len(w['states']):2} states  {f}  → likely in: {src}")
    if reextract:
        print(f"\n=== re-extract candidates (value IS in our text, was missed) ===")
        for st, fields in sorted(reextract.items()):
            print(f"  {st}: {sorted(fields)}")
    else:
        print("\n  no answerable_missed gaps — extraction quality is good on the text we have.")
    # the dominant missing source across the profession
    allsrc = Counter()
    for w in wishlist.values():
        allsrc += w["sources"]
    if allsrc:
        print(f"\n  TOP MISSING SOURCE(S): {allsrc.most_common(3)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True)
    ap.add_argument("mode", nargs="?", default="audit", choices=["audit", "summary"])
    ap.add_argument("--states", default="")
    args = ap.parse_args()
    prof = args.profession.lower()
    if args.mode == "summary":
        summary(prof); return
    sch_fp = DISCOVERED / f"{prof}.json"
    if not sch_fp.exists():
        sys.exit(f"no schema: {sch_fp}")
    sf = _schema_fields(json.loads(sch_fp.read_text()))
    states = ([s.strip().upper() for s in args.states.split(",") if s.strip()]
              or sorted(os.path.basename(f)[:-5] for f in glob.glob(str(STRUCTURED / prof / "*.json")) if "_summary" not in f))
    for st in states:
        audit_state(prof, st, sf)
    usage_summary()
    print(f"\nnext: pipeline/.venv/bin/python -m pipeline.discover.gap_loop --profession {prof} summary")


if __name__ == "__main__":
    main()
