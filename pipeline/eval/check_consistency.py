"""Deterministic cross-field consistency check for structured records.

The extraction prompt (config/prompts.yaml) states several invariants that the
form-of-regulation fields MUST satisfy, but the model occasionally violates its
own instructions (notably for title-protection professions, where the
`regulatory_model` rung flip-flops run-to-run). This harness re-checks those
invariants deterministically and reports violations — it does NOT rewrite values
(reliable detection over silent auto-correction; a flagged record is re-extracted
or adjudicated by hand).

Only the invariants the prompt states *decisively* are enforced. `is_mandatory`
vs the rung is deliberately NOT checked: the prompt's own definition is ambiguous
for title-protection schemes ("required to practice OR claim the protected title"
→ True, but "False if optional (e.g. voluntary certification that only protects
the title)" → False), so either value is defensible there.

Invariants (prompts.yaml:138-216):
  V1  regulatory_model ∈ {license, mandatory_certification} ⟹ scope_protection = true
      ("license and mandatory_certification both REQUIRE scope_protection = true";
       the DECISIVE TEST: scope_protection false + title-only ⟹ voluntary_certification)
  V2a credential_type = none ⟹ regulatory_model = market_forces
  V2b regulatory_model = market_forces ⟹ credential_type = none
      ("market_forces means no such state credential exists")
  V3  regulatory_model = market_forces ⟹ is_mandatory not true
      (no state credential exists, so holding one cannot be mandatory)

Usage:
  python -m pipeline.eval.check_consistency [--profession P] [--states A,B]
  # exit code 1 if any violations found (CI-friendly)
"""

from __future__ import annotations

import argparse
import csv
import json
import sys

from pipeline.paths import STRUCTURED_DIR
from pipeline._records import record_files

REPORT_PATH = STRUCTURED_DIR / "_consistency_report.csv"

_SCOPE_RUNGS = {"license", "mandatory_certification"}


def _val(field: object) -> object:
    """Pull `.value` from an Evidence-wrapped field; None if the field is null."""
    if isinstance(field, dict):
        return field.get("value")
    return None


def _cite(field: object) -> str:
    if isinstance(field, dict):
        return f"{field.get('citation') or ''} — {(field.get('quote') or '')[:80]}".strip(" —")
    return ""


def check_record(profession: str, state: str, record: dict) -> list[dict]:
    lic = record.get("licensure") or {}
    rm = _val(lic.get("regulatory_model"))
    scope = _val(lic.get("scope_protection"))
    title = _val(lic.get("title_protection"))
    cred = _val(lic.get("credential_type"))
    mand = _val(lic.get("is_mandatory"))

    violations: list[dict] = []

    def flag(rule: str, detail: str) -> None:
        violations.append({
            "profession": profession, "state": state, "rule": rule, "detail": detail,
            "regulatory_model": rm, "scope_protection": scope, "title_protection": title,
            "credential_type": cred, "is_mandatory": mand,
            "rm_evidence": _cite(lic.get("regulatory_model")),
            "scope_evidence": _cite(lic.get("scope_protection")),
        })

    # V1: scope-protecting rungs require scope_protection = true.
    if rm in _SCOPE_RUNGS and scope is False:
        flag("V1_rung_requires_scope_protection",
             f"regulatory_model={rm} but scope_protection=false "
             f"(decisive test → should be voluntary_certification)")

    # V2a: credential_type none ⟹ market_forces.
    if cred == "none" and rm is not None and rm != "market_forces":
        flag("V2a_credential_none_requires_market_forces",
             f"credential_type=none but regulatory_model={rm}")

    # V2b: market_forces ⟹ credential_type none.
    if rm == "market_forces" and cred is not None and cred != "none":
        flag("V2b_market_forces_requires_credential_none",
             f"regulatory_model=market_forces but credential_type={cred}")

    # V3: market_forces ⟹ not mandatory.
    if rm == "market_forces" and mand is True:
        flag("V3_market_forces_not_mandatory",
             "regulatory_model=market_forces but is_mandatory=true")

    return violations


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", default="", help="Only this profession (default: all)")
    ap.add_argument("--states", default="", help="Comma-separated subset of states")
    args = ap.parse_args()

    only_states = {s.strip().upper() for s in args.states.split(",") if s.strip()}
    prof_dirs = (
        [STRUCTURED_DIR / args.profession] if args.profession
        else sorted(p for p in STRUCTURED_DIR.iterdir() if p.is_dir())
    )

    all_violations: list[dict] = []
    n_records = 0
    for pdir in prof_dirs:
        if not pdir.is_dir():
            continue
        for jf in record_files(pdir):
            state = jf.stem
            if only_states and state not in only_states:
                continue
            n_records += 1
            try:
                record = json.loads(jf.read_text())
            except json.JSONDecodeError:
                continue
            all_violations.extend(check_record(pdir.name, state, record))

    if all_violations:
        REPORT_PATH.write_text("")
        with REPORT_PATH.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(all_violations[0].keys()))
            w.writeheader()
            w.writerows(all_violations)
    elif REPORT_PATH.exists():
        # Clean run: drop the stale report so it never lingers showing
        # violations that have since been fixed.
        REPORT_PATH.unlink()

    # Console summary
    by_rule: dict[str, int] = {}
    for v in all_violations:
        by_rule[v["rule"]] = by_rule.get(v["rule"], 0) + 1
    print(f"checked {n_records} records across {len(prof_dirs)} profession(s)")
    print(f"violations: {len(all_violations)}")
    for rule, n in sorted(by_rule.items()):
        print(f"  {rule}: {n}")
    for v in all_violations:
        print(f"  [{v['profession']}/{v['state']}] {v['rule']}: {v['detail']}")
    if all_violations:
        print(f"\nwrote {REPORT_PATH}")
        sys.exit(1)
    print("all records consistent")


if __name__ == "__main__":
    main()
