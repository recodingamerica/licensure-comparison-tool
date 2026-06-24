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
import csv, glob, json, os, signal, subprocess, sys, datetime

# Track the current child pull so killing the grind doesn't orphan it. An orphaned
# pull_text keeps hammering the shared Chrome and collides with any later pull
# (garbled 1-section "partials"). On SIGTERM/SIGINT, kill the child's whole
# process group, then exit.
_CHILD = None


def _kill_child_and_exit(signum, _frame):
    global _CHILD
    if _CHILD and _CHILD.poll() is None:
        try:
            os.killpg(os.getpgid(_CHILD.pid), signal.SIGTERM)
        except Exception:  # noqa: BLE001
            pass
    sys.exit(143)


signal.signal(signal.SIGTERM, _kill_child_and_exit)
signal.signal(signal.SIGINT, _kill_child_and_exit)

ROOT = "/Users/abigailhaddad/Documents/repos/utah"
PY = f"{ROOT}/pipeline/.venv/bin/python"
LOG = f"{ROOT}/pipeline/results/batches/_cdp_grind.log"
# Professions already complete or in-progress by other means — skip entirely.
SKIP_PROFS = {"_families"}
# Only the 7 published professions are complete (50/50); skip them. Everything
# else — including the 4 trades' stragglers (hvac etc.) — is fair game. The
# section cap protects against flat-title trade runaways (OK/LA/NJ).
TRADES = set()
PUBLISHED = {"dentistry", "dietetics", "medicine", "nursing", "optometry",
             "podiatry", "public_accountancy"}
# Per-state section cap: bounds runaway title-level / umbrella over-matches so one
# bad mapping can't burn hours of the CDP window. Generous for any single niche
# profession; states that hit it get logged for manual section-range scoping.
SECTION_CAP = 250


def log(msg):
    line = f"{datetime.datetime.now().isoformat(timespec='seconds')} {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def pulled_states(prof):
    """States already pulled WITH content (>=1 ok section). A corpus that came
    back all-error/empty is NOT counted as done, so the resumable grind retries
    it next run instead of silently treating a failed profession as complete — a
    permanent gap that would otherwise only surface via a blind re-scrape."""
    out = set()
    for fp in glob.glob(f"{ROOT}/pipeline/results/text/{prof}/*.json"):
        st = os.path.basename(fp)[:-5]
        if st == "_summary":
            continue
        try:
            d = json.load(open(fp))
        except Exception:  # noqa: BLE001
            continue
        if any(not s.get("error") for s in (d.get("sections") or [])):
            out.add(st)
    return out


def mapped_states(prof):
    """States with a REAL (non-empty) match. by_state lists all 50 states even
    when `matched` is empty — pulling those is a wasted no-op and inflates the
    gap (which broke ordering), so filter to states with actual chapter rows."""
    fp = f"{ROOT}/pipeline/results/profession_index/{prof}.json"
    if not os.path.exists(fp):
        return set()
    bs = json.load(open(fp)).get("by_state") or {}
    return {s for s, v in bs.items() if v.get("matched")}


# User needs the trades this week — pull their remaining states FIRST (hvac leads;
# it's the biggest trade gap), then the rest of the harvest by gap descending.
PRIORITY = ["hvac", "construction_trades", "electrician", "plumbing"]


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
    have_gap = {p for _, p in rows}
    pri = [p for p in PRIORITY if p in have_gap]
    rest = [p for _, p in rows if p not in PRIORITY]
    return pri + rest


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
            global _CHILD
            # start_new_session=True puts the child in its own process group so
            # the signal handler can kill the whole group (not just the wrapper).
            _CHILD = subprocess.Popen(
                [PY, "-m", "pipeline.ingest.pull_text",
                 "--profession", prof, "--states", ",".join(missing),
                 "--limit-sections", str(SECTION_CAP), "--force"],
                cwd=ROOT, start_new_session=True,
            )
            _CHILD.wait()
            _CHILD = None
        except Exception as e:  # noqa: BLE001
            log(f"[{prof}] ERROR: {e!r} — continuing")
            continue
        # Flag any state that hit the cap — likely a title-level/umbrella over-match
        # needing manual section-range scoping, not a clean profession chapter.
        for s in missing:
            fp = f"{ROOT}/pipeline/results/text/{prof}/{s}.json"
            if os.path.exists(fp):
                try:
                    n = len(json.load(open(fp)).get("sections") or [])
                except Exception:  # noqa: BLE001
                    continue
                if n >= SECTION_CAP:
                    log(f"[{prof}/{s}] HIT CAP ({n}>={SECTION_CAP}) — review for over-match / manual scope")
        now_have = len(pulled_states(prof))
        log(f"[{prof}] done — now have {now_have} states")
        commit(prof, now_have)
    log("=== GRIND COMPLETE ===")


if __name__ == "__main__":
    main()
