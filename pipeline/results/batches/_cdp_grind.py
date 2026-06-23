#!/usr/bin/env python
"""CDP-Justia harvest grind — pull every mapped-but-unpulled (profession, state).

One process (shares the single debug Chrome). Resumable: recomputes the missing
set per profession each run, so killing/restarting just continues. Commits per
profession (storage strategy: commit-to-git, push periodically). Ordered by
harvest gap (biggest first). Continues past any single-profession failure.

Run from repo root:
  JUSTIA_CDP_URL=http://localhost:9222 PULL_HOST_DELAY=7 \
    pipeline/.venv/bin/python pipeline/results/batches/_cdp_grind.py
"""
import csv, glob, json, os, subprocess, sys, datetime

ROOT = "/Users/abigailhaddad/Documents/repos/utah"
PY = f"{ROOT}/pipeline/.venv/bin/python"
LOG = f"{ROOT}/pipeline/results/batches/_cdp_grind.log"
# Professions already complete or in-progress by other means — skip entirely.
SKIP_PROFS = {"_families"}
# Published + trades are handled separately; grind the rest. (Trades still have a
# small gap but are managed by their own batch flow; include them last if desired.)
TRADES = {"construction_trades", "electrician", "plumbing", "hvac"}
PUBLISHED = {"dentistry", "dietetics", "medicine", "nursing", "optometry",
             "podiatry", "public_accountancy"}


def log(msg):
    line = f"{datetime.datetime.now().isoformat(timespec='seconds')} {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def pulled_states(prof):
    d = f"{ROOT}/pipeline/results/text/{prof}"
    return {os.path.basename(f)[:-5] for f in glob.glob(d + "/*.json")} - {"_summary"}


def mapped_states(prof):
    fp = f"{ROOT}/pipeline/results/profession_index/{prof}.json"
    if not os.path.exists(fp):
        return set()
    d = json.load(open(fp))
    return set((d.get("by_state") or {}).keys())


def gap_ordered():
    rows = []
    for r in csv.DictReader(open(f"{ROOT}/pipeline/results/profession_index/_coverage.csv")):
        p = r["profession"]
        if p in SKIP_PROFS or p in PUBLISHED or p in TRADES:
            continue
        gap = len(mapped_states(p) - pulled_states(p))
        if gap > 0:
            rows.append((gap, p))
    rows.sort(reverse=True)
    return [p for _, p in rows]


def commit(prof, n):
    subprocess.run(["git", "add", f"pipeline/results/text/{prof}"], cwd=ROOT)
    msg = (f"data: {prof} via CDP-Justia grind ({n} states)\n\n"
           "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>")
    r = subprocess.run(["git", "commit", "-m", msg], cwd=ROOT,
                       capture_output=True, text=True)
    log(f"  commit: {r.stdout.strip() or r.stderr.strip()}")


def main():
    profs = gap_ordered()
    log(f"=== GRIND START: {len(profs)} professions with a gap ===")
    log(f"order: {profs}")
    for prof in profs:
        missing = sorted(mapped_states(prof) - pulled_states(prof))
        if not missing:
            log(f"[{prof}] already complete — skip")
            continue
        log(f"[{prof}] pulling {len(missing)} states: {missing}")
        try:
            subprocess.run(
                [PY, "-m", "pipeline.ingest.pull_text",
                 "--profession", prof, "--states", ",".join(missing), "--force"],
                cwd=ROOT, check=False,
            )
        except Exception as e:  # noqa: BLE001
            log(f"[{prof}] ERROR: {e!r} — continuing")
            continue
        now_have = len(pulled_states(prof))
        log(f"[{prof}] done — now have {now_have} states")
        commit(prof, now_have)
    log("=== GRIND COMPLETE ===")


if __name__ == "__main__":
    main()
