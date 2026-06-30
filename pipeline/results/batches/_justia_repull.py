#!/usr/bin/env python
"""Targeted CDP-Justia re-pull of the raw pull-failures (not a full harvest).

Scope = exactly .scratch/jul1_prep/justia_repull.json ({prof:[states]}), the
134 Justia-source pairs that errored/came back empty. Resumable: skips any
(prof,state) that now has >=1 non-error section, so killing/restarting continues.
Commits per profession (commit-to-git durability). ONE process — shares the
single debug Chrome.

Run from repo root:
  JUSTIA_CDP_URL=http://localhost:9222 PULL_HOST_DELAY=7 \
    caffeinate -dimsu pipeline/.venv/bin/python pipeline/results/batches/_justia_repull.py
"""
import json, os, signal, subprocess, sys, datetime

ROOT = "/Users/abigailhaddad/Documents/repos/utah"
PY = f"{ROOT}/pipeline/.venv/bin/python"
WORKLIST = f"{ROOT}/.scratch/jul1_prep/justia_repull.json"
LOG = f"{ROOT}/pipeline/results/batches/_justia_repull.log"
SECTION_CAP = 400  # runaway guard

_CHILD = None


def _kill_child_and_exit(signum, _frame):
    if _CHILD and _CHILD.poll() is None:
        try:
            os.killpg(os.getpgid(_CHILD.pid), signal.SIGTERM)
        except Exception:
            pass
    sys.exit(143)


signal.signal(signal.SIGTERM, _kill_child_and_exit)
signal.signal(signal.SIGINT, _kill_child_and_exit)


def log(msg):
    line = f"{datetime.datetime.now().isoformat(timespec='seconds')}  {msg}"
    print(line, flush=True)
    with open(LOG, "a") as fh:
        fh.write(line + "\n")


def has_real_sections(prof, state):
    fp = f"{ROOT}/pipeline/results/text/{prof}/{state}.json"
    if not os.path.exists(fp):
        return False
    try:
        d = json.load(open(fp))
    except Exception:
        return False
    secs = d.get("sections") or []
    return any(not s.get("error") for s in secs)


def commit(prof, n):
    subprocess.run(["git", "add", f"pipeline/results/text/{prof}"], cwd=ROOT)
    subprocess.run(["git", "commit", "-q", "-m",
                    f"data: CDP-Justia re-pull {prof} ({n} states recovered)"], cwd=ROOT)


def main():
    global _CHILD
    worklist = json.load(open(WORKLIST))
    total = sum(len(v) for v in worklist.values())
    log(f"=== justia re-pull start: {total} pairs across {len(worklist)} profs ===")
    for prof in sorted(worklist):
        states = sorted(worklist[prof])
        todo = [s for s in states if not has_real_sections(prof, s)]
        if not todo:
            log(f"[{prof}] all {len(states)} already recovered — skip")
            continue
        log(f"[{prof}] pulling {len(todo)} states: {todo}")
        _CHILD = subprocess.Popen(
            [PY, "-m", "pipeline.ingest.pull_text",
             "--profession", prof, "--states", ",".join(todo),
             "--limit-sections", str(SECTION_CAP), "--force"],
            cwd=ROOT, preexec_fn=os.setsid,
        )
        _CHILD.wait()
        recovered = [s for s in todo if has_real_sections(prof, s)]
        log(f"[{prof}] recovered {len(recovered)}/{len(todo)}: {recovered}")
        if recovered:
            commit(prof, len(recovered))
    log("=== justia re-pull done ===")


if __name__ == "__main__":
    main()
