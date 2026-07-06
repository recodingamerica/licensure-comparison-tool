"""Production search-driven locator. For every Tier-3 likely-gap (profession, state),
use the Anthropic web_search tool (scoped to law.justia.com) to find the Justia code
chapter/article URL that primarily regulates that occupation's licensing there — or null
if genuinely unlicensed. Concurrent, checkpointed, resumable. Output feeds verify_urls
gate → override targets → pull."""
import sys, os, json, re, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, "/Users/abigailhaddad/Documents/repos/utah")
os.chdir("/Users/abigailhaddad/Documents/repos/utah")
from pipeline._env import load_env
from pipeline.config.loaders import load_professions
import anthropic

load_env()
MODEL = "claude-haiku-4-5-20251001"
client = anthropic.Anthropic()
profs = load_professions()
SP = "/private/tmp/claude-501/-Users-abigailhaddad-Documents-repos-utah/a4c2a38a-3f03-4281-9391-7b1770858434/scratchpad"
OUT = f"{SP}/locator_results.json"

STATE_SLUG = {"AL":"alabama","AK":"alaska","AZ":"arizona","AR":"arkansas","CA":"california",
"CO":"colorado","CT":"connecticut","DE":"delaware","FL":"florida","GA":"georgia","HI":"hawaii",
"ID":"idaho","IL":"illinois","IN":"indiana","IA":"iowa","KS":"kansas","KY":"kentucky","LA":"louisiana",
"ME":"maine","MD":"maryland","MA":"massachusetts","MI":"michigan","MN":"minnesota","MS":"mississippi",
"MO":"missouri","MT":"montana","NE":"nebraska","NV":"nevada","NH":"new-hampshire","NJ":"new-jersey",
"NM":"new-mexico","NY":"new-york","NC":"north-carolina","ND":"north-dakota","OH":"ohio","OK":"oklahoma",
"OR":"oregon","PA":"pennsylvania","RI":"rhode-island","SC":"south-carolina","SD":"south-dakota",
"TN":"tennessee","TX":"texas","UT":"utah","VT":"vermont","VA":"virginia","WA":"washington",
"WV":"west-virginia","WI":"wisconsin","WY":"wyoming"}

SYS = ("You locate the primary licensing statute for an occupation on Justia. Given an "
"occupation and a U.S. state, search law.justia.com and return the SINGLE Justia code URL "
"for the CHAPTER, ARTICLE, or PART (a container that lists sections — NOT a single section, "
"NOT a year-versioned page) that primarily governs that occupation's LICENSE/CERTIFICATION/"
"REGISTRATION to practice in that state. Prefer the current (year-less) code path like "
"https://law.justia.com/codes/<state>/<title>/<chapter>/ . If the state genuinely does not "
"license this occupation at the state level, return null. End your reply with exactly one "
'line: RESULT: {"url": "<url or null>", "label": "<chapter label>", "confidence": "high|med|low"}')

lock = threading.Lock()
results = {}
if os.path.exists(OUT):
    try: results = json.load(open(OUT))
    except Exception: results = {}

def done(p, st): return p in results and st in results[p]

def locate(prof, st):
    disp = profs[prof].get("display") or prof
    pats = ", ".join((profs[prof].get("patterns") or [])[:4])
    q = (f"Occupation: {disp} (aka: {pats}). State: {st} ({STATE_SLUG[st]}). "
         f"Find its primary licensing chapter on law.justia.com/codes/{STATE_SLUG[st]}/ .")
    for attempt in range(2):
        try:
            r = client.messages.create(model=MODEL, max_tokens=1500,
                tools=[{"type":"web_search_20250305","name":"web_search","max_uses":4,
                        "allowed_domains":["law.justia.com"]}],
                system=SYS, messages=[{"role":"user","content":q}])
            txt="".join(b.text for b in r.content if getattr(b,"type","")=="text")
            m=re.search(r'RESULT:\s*(\{.*\})', txt, re.S)
            if m: return json.loads(m.group(1))
            return {"url":None,"label":"","confidence":"parse_fail"}
        except Exception as e:
            if attempt==1: return {"url":None,"label":"","confidence":f"err:{type(e).__name__}"}
    return {"url":None,"label":"","confidence":"err"}

def norm(url):
    """Justia code paths hyphenate title/chapter numbers — the model sometimes emits a
    dot (title-32.1 → title-32-1). Dots never appear in valid Justia code slugs, so
    replace them in the path portion only."""
    if not url or url=="null" or "law.justia.com/codes/" not in url: return url
    head, _, path = url.partition("/codes/")
    return head + "/codes/" + path.replace(".", "-")

def valid(url, st):
    return bool(url) and url!="null" and "law.justia.com" in url and f"/codes/{STATE_SLUG.get(st,'')}/" in url

def work(item):
    prof, st = item
    res = locate(prof, st)
    if res.get("url"): res["url"] = norm(res["url"])
    with lock:
        results.setdefault(prof, {})[st] = res
        # checkpoint every write is cheap enough; flush periodically
        if sum(len(v) for v in results.values()) % 20 == 0:
            json.dump(results, open(OUT,"w"), indent=0)
    return prof, st, res

def main():
    gap = json.load(open(f"{SP}/tier3_absence.json"))["likely_gap"]
    todo = [(p, st) for p in gap for st in gap[p] if not done(p, st)]
    limit = int(os.environ.get("LOCATOR_LIMIT", "0"))
    already = total = sum(len(v) for v in gap.values())
    already = total - len(todo)
    if limit:  # cap total completed at `limit`
        todo = todo[:max(0, limit - already)]
    print(f"gap cells: {total}; already done: {already}; to do now: {len(todo)}", flush=True)
    n=0
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs=[ex.submit(work, it) for it in todo]
        for f in as_completed(futs):
            p, st, res = f.result(); n+=1
            if n % 25 == 0:
                json.dump(results, open(OUT,"w"), indent=0)
                print(f"  {n}/{len(todo)} …", flush=True)
    json.dump(results, open(OUT,"w"), indent=1)
    # summary
    ok=null=bad=0
    for p in results:
        for st,res in results[p].items():
            u=res.get("url")
            if u in (None,"null"): null+=1
            elif valid(u,st): ok+=1
            else: bad+=1
    print(f"\nDONE. valid-url: {ok}  null/absent: {null}  bad/parse/err: {bad}  → {OUT}", flush=True)

if __name__=="__main__":
    main()
