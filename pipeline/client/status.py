"""Client-facing pipeline status + cost planner (READ-ONLY).

Answers, for every (occupation, state): how far did it get through the pipeline,
and what would it cost to finish? Walks only the committed stage dirs plus the
gap-harvest locator results — no fetch, no LLM, no writes outside results/status/.

    python -m pipeline.client.status            # write results/status/status.json + print summary

The dashboard (pipeline/client/dashboard.py) reads the JSON this emits. Keeping the
computation here (not in the HTML) means one definition of "what stage is this cell at"
and "what does it cost to finish", reused by both the report and the runner.

Reuses (no reimplementation):
  - pipeline.paths                              stage output dirs, taxonomy filter
  - pipeline.config.loaders.load_professions    the profession list
  - gap_harvest.coverage._has_corpus            corpus-present test (text stage)
  - gap_harvest._common                         ALL_STATES + locator loader
"""
from __future__ import annotations

import json

from pipeline.paths import (
    TEXT_DIR, CLEAN_DIR, TRIMMED_DIR, STRUCTURED_DIR, DISCOVERED_DIR, RESULTS_DIR,
)
from pipeline.config.loaders import load_professions, load_verified_absences, cost_for
from pipeline.discover.gap_harvest import _common as C
from pipeline.discover.gap_harvest.coverage import _has_corpus
from pipeline.ingest._trim_health import is_poisoned
from pipeline import provenance


def _poisoned_cells() -> list[str]:
    """Every trimmed corpus that degraded to keep-everything (trim LLM failed).
    Extract-preflight blocks these per-queue; surfacing the repo-wide list here
    makes them a standing, proactive signal instead of a per-run surprise. See
    pipeline.extract.verify_negatives / _trim_health.is_poisoned."""
    import json as _json
    out = []
    for f in sorted(TRIMMED_DIR.glob("*/*.json")):
        if f.name.startswith("_"):
            continue
        try:
            if is_poisoned(_json.loads(f.read_text())):
                out.append(f"{f.parent.name}/{f.stem}")
        except Exception:
            continue
    return out

# --- cost model ----------------------------------------------------------------
# From docs/runbooks/gap_harvest_plan_2026-07-05.md: the only per-cell $ steps are
# the two LLM stages. clean (deterministic), pull (fetch time, not $), and publish
# (deterministic) are free. Kept here as the single source of truth so the runner
# and dashboard quote the same numbers.
COST_TRIM = cost_for("trim")        # trim_state, Haiku
COST_EXTRACT = cost_for("extract")  # extract_state_batch, Sonnet
COST_TO_EXTRACT = COST_EXTRACT
COST_TO_TRIM = COST_TRIM + COST_EXTRACT   # trim then extract
# discover_schema, Sonnet: ONE call per profession (reads all its states' trimmed
# corpora at once), not per cell — measured ~$1/profession in a real run (same
# runbook: a 40-profession batch ran ~$40 for schemas). Distinct from COST_TRIM/
# COST_EXTRACT because it's a one-time profession-level cost, never a per-state one.
COST_SCHEMA = cost_for("schema")

OUT = RESULTS_DIR / "status" / "status.json"

# Stage a cell has reached -> (remaining $ to finish, needs a fetch first?).
# "ready" stages are everything the client can run themselves (no fetch): the corpus
# is already on disk. "needs-fetch"/"absent"/"unknown" have no local corpus.
_READY_COST = {
    "trimmed": COST_TO_EXTRACT,
    "cleaned": COST_TO_TRIM,
    "pulled": COST_TO_TRIM,   # clean is free, so same $ as cleaned
}


def _stage(prof: str, state: str, locator: dict, absences: dict | None = None) -> str:
    """Furthest stage reached for one (profession, state). Checked newest-first."""
    if (STRUCTURED_DIR / prof / f"{state}.json").exists():
        return "done"
    if (TRIMMED_DIR / prof / f"{state}.json").exists():
        return "trimmed"
    if (CLEAN_DIR / prof / f"{state}.json").exists():
        return "cleaned"
    if _has_corpus(prof, state):
        return "pulled"
    # No local corpus. A hand-verified absence is a correct-blank, NOT a fetch gap —
    # check it BEFORE the locator, because the gap-harvest locator often (mis-)locates
    # a thematically-adjacent chapter for an occupation the state doesn't license,
    # which would otherwise be counted as pending scrape work forever.
    if absences and state in (absences.get(prof) or {}):
        return "absent"
    # Is the law even located?
    loc = locator.get(prof, {}).get(state)
    if loc is None:
        return "unknown"          # never searched for this pair
    url = loc.get("url")
    if url in (None, "null", ""):
        return "absent"           # searched, no governing chapter found
    return "needs-fetch"          # located a URL, corpus not pulled yet


def _chapter_urls(prof: str, state: str) -> list | None:
    """The Justia chapter URL(s) the corpus was built from — the definitive source,
    present in every pulled corpus (unlike the locator, which misses published profs).
    Reads the deepest stage available."""
    for d in (TRIMMED_DIR, CLEAN_DIR, TEXT_DIR):
        f = d / prof / f"{state}.json"
        if f.exists():
            try:
                data = json.loads(f.read_text())
            except Exception:
                continue
            urls = data.get("chapter_urls") if isinstance(data, dict) else None
            if urls:
                return urls
    return None


def _has_schema(prof: str) -> bool:
    """Extract needs a discovered schema (results/discovered/<prof>.json); without one the
    extract preflight drops the cell, so a corpus-on-disk cell can't actually be finished."""
    return (DISCOVERED_DIR / f"{prof}.json").exists()


def _refresh_cost(stale_stage: str) -> float:
    """Cost to bring a stale done cell back to current by re-running from the earliest
    stale stage. clean is free, so a stale clean/trim both cost trim+extract."""
    return COST_EXTRACT if stale_stage == "extract" else COST_TO_TRIM


def build() -> dict:
    profs = [k for k in load_professions() if not k.startswith("_")]
    locator = C.load_json("locator_results.json", {})
    absences = load_verified_absences()

    professions: dict[str, dict] = {}
    for prof in sorted(profs):
        # Extract can't run without a discovered schema (results/discovered/<prof>.json);
        # the extract preflight drops these cells. Without knowing that, a client could pay
        # for trim on a corpus that can never reach extract — so we gate it here.
        has_schema = _has_schema(prof)
        states: dict[str, dict] = {}
        summary = {"done": 0, "done_current": 0, "done_stale": 0, "done_unstamped": 0,
                   "ready": 0, "needs_schema": 0, "needs_fetch": 0, "absent": 0, "unknown": 0,
                   "cost_to_finish": 0.0, "cost_to_refresh": 0.0, "cost_runnable": 0.0}
        for state in C.ALL_STATES:
            stage = _stage(prof, state, locator, absences)
            cell = {"stage": stage, "cost": 0.0, "run": False}
            is_verified_absence = state in (absences.get(prof) or {})

            # Traceability: where the law came from + when it was last processed.
            loc = locator.get(prof, {}).get(state) or {}
            urls = _chapter_urls(prof, state)
            if not urls and loc.get("url") and loc.get("url") != "null":
                urls = [loc["url"]]
            if urls and not is_verified_absence:
                # A verified absence's locator URL is a mis-location (the state doesn't
                # license this) — don't advertise it as this cell's source.
                cell["source_urls"] = urls
            if is_verified_absence:
                cell["source_label"] = "not state-regulated (verified)"
            elif loc.get("label"):
                cell["source_label"] = loc["label"]
            last = provenance.last_stamped(prof, state)
            if last:
                cell["last_processed"] = last

            if stage == "done":
                verdict, stale_stage = provenance.cell_freshness(prof, state)
                cell["fresh"] = verdict
                summary["done"] += 1
                if verdict == "stale":
                    cell["cost"] = _refresh_cost(stale_stage)
                    cell["run"] = True
                    cell["stale_stage"] = stale_stage
                    summary["done_stale"] += 1
                    summary["cost_to_refresh"] += cell["cost"]
                elif verdict == "current":
                    summary["done_current"] += 1
                else:  # unstamped — provenance unknown; don't auto-charge to re-run
                    summary["done_unstamped"] += 1
            elif stage in ("pulled", "cleaned", "trimmed"):  # corpus on disk
                if has_schema:
                    cell["cost"] = _READY_COST[stage]
                    cell["run"] = True
                    summary["ready"] += 1
                    summary["cost_to_finish"] += cell["cost"]
                else:
                    # No schema → extract can't run. Keep it out of the queue (run stays
                    # False, cost 0) and flag it so the dashboard shows *why* it's stuck.
                    cell["needs_schema"] = True
                    summary["needs_schema"] += 1
            elif stage == "needs-fetch":
                cell["cost"] = COST_TO_TRIM  # informational: needs a fetch (can't run yet)
                summary["needs_fetch"] += 1
            elif stage == "absent":
                summary["absent"] += 1
            else:
                summary["unknown"] += 1

            cell["cost"] = round(cell["cost"], 2)
            states[state] = cell

        summary["cost_runnable"] = round(summary["cost_to_finish"] + summary["cost_to_refresh"], 2)
        summary["cost_to_finish"] = round(summary["cost_to_finish"], 2)
        summary["cost_to_refresh"] = round(summary["cost_to_refresh"], 2)
        summary["has_schema"] = has_schema
        # One-time, profession-level (not per-cell): only worth counting if there's
        # actually corpus on disk waiting on it (discover_schema needs trimmed text
        # to read; charging for a profession with zero pulled cells is premature).
        summary["cost_schema"] = COST_SCHEMA if not has_schema and summary["needs_schema"] > 0 else 0.0
        professions[prof] = {"states": states, "summary": summary}

    def _sum(key):
        return sum(p["summary"][key] for p in professions.values())

    totals = {
        "professions": len(profs),
        "professions_no_schema": sum(1 for p in professions.values() if not p["summary"]["has_schema"]),
        "professions_needing_schema_now": sum(1 for p in professions.values() if p["summary"]["cost_schema"] > 0),
        "cells_done": _sum("done"),
        "cells_current": _sum("done_current"),
        "cells_stale": _sum("done_stale"),
        "cells_unstamped": _sum("done_unstamped"),
        "cells_ready": _sum("ready"),
        "cells_needs_schema": _sum("needs_schema"),
        "cells_needs_fetch": _sum("needs_fetch"),
        "cost_to_finish": round(_sum("cost_to_finish"), 2),
        "cost_to_refresh": round(_sum("cost_to_refresh"), 2),
        "cost_all_schemas": round(_sum("cost_schema"), 2),
    }
    poisoned = _poisoned_cells()
    totals["poisoned_cells"] = len(poisoned)
    return {
        "poisoned_cells": poisoned,
        "cost_model": {"trim": COST_TRIM, "extract": COST_EXTRACT, "schema": COST_SCHEMA,
                       "clean": 0.0,
                       "note": "clean/pull/publish are free; trim+extract are per-cell; "
                               "schema is one-time per occupation, not per state"},
        "totals": totals,
        "professions": professions,
    }


def main() -> None:
    data = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1))
    t = data["totals"]
    print(f"wrote {OUT}")
    print(f"  {t['professions']} professions  ·  {t['cells_done']} done "
          f"({t['cells_current']} current / {t['cells_stale']} stale / {t['cells_unstamped']} unstamped)  ·  "
          f"{t['cells_ready']} ready to process (${t['cost_to_finish']:.2f})  ·  "
          f"{t['cells_stale']} stale (${t['cost_to_refresh']:.2f})  ·  "
          f"{t['cells_needs_fetch']} need a fetch")
    print(f"  {t['professions_no_schema']} professions have no schema yet "
          f"({t['cells_needs_schema']} corpus cells blocked from extract until one is discovered) — "
          f"{t['professions_needing_schema_now']} of those have corpus on disk ready for "
          f"discover_schema now (${t['cost_all_schemas']:.2f} total, one-time per occupation)")
    if t["poisoned_cells"]:
        print(f"  ⚠ {t['poisoned_cells']} POISONED trim(s) (degraded to keep-everything; extract-blocked) — "
              f"re-trim, or re-map + re-fetch if over-broad. See data['poisoned_cells'].")


if __name__ == "__main__":
    main()
