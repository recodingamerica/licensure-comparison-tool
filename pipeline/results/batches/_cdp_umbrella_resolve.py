#!/usr/bin/env python
"""Resolve umbrella/general chapters (from the xref audit) to their Justia URLs
via the local hierarchy, producing a turnkey injection list: which (profession,
state) should gain which extra chapter URL so the missing general provisions get
pulled. Read-only.

  pipeline/.venv/bin/python pipeline/results/batches/_cdp_umbrella_resolve.py --profession construction_trades,electrician,plumbing,hvac --min-refs 8
"""
import argparse, glob, json, os, re
from collections import Counter

ROOT = "/Users/abigailhaddad/Documents/repos/utah"


def umbrella_refs(fp, min_refs):
    d = json.load(open(fp))
    secs = [s for s in d.get("sections") or [] if not s.get("error")]
    cites = [s.get("citation", "") for s in secs]
    pulled = {f"{m.group(1)}-{m.group(2)}" for c in cites if (m := re.match(r"(\d+)-(\d+)", c))}
    if not pulled:
        return {}
    text = " ".join((s.get("text") or "") for s in secs)
    refs = Counter(re.findall(r"\b(\d+-\d+)-\d+", text))
    return {c: n for c, n in refs.items() if c not in pulled and n >= min_refs}


def resolve_url(state, chapter):
    """chapter like '58-1' -> title 58 chapter 1; find its URL in the hierarchy."""
    title, ch = chapter.split("-", 1)
    fp = f"{ROOT}/pipeline/results/hierarchy/{state}.json"
    if not os.path.exists(fp):
        return None
    h = json.load(open(fp))
    found = []

    def walk(n):
        if isinstance(n, dict):
            u = n.get("url", "")
            # title-{title} may be followed by an intermediate segment (CO:
            # /title-12/division-of-professions-and-occupations/article-20/) and
            # the leaf may be article- OR chapter-.
            if f"title-{title}/" in u and re.search(rf"/(?:article|chapter)-{ch}(?:[-/]|$)", u):
                found.append(u)
            for v in n.values():
                walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)
    walk(h)
    return found[0] if found else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", default="*")
    ap.add_argument("--min-refs", type=int, default=8)
    args = ap.parse_args()
    profs = args.profession.split(",") if args.profession != "*" else ["*"]
    inject, unresolved = [], []
    for pg in profs:
        for fp in sorted(glob.glob(f"{ROOT}/pipeline/results/text/{pg}/*.json")):
            if fp.endswith("_summary.json"):
                continue
            prof = os.path.basename(os.path.dirname(fp))
            st = os.path.basename(fp)[:-5]
            for ch, n in sorted(umbrella_refs(fp, args.min_refs).items(), key=lambda x: -x[1]):
                url = resolve_url(st, ch)
                rec = {"profession": prof, "state": st, "chapter": ch, "refs": n, "url": url}
                (inject if url else unresolved).append(rec)
    print(f"RESOLVED umbrella chapters to inject ({len(inject)}):")
    for r in inject:
        print(f"  {r['profession']}/{r['state']} += {r['chapter']} ({r['refs']}x)  {r['url']}")
    print(f"\nUNRESOLVED (citation numbering != Justia slug — needs manual URL) ({len(unresolved)}):")
    for r in unresolved:
        print(f"  {r['profession']}/{r['state']} {r['chapter']} ({r['refs']}x)")
    op = f"{ROOT}/pipeline/results/batches/_umbrella_inject.json"
    json.dump({"inject": inject, "unresolved": unresolved}, open(op, "w"), indent=2)
    print(f"\nwrote {op}")


if __name__ == "__main__":
    main()
