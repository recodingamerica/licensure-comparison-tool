#!/usr/bin/env python
"""Post-grind downstream: turn harvested raw text into structured data.

The grind (_cdp_grind.py) only pulls raw text. This drives the rest of the
pipeline for professions that have text but no structured output yet:

  clean (local) -> trim (LLM) -> discover_schema if missing (LLM) -> extract (BATCH)

It does NOT pull (the grind owns Chrome) and does NOT publish (a separate,
deliberate step). Extraction goes through the Anthropic batch API (cheaper +
durable), accumulating ONE combined queue across all professions.

Run from repo root:
  pipeline/.venv/bin/python pipeline/results/batches/_cdp_downstream.py --dry-run
  pipeline/.venv/bin/python pipeline/results/batches/_cdp_downstream.py            # do it
  pipeline/.venv/bin/python pipeline/results/batches/_cdp_downstream.py --profession pharmacy
"""
import argparse, glob, json, os, subprocess, sys, datetime

ROOT = "/Users/abigailhaddad/Documents/repos/utah"
PY = f"{ROOT}/pipeline/.venv/bin/python"
LOG = f"{ROOT}/pipeline/results/batches/_cdp_downstream.log"
SKIP = {"_families"}


def log(msg):
    line = f"{datetime.datetime.now().isoformat(timespec='seconds')} {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def states_in(stage, prof):
    d = f"{ROOT}/pipeline/results/{stage}/{prof}"
    return {os.path.basename(f)[:-5] for f in glob.glob(d + "/*.json")} - {"_summary"}


def has_schema(prof):
    return os.path.exists(f"{ROOT}/pipeline/results/discovered/{prof}.json")


def in_flight_states():
    """{(prof, state)} that are already queued in a submitted batch (custom_ids).
    Prevents re-extracting states an in-flight batch will produce."""
    out = set()
    for fp in glob.glob(f"{ROOT}/pipeline/results/batches/msgbatch_*.json"):
        try:
            cids = json.load(open(fp)).get("custom_ids") or []
        except Exception:  # noqa: BLE001
            continue
        for cid in cids:
            if "__" in cid:
                p, s = cid.split("__", 1)
                out.add((p, s))
    return out


def professions_with_work():
    """Professions where text states exist that are neither structured yet nor
    already queued in an in-flight batch."""
    flight = in_flight_states()
    out = {}
    for d in glob.glob(f"{ROOT}/pipeline/results/text/*/"):
        prof = os.path.basename(d.rstrip("/"))
        if prof in SKIP:
            continue
        text = states_in("text", prof)
        structured = states_in("structured", prof)
        todo = sorted(text - structured - {s for (p, s) in flight if p == prof})
        if todo:
            out[prof] = todo
    return out


def sh(cmd):
    log("  $ " + " ".join(cmd))
    return subprocess.run(cmd, cwd=ROOT).returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", default="")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--model", default="")
    args = ap.parse_args()

    work = professions_with_work()
    if args.profession:
        p = args.profession.lower()
        todo = work.get(p)
        work = {p: todo} if todo else {}
    if not work:
        log("nothing to do — all harvested text is already structured")
        return

    log(f"=== DOWNSTREAM PLAN: {len(work)} professions, "
        f"{sum(len(v) for v in work.values())} (prof,state) to extract ===")
    for prof, states in sorted(work.items(), key=lambda kv: -len(kv[1])):
        schema = "schema OK" if has_schema(prof) else "NEEDS schema"
        log(f"  {prof}: {len(states)} states [{schema}] {states}")

    if args.dry_run:
        log("dry-run — stopping before any LLM calls")
        return

    queue = {}
    for prof, states in work.items():
        log(f"[{prof}] clean")
        sh([PY, "-m", "pipeline.ingest.clean_text", "--profession", prof])
        log(f"[{prof}] trim {len(states)} states")
        sh([PY, "-m", "pipeline.ingest.trim_state", "--profession", prof,
            "--states", ",".join(states)])
        if not has_schema(prof):
            log(f"[{prof}] discover_schema (was missing)")
            sh([PY, "-m", "pipeline.extract.discover_schema", "--profession", prof])
        if has_schema(prof):
            queue[prof] = states
        else:
            log(f"[{prof}] STILL no schema after discover — skipping extract")

    if not queue:
        log("no professions ready to extract")
        return
    qpath = f"{ROOT}/pipeline/results/batches/_downstream_queue.json"
    json.dump(queue, open(qpath, "w"), indent=2)
    log(f"submitting combined extract batch: {sum(len(v) for v in queue.values())} requests")
    cmd = [PY, "-m", "pipeline.extract.extract_state_batch", "submit", "--queue", qpath]
    if args.model:
        cmd += ["--model", args.model]
    sh(cmd)
    log("=== DOWNSTREAM SUBMITTED ===")


if __name__ == "__main__":
    main()
