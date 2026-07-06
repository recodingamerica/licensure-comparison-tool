"""Null-recovery pass. The main locator returns null when an occupation isn't *licensed*
in a state. But some states regulate it under an EXEMPTION / CERTIFICATION / REGISTRATION
regime with a real chapter (e.g. UT optician: Title 58 Ch 16a exempts opticians but the
chapter addresses them). Our completeness goal wants that chapter. Re-run ONLY the nulls
with a looser prompt; keep null only if there's genuinely no chapter. Safe: truly-absent
states (CO/IL optician) still return null — no chapter to find."""
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
RESULTS = f"{SP}/locator_results.json"

STATE_SLUG = {"AL":"alabama","AK":"alaska","AZ":"arizona","AR":"arkansas","CA":"california",
"CO":"colorado","CT":"connecticut","DE":"delaware","FL":"florida","GA":"georgia","HI":"hawaii",
"ID":"idaho","IL":"illinois","IN":"indiana","IA":"iowa","KS":"kansas","KY":"kentucky","LA":"louisiana",
"ME":"maine","MD":"maryland","MA":"massachusetts","MI":"michigan","MN":"minnesota","MS":"mississippi",
"MO":"missouri","MT":"montana","NE":"nebraska","NV":"nevada","NH":"new-hampshire","NJ":"new-jersey",
"NM":"new-mexico","NY":"new-york","NC":"north-carolina","ND":"north-dakota","OH":"ohio","OK":"oklahoma",
"OR":"oregon","PA":"pennsylvania","RI":"rhode-island","SC":"south-carolina","SD":"south-dakota",
"TN":"tennessee","TX":"texas","UT":"utah","VT":"vermont","VA":"virginia","WA":"washington",
"WV":"west-virginia","WI":"wisconsin","WY":"wyoming"}

SYS = ("You locate any statute chapter that ADDRESSES an occupation on Justia — not only "
"licensure. Given an occupation and a U.S. state, search law.justia.com and return the SINGLE "
"Justia code URL for the CHAPTER/ARTICLE/PART (a container listing sections, current year-less "
"path, NOT a single section) that governs, certifies, registers, OR expressly EXEMPTS this "
"occupation in that state. Return the chapter even if the occupation is exempt or only "
"nationally-certified there — the exemption/certification IS the regulatory fact. Return null "
"ONLY if the state's code truly contains no chapter addressing this occupation at all. End your "
'reply with exactly one line: RESULT: {"url": "<url or null>", "label": "<label>", "confidence": "high|med|low"}')

lock = threading.Lock()

def norm(url):
    if not url or url=="null" or "law.justia.com/codes/" not in url: return url
    head,_,path=url.partition("/codes/"); return head+"/codes/"+path.replace(".","-")

def locate(prof, st):
    disp = profs[prof].get("display") or prof
    pats = ", ".join((profs[prof].get("patterns") or [])[:4])
    q = (f"Occupation: {disp} (aka: {pats}). State: {st} ({STATE_SLUG[st]}). "
         f"Find ANY chapter addressing it (license, certification, registration, or exemption) "
         f"on law.justia.com/codes/{STATE_SLUG[st]}/ .")
    for attempt in range(2):
        try:
            r = client.messages.create(model=MODEL, max_tokens=1500,
                tools=[{"type":"web_search_20250305","name":"web_search","max_uses":4,
                        "allowed_domains":["law.justia.com"]}],
                system=SYS, messages=[{"role":"user","content":q}])
            txt="".join(b.text for b in r.content if getattr(b,"type","")=="text")
            m=re.search(r'RESULT:\s*(\{.*\})', txt, re.S)
            if m: return json.loads(m.group(1))
            return {"url":None,"confidence":"parse_fail"}
        except Exception as e:
            if attempt==1: return {"url":None,"confidence":f"err:{type(e).__name__}"}

def work(item, results):
    prof, st = item
    res = locate(prof, st)
    url = norm(res.get("url")) if res.get("url") else None
    with lock:
        if url and url != "null":  # recovered — overwrite the null
            results[prof][st] = {"url":url, "label":res.get("label",""),
                                 "confidence":res.get("confidence",""), "via":"null_recovery"}
            return prof, st, True
    return prof, st, False

def main():
    results = json.load(open(RESULTS))
    nulls = [(p, st) for p in results for st, r in results[p].items()
             if r.get("url") in (None, "null") and r.get("via") != "null_recovery"]
    print(f"nulls to recheck: {len(nulls)}", flush=True)
    recovered = 0; n = 0
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = [ex.submit(work, it, results) for it in nulls]
        for f in as_completed(futs):
            p, st, rec = f.result(); n += 1; recovered += rec
            if n % 25 == 0:
                json.dump(results, open(RESULTS,"w"), indent=1)
                print(f"  {n}/{len(nulls)} … recovered {recovered}", flush=True)
    json.dump(results, open(RESULTS,"w"), indent=1)
    still_null = sum(1 for p in results for st,r in results[p].items() if r.get("url") in (None,"null"))
    print(f"\nDONE. recovered {recovered} chapters from nulls; {still_null} remain null (genuine absence).", flush=True)

if __name__ == "__main__":
    main()
