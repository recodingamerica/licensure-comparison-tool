"""Small LLM pass: classify recurring unmapped occupations-title chapters as
'distinct licensed occupation' vs 'not an occupation' (topic/entity/product/etc).
Haiku, batched. Output: the clean list of occupations we DON'T yet track."""
import sys, json, re, glob, collections
sys.path.insert(0, "/Users/abigailhaddad/Documents/repos/utah")
import os; os.chdir("/Users/abigailhaddad/Documents/repos/utah")
from urllib.parse import urlparse
from pipeline._env import load_env
from pipeline.config.loaders import load_professions
from pipeline.discover.match_profession import label_matches
import anthropic

load_env()
HAIKU = "claude-haiku-4-5-20251001"
profs = load_professions()
ours = sorted(k for k in profs if not k.startswith("_"))
pats = [((v or {}).get("patterns") or [], (v or {}).get("excludes") or []) for k, v in profs.items() if not k.startswith("_")]

def title_of(url):
    p = urlparse(url).path if url.startswith("http") else url
    m = re.match(r'(/codes/[^/]+/(?:title|volume|part)-[^/]+/)', p)
    return m.group(1) if m else None

occ_titles = set()
for f in glob.glob("pipeline/results/profession_index/*.json"):
    if f.split("/")[-1].startswith("_"): continue
    for st, b in json.load(open(f)).get("by_state", {}).items():
        for n in b.get("matched", []):
            t = title_of(n.get("url", ""))
            if t: occ_titles.add((st, t))

cand = collections.Counter()
for f in glob.glob("pipeline/results/hierarchy/*.json"):
    st = f.split("/")[-1][:-5]
    try: chs = json.load(open(f)).get("chapters", [])
    except Exception: continue
    for c in chs:
        if c.get("parent_chapter_url") or c.get("is_section"): continue
        t = title_of(c.get("url", ""))
        if not t or (st, t) not in occ_titles: continue
        lab = c.get("label", "").strip()
        core = re.sub(r'^\s*(chapter|article|part|subchapter)\s+[\dA-Za-z.\-]+\s*[-–.:]*\s*', '', lab, flags=re.I).strip().strip(".")
        if len(core) < 4 or re.search(r'general provision|^definition|penalt|miscellaneous|former provision|repeal|reserved', core, re.I): continue
        if any(label_matches(lab, p, e) for p, e in pats): continue
        cand[core.lower()] += 1

recurring = sorted([c for c, n in cand.items() if n >= 2], key=lambda x: -cand[x])
print(f"recurring candidates (>=3 states): {len(recurring)}", flush=True)

client = anthropic.Anthropic()
SYS = ("You classify U.S. state statute chapter titles. For each title, decide if it names a "
       "DISTINCT LICENSED OCCUPATION/PROFESSION — a kind of worker who must hold a state license, "
       "certification, or registration to practice (e.g. 'Opticians', 'Bail Bond Agents', 'Midwifery'). "
       "Return null for anything that is NOT a licensed-worker type: general topics, statutes/acts, "
       "business/entity types (credit unions, HMOs), insurance products, procedures, government bodies, "
       "boards, funds. Reply ONLY with a JSON array, one object per input: "
       '{"i": <index>, "occ": "<canonical occupation name>" | null}.')
found = {}
B = 50
for i in range(0, len(recurring), B):
    batch = recurring[i:i+B]
    lines = "\n".join(f"{j}. {t}" for j, t in enumerate(batch))
    try:
        r = client.messages.create(model=HAIKU, max_tokens=4000,
            system=SYS + f"\nWe ALREADY track these, don't return them: {', '.join(ours)}.",
            messages=[{"role": "user", "content": f"Classify these {len(batch)} titles:\n{lines}"}])
        txt = r.content[0].text
        arr = json.loads(txt[txt.find("["):txt.rfind("]")+1])
        for o in arr:
            if o.get("occ"):
                found.setdefault(o["occ"].strip().lower(), 0)
                found[o["occ"].strip().lower()] += cand.get(batch[o["i"]], 1)
        print(f"  batch {i//B+1}/{(len(recurring)+B-1)//B}: +{sum(1 for o in arr if o.get('occ'))} occ", flush=True)
    except Exception as e:
        print(f"  batch {i//B+1} error: {type(e).__name__}: {e}", flush=True)

SP = "/private/tmp/claude-501/-Users-abigailhaddad-Documents-repos-utah/a4c2a38a-3f03-4281-9391-7b1770858434/scratchpad"
occs = sorted(found.items(), key=lambda x: -x[1])
json.dump(occs, open(f"{SP}/missing_occupations.json", "w"), indent=1)
print(f"\n=== {len(occs)} DISTINCT MISSING OCCUPATIONS (not in our {len(ours)}) ===")
for name, weight in occs:
    print(f"  {weight:3d}  {name}")
