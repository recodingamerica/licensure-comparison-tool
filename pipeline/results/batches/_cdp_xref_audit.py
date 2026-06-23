#!/usr/bin/env python
"""Cross-reference audit — find UMBRELLA/general chapters a corpus depends on but
that we never pulled. A profession's specific chapter (e.g. UT 58-55) routinely
points to a shared general-provisions chapter (UT 58-1: discipline, renewal,
unprofessional conduct for ALL professions). If we only pulled the specific
chapter, those provisions are silently MISSING — re-scrape-class incompleteness
a re-clean can't fix.

Per (profession, state): infers the chapter(s) self-covered (from section
citations in Title-Chapter[-Section] numeric form), counts text references to
OTHER chapters, and flags external chapters referenced >= MIN_REFS that we didn't
pull. Heavily-referenced "-1"/low-number chapters are the usual umbrella suspects.

Read-only. Usage:
  pipeline/.venv/bin/python pipeline/results/batches/_cdp_xref_audit.py [--profession P] [--min-refs N]
NOTE: numeric-citation heuristic — covers states with Title-Chapter-Section cites
(UT/CO/IN/SC/GA/AL/AR/...). States with prose cites (KRS, RS, §) are not analyzed.
"""
import argparse, glob, json, os, re
from collections import Counter

ROOT = "/Users/abigailhaddad/Documents/repos/utah"


def analyze(fp):
    d = json.load(open(fp))
    secs = [s for s in d.get("sections") or [] if not s.get("error")]
    if not secs:
        return None
    cites = [s.get("citation", "") for s in secs]
    pulled = {f"{m.group(1)}-{m.group(2)}" for c in cites
              if (m := re.match(r"(\d+)-(\d+)", c))}
    if not pulled:
        return None
    text = " ".join((s.get("text") or "") for s in secs)
    refs = Counter(re.findall(r"\b(\d+-\d+)-\d+", text))
    return pulled, {c: n for c, n in refs.items() if c not in pulled}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", default="*")
    ap.add_argument("--min-refs", type=int, default=5)
    args = ap.parse_args()
    rows = []
    for fp in sorted(glob.glob(f"{ROOT}/pipeline/results/text/{args.profession}/*.json")):
        if fp.endswith("_summary.json"):
            continue
        prof = os.path.basename(os.path.dirname(fp))
        st = os.path.basename(fp)[:-5]
        res = analyze(fp)
        if not res:
            continue
        pulled, ext = res
        umb = {c: n for c, n in ext.items() if n >= args.min_refs}
        if umb:
            rows.append((prof, st, sorted(pulled),
                         sorted(umb.items(), key=lambda x: -x[1])))
    print(f"{len(rows)} (profession,state) corpora reference an UNPULLED chapter "
          f">= {args.min_refs}x (umbrella candidates):\n")
    # aggregate: which umbrella chapters recur across professions in a state?
    by_state = {}
    for prof, st, pulled, umb in rows:
        print(f"  {prof}/{st}: pulled {pulled} -> {umb}")
        for ch, n in umb:
            by_state.setdefault(st, Counter())[ch] += 1
    print("\n  recurring umbrella chapters (referenced by >=2 professions in a state):")
    for st, c in sorted(by_state.items()):
        rec = {ch: k for ch, k in c.items() if k >= 2}
        if rec:
            print(f"    {st}: {rec}")
    out = [{"profession": p, "state": s, "pulled": pl, "umbrella_refs": dict(u)}
           for p, s, pl, u in rows]
    op = f"{ROOT}/pipeline/results/batches/_umbrella_candidates.json"
    json.dump(out, open(op, "w"), indent=2)
    print(f"\nwrote {op}")


if __name__ == "__main__":
    main()
