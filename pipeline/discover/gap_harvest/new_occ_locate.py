import sys, os, json
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0,"/Users/abigailhaddad/Documents/repos/utah"); os.chdir("/Users/abigailhaddad/Documents/repos/utah")
sys.path.insert(0,"/private/tmp/claude-501/-Users-abigailhaddad-Documents-repos-utah/a4c2a38a-3f03-4281-9391-7b1770858434/scratchpad")
from locator_full import locate, norm, valid, STATE_SLUG
SP="/private/tmp/claude-501/-Users-abigailhaddad-Documents-repos-utah/a4c2a38a-3f03-4281-9391-7b1770858434/scratchpad"
NEW=['pest_control','outfitter_guide','asbestos_abatement','meat_inspector','boxer','hawker_peddler','septage_pumper','managing_general_agent']
STATES=["CA","TX","FL","NY","CO","MT","ME","GA","WA","OH","AK","WY"]
out={}
def work(it):
    p,st=it; r=locate(p,st)
    if r.get("url"): r["url"]=norm(r["url"])
    return p,st,r
with ThreadPoolExecutor(max_workers=10) as ex:
    for f in as_completed([ex.submit(work,(p,st)) for p in NEW for st in STATES]):
        p,st,r=f.result(); out.setdefault(p,{})[st]=r
json.dump(out,open(f"{SP}/new_occ_located.json","w"),indent=1)
for p in NEW:
    got=sum(1 for st in out[p] if out[p][st].get("url") and out[p][st]["url"]!="null")
    print(f"  {p:26s}: {got}/{len(STATES)} located")
