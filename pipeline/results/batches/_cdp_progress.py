#!/usr/bin/env python
"""Grind progress readout — % of the harvest done. Read-only, run anytime:
  pipeline/.venv/bin/python pipeline/results/batches/_cdp_progress.py
"""
import glob, json, os, sys, importlib.util

ROOT = "/Users/abigailhaddad/Documents/repos/utah"
spec = importlib.util.spec_from_file_location("g", f"{ROOT}/pipeline/results/batches/_cdp_grind.py")
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def grind_profs():
    out = []
    for fp in glob.glob(f"{ROOT}/pipeline/results/profession_index/*.json"):
        p = os.path.basename(fp)[:-5]
        if p.startswith("_") or p in g.PUBLISHED or p in g.SKIP_PROFS:
            continue
        out.append(p)
    return out


def main():
    profs = grind_profs()
    tot_mapped = tot_pulled = 0
    done_profs = []
    for p in profs:
        mapped = g.mapped_states(p)
        pulled = g.pulled_states(p) & mapped
        tot_mapped += len(mapped)
        tot_pulled += len(pulled)
        if mapped and pulled >= mapped:
            done_profs.append(p)
    pct = 100 * tot_pulled / tot_mapped if tot_mapped else 0
    cur = ""
    try:
        log = open(f"{ROOT}/pipeline/results/batches/_cdp_grind.log").read().splitlines()
        for ln in reversed(log):
            if "] pulling" in ln:
                cur = ln.split("[", 1)[1].split("]", 1)[0]
                break
    except Exception:
        pass
    bar = int(pct / 2)
    print(f"\n  HARVEST: [{'#'*bar}{'.'*(50-bar)}] {pct:.1f}%")
    print(f"  states pulled-with-content: {tot_pulled} / {tot_mapped} real targets")
    print(f"  professions complete: {len(done_profs)} / {len(profs)}")
    print(f"  currently pulling: {cur or '?'}")
    print(f"\n  (published 7 professions at 50/50 are excluded — already done)\n")


if __name__ == "__main__":
    main()
