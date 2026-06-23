#!/usr/bin/env python
"""Post-pull corpus health audit — find states that need a RE-PULL (raw text
missing/wrong; a re-clean can't fix it). Read-only, safe to run anytime.

Flags per (profession, state):
  - error_sections: sections with an `error` (fetch failures + the in-pull
    empty/block-page guard).
  - silent_bad: sections marked ok but whose text is empty/thin or a block page
    (bad_section_text). Catches corpora pulled BEFORE the in-pull guard landed
    (e.g. the grind's first profession) where corruption wasn't flagged.
  - cap_hit: section count == SECTION_CAP (250) — likely a title-level/umbrella
    over-match that was truncated and needs manual section-range scoping.

Usage:
  pipeline/.venv/bin/python pipeline/results/batches/_cdp_audit.py [--profession P]
"""
import argparse, glob, json, os, sys

ROOT = "/Users/abigailhaddad/Documents/repos/utah"
sys.path.insert(0, ROOT)
from pipeline.ingest.pull_text import bad_section_text  # noqa: E402
CAP = 250


def audit_corpus(fp):
    d = json.load(open(fp))
    secs = d.get("sections") or []
    err = [s for s in secs if s.get("error")]
    ok = [s for s in secs if not s.get("error")]
    silent_bad = [s for s in ok if bad_section_text(s.get("text") or "")]
    return {
        "total": len(secs), "ok": len(ok), "errors": len(err),
        # Truncation-at-cap is EXACTLY the cap (grind pulls). Published corpora
        # were pulled without the cap, so 896 sections is legit, not truncated.
        # THIN: very few ok sections => likely a spurious match (wrong chapter),
        # a flat-title section-level pull (incomplete), or a repealed chapter.
        # The error/empty/cap checks miss these (the text is "ok", just sparse).
        "silent_bad": len(silent_bad), "cap_hit": len(secs) == CAP,
        "thin": len(ok) <= 3,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", default="")
    args = ap.parse_args()
    pat = f"{ROOT}/pipeline/results/text/{args.profession or '*'}/*.json"
    flagged = []
    n = 0
    for fp in sorted(glob.glob(pat)):
        if fp.endswith("_summary.json"):
            continue
        prof = os.path.basename(os.path.dirname(fp))
        st = os.path.basename(fp)[:-5]
        n += 1
        h = audit_corpus(fp)
        reasons = []
        if h["ok"] == 0:
            reasons.append("EMPTY corpus")
        if h["errors"]:
            reasons.append(f"{h['errors']} error-sec")
        if h["silent_bad"]:
            reasons.append(f"{h['silent_bad']} silent-bad")
        if h["cap_hit"]:
            reasons.append(f"CAP-HIT ({h['total']})")
        if h["thin"] and h["ok"] > 0:
            reasons.append(f"THIN ({h['ok']} sec — likely incomplete/spurious)")
        if reasons:
            flagged.append((prof, st, h, reasons))
    print(f"audited {n} corpora; {len(flagged)} need attention (re-pull candidates):\n")
    for prof, st, h, reasons in flagged:
        print(f"  {prof}/{st}: {h['ok']}/{h['total']} ok — {', '.join(reasons)}")
    # machine-readable list for a targeted re-pull pass
    out = [{"profession": p, "state": s, **h, "reasons": r} for p, s, h, r in flagged]
    op = f"{ROOT}/pipeline/results/batches/_repull_candidates.json"
    json.dump(out, open(op, "w"), indent=2)
    print(f"\nwrote {op}")


if __name__ == "__main__":
    main()
