"""Reuse-existing-corpus step. Many gap cells' located chapters were ALREADY fetched
for another profession in the same state (osteopathic_medicine -> the medical-practice
act we have under 'medicine'; acupuncture -> a big medical chapter). Instead of re-fetching
via CDP, copy the sections whose URL falls under the located chapter from whatever existing
corpus already holds them. LLM-free, instant. Writes text/<prof>/<state>.json for reused
cells and removes them from the pull worklist."""
import json, os, glob, re
os.chdir("/Users/abigailhaddad/Documents/repos/utah")
SP = "/private/tmp/claude-501/-Users-abigailhaddad-Documents-repos-utah/a4c2a38a-3f03-4281-9391-7b1770858434/scratchpad"

def sections_of(f):
    try: d = json.load(open(f))
    except Exception: return []
    return d if isinstance(d, list) else d.get("sections", [])

# index existing sections by state: {state: [(url, section)]}
by_state = {}
for f in glob.glob("pipeline/results/text/*/*.json"):
    parts = f.split("/")
    prof, st = parts[-2], parts[-1][:-5]
    if st.startswith("_"): continue
    for sec in sections_of(f):
        u = sec.get("url", "")
        if u:
            by_state.setdefault(st, []).append((u, sec, prof))

res = json.load(open(f"{SP}/locator_results.json"))
reused = {}   # prof -> [states]
still_pull = {}
reuse_count = sec_total = 0

for p in res:
    for st, r in res[p].items():
        url = r.get("url")
        if not url or url == "null" or r.get("via") == "null_recovery":
            continue
        if os.path.exists(f"pipeline/results/text/{p}/{st}.json"):
            continue  # already have it
        base = url.rstrip("/")
        # collect sections under this chapter from OTHER professions' corpora
        pool = by_state.get(st, [])
        matched = {}
        for u, sec, src in pool:
            if src == p:  # same profession (won't happen, no corpus) — skip
                continue
            if u.rstrip("/") == base or u.startswith(base + "/"):
                matched.setdefault(u, sec)  # dedupe by url
        if matched:
            secs = list(matched.values())
            os.makedirs(f"pipeline/results/text/{p}", exist_ok=True)
            json.dump({"sections": secs, "source": "reused_from_existing_corpus",
                       "reused_chapter": url},
                      open(f"pipeline/results/text/{p}/{st}.json", "w"), indent=1)
            reused.setdefault(p, []).append(st)
            reuse_count += 1; sec_total += len(secs)
        else:
            still_pull.setdefault(p, []).append(st)

json.dump(still_pull, open(f"{SP}/gap_pull_worklist.json", "w"), indent=1)
json.dump(reused, open(f"{SP}/gap_reused.json", "w"), indent=1)
print(f"REUSED {reuse_count} cells ({sec_total} sections) — no fetch needed")
print(f"STILL TO PULL: {sum(len(v) for v in still_pull.values())} cells across {len(still_pull)} professions")
