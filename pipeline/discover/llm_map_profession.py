"""LLM-based occupation→chapter mapper (Pass 1).

Replaces brittle keyword matching (match_profession) with judgment: for each
state, hand the LLM that state's chapter list (from results/hierarchy/) plus the
profession definition and ask which chapter(s) hold THIS profession's licensing —
including when the label doesn't contain the profession keyword (umbrella
"Occupational Code"/"Contractors"/"Construction Industries" chapters, or a
classification under one contractor board). When the licensing is likely nested
inside a broad container whose sub-articles aren't in the top-level hierarchy, the
LLM flags the container URL to expand (Pass 2, separate).

Output is a CANDIDATE file (results/profession_index/_llm_candidates/<prof>.json)
for review — it does NOT overwrite profession_index (which carries manual
additions). Apply selectively.

Run:
  pipeline/.venv/bin/python -m pipeline.discover.llm_map_profession --profession electrician
  pipeline/.venv/bin/python -m pipeline.discover.llm_map_profession --profession electrician --states NM,CA,OR,WI  # subset
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from pipeline._env import load_env  # noqa: E402
load_env()

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _llm import call_structured, usage_summary  # noqa: E402
from paths import RESULTS_DIR, CONFIG_DIR  # noqa: E402

HIER_DIR = RESULTS_DIR / "hierarchy"
OUT_DIR = RESULTS_DIR / "profession_index" / "_llm_candidates"
MODEL = "claude-haiku-4-5-20251001"  # cheap; this is a wide first-pass screen

ALL_STATES = ("AK AL AR AZ CA CO CT DE FL GA HI IA ID IL IN KS KY LA MA MD ME MI "
              "MN MO MS MT NC ND NE NH NJ NM NV NY OH OK OR PA RI SC SD TN TX UT "
              "VA VT WA WI WV WY").split()

# Drop obvious non-licensing noise from the chapter list to keep the prompt tight.
_NOISE = re.compile(r"\brepealed\b", re.I)
# A leaf SECTION url-segment (vs a chapter/article/title) — flat-title states list
# thousands of these; the mapper wants structure granularity, not every section.
_LEAF_SECTION = re.compile(r"^(section-|rs-\d|statute-\d|s-\d|\d+[-.]\d+[-.]\d)", re.I)


class StateMapping(BaseModel):
    licensed: bool = Field(description="Is this profession licensed/regulated at the STATE level in this state (vs. local-only or not regulated)?")
    chapter_urls: list[str] = Field(default_factory=list, description="URLs of the chapter(s)/article(s) whose text contains this profession's licensing law. Empty if not licensed or if only an umbrella container can be identified.")
    umbrella_container_url: str | None = Field(default=None, description="If the licensing is almost certainly nested inside a broad container chapter (e.g. an 'Occupational Code', 'Contractors', or 'Construction Industries' chapter) whose sub-articles are NOT shown in the list, give that container's URL to expand later. Else null.")
    basis: str = Field(description="One sentence: which chapter label(s) and why — the evidence used. Not a confidence score.")


def load_profession(prof: str) -> dict:
    d = yaml.safe_load((CONFIG_DIR / "professions.yaml").read_text())
    if prof not in d:
        sys.exit(f"profession {prof!r} not in professions.yaml")
    return d[prof]


def state_chapter_list(state: str) -> list[dict]:
    fp = HIER_DIR / f"{state}.json"
    if not fp.exists():
        return []
    chapters = json.loads(fp.read_text()).get("chapters", []) or []
    out = []
    for c in chapters:
        lab = (c.get("label") or "").strip()
        if not lab or _NOISE.search(lab):
            continue
        # Drop individual LEAF SECTIONS — the mapper wants chapter/article/title
        # granularity, not 1,500 flat sections (which blow the 200k context for
        # flat-title states like AZ title-32). Section-level slugs: section-…,
        # rs-NN-…, a trailing NN-NN-NN. Flat-title states then map to the title +
        # are section-range-scoped separately (a known manual step).
        last = (c.get("url", "").rstrip("/").rsplit("/", 1)[-1]).lower()
        if _LEAF_SECTION.match(last):
            continue
        out.append({"label": lab[:120], "url": c.get("url", "")})
    return out[:1200]  # safety cap (~100k tokens) so no state exceeds the 200k window


SYSTEM = (
    "You map U.S. state occupational-licensing statutes. Given one state's list of "
    "code chapters (label + url) and one profession, identify which chapter(s) hold "
    "that profession's LICENSING law. Key judgment: the right chapter often does NOT "
    "contain the profession's name — it may be a broad 'Occupational Code', "
    "'Contractors', 'Construction Industries Licensing', or 'Professions and "
    "Occupations' chapter that licenses the profession as one classification among "
    "many. If the profession is clearly licensed but only via such a broad container "
    "whose sub-articles are not in the list, return that container as "
    "umbrella_container_url (to expand later) rather than guessing. If the profession "
    "is regulated only locally or not at the state level, set licensed=false. Be "
    "precise; prefer the specific licensing chapter over general administrative ones."
)


def map_state(prof: str, defn: dict, state: str) -> dict | None:
    chapters = state_chapter_list(state)
    if not chapters:
        return None
    listing = "\n".join(f"- {c['label']}  [{c['url']}]" for c in chapters)
    user = (
        f"PROFESSION: {defn.get('display', prof)}\n"
        f"(matches terms like: {', '.join(defn.get('patterns') or [])})\n\n"
        f"STATE: {state}\nCHAPTERS:\n{listing}\n\n"
        "Which chapter(s) hold this profession's state licensing law?"
    )
    res = call_structured(model=MODEL, system=SYSTEM, user=user, schema_cls=StateMapping,
                          embed_schema=True, log_prefix=f"[{state}]")
    if res is None:
        return None
    return {"state": state, **res.model_dump()}


# ---------- Batched mode: one call per state maps MANY professions ----------
# The per-state chapter list dominates token cost; sending it once per state and
# mapping a batch of professions against it is ~25x cheaper than one call per
# (profession, state). Output is bounded by batching professions in groups.
PROF_BATCH = 20


class ProfMapping(StateMapping):
    profession: str = Field(description="the profession key this mapping is for")


class BatchResult(BaseModel):
    mappings: list[ProfMapping] = Field(description="one entry per profession asked about")


SYSTEM_BATCH = SYSTEM + (
    "\n\nYou will be given ONE state's chapter list and SEVERAL professions. Return "
    "a mapping for EVERY profession in the list (use its exact key)."
)


def map_state_batch(state: str, profs: list[tuple[str, dict]]) -> list[dict]:
    chapters = state_chapter_list(state)
    if not chapters:
        return []
    listing = "\n".join(f"- {c['label']}  [{c['url']}]" for c in chapters)
    out: list[dict] = []
    for i in range(0, len(profs), PROF_BATCH):
        chunk = profs[i:i + PROF_BATCH]
        proflines = "\n".join(
            f"- key={k}: {d.get('display', k)} (terms: {', '.join((d.get('patterns') or [])[:6])})"
            for k, d in chunk
        )
        user = (
            f"STATE: {state}\nCHAPTERS:\n{listing}\n\n"
            f"PROFESSIONS (map each one):\n{proflines}\n\n"
            "For each profession key, which chapter(s) hold its state licensing law?"
        )
        res = call_structured(model=MODEL, system=SYSTEM_BATCH, user=user,
                              schema_cls=BatchResult, embed_schema=True,
                              max_tokens=8000, log_prefix=f"[{state} {i//PROF_BATCH+1}]")
        if res is None:
            continue
        for m in res.mappings:
            out.append({"state": state, **m.model_dump()})
    return out


def run_batched(prof_names: list[str], states: list[str]) -> None:
    alldefs = yaml.safe_load((CONFIG_DIR / "professions.yaml").read_text())
    profs = [(k, alldefs[k]) for k in prof_names if k in alldefs and not k.startswith("_")]
    # accumulate per-profession rows
    by_prof: dict[str, list[dict]] = {k: [] for k, _ in profs}
    for st in states:
        rows = map_state_batch(st, profs)
        for r in rows:
            p = r.pop("profession", None)
            if p in by_prof:
                by_prof[p].append(r)
        done = sum(1 for r in rows if r.get("licensed"))
        print(f"  {st}: mapped {len(rows)} professions ({done} licensed)")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for p, rows in by_prof.items():
        (OUT_DIR / f"{p}.json").write_text(json.dumps({"profession": p, "states": rows}, indent=1, ensure_ascii=False))
    print(f"\nbatched: {len(profs)} professions x {len(states)} states → {OUT_DIR}")
    print(f"USAGE: {json.dumps(usage_summary())}")


# ---------- Pass 2: expand umbrella containers into specific articles ----------
# Pass 1 flags states where the profession is licensed but only via a broad
# container chapter whose sub-articles weren't in the hierarchy. Pass 2 fetches
# each flagged container's article list (Justia — shares the CDP Chrome with the
# grind via the flock, so it serializes) and asks the LLM which article(s) hold
# the profession's license, resolving the flag to concrete chapter_urls.

class ArticlePick(BaseModel):
    licensed: bool = Field(description="Does the container actually license this profession (in one of its articles)?")
    article_urls: list[str] = Field(default_factory=list, description="URL(s) of the specific article(s)/section-range that license this profession")
    basis: str


def _container_articles(container_url: str) -> list[dict]:
    """Fetch a container chapter page and return its child article/section links."""
    from pipeline.ingest import pull_text as pt
    from bs4 import BeautifulSoup
    import urllib.parse as _up
    status, html, _ = pt.fetch(container_url)
    if not html:
        return []
    base_path = _up.urlparse(container_url).path.rstrip("/")
    soup = BeautifulSoup(html, "html.parser")
    out, seen = [], set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        path = _up.urlparse(href).path
        # children of the container (one level deeper), not the container itself
        if base_path in href and path.rstrip("/") != base_path:
            lab = " ".join(a.get_text(" ", strip=True).split())
            if lab and href not in seen and len(lab) > 4:
                seen.add(href)
                out.append({"label": lab[:120], "url": href})
    return out[:200]


def run_pass2(prof: str) -> None:
    defn = load_profession(prof)
    fp = OUT_DIR / f"{prof}.json"
    if not fp.exists():
        sys.exit(f"no Pass-1 candidate file for {prof} — run Pass 1 first")
    d = json.loads(fp.read_text())
    flagged = [r for r in d["states"] if r.get("umbrella_container_url")]
    print(f"{prof}: expanding {len(flagged)} umbrella-flagged states")
    for r in flagged:
        arts = _container_articles(r["umbrella_container_url"])
        if not arts:
            print(f"  {r['state']}: container fetch empty — leaving flagged")
            continue
        listing = "\n".join(f"- {a['label']}  [{a['url']}]" for a in arts)
        user = (f"PROFESSION: {defn.get('display', prof)} (terms: {', '.join(defn.get('patterns') or [])})\n"
                f"STATE: {r['state']}\nThis is the article list inside the container "
                f"{r['umbrella_container_url']}:\n{listing}\n\n"
                "Which article(s) license this profession? If a specific article does, "
                "return it. If the container licenses it as a whole (unified contractor "
                "license, no per-trade article), licensed=true with empty article_urls. "
                "If it doesn't license this profession at all, licensed=false.")
        res = call_structured(model=MODEL, system=SYSTEM, user=user, schema_cls=ArticlePick,
                              embed_schema=True, log_prefix=f"[{r['state']}]")
        if res and res.licensed:
            # If a specific article was found use it; otherwise the container
            # itself IS the license (unified contractor chapter, no per-trade
            # article — e.g. CA CSLB / NV NRS 624 license electricians as a
            # classification, not a separate statute article).
            r["chapter_urls"] = res.article_urls or [r["umbrella_container_url"]]
            r["licensed"] = True
            r["umbrella_container_url"] = None
            print(f"  {r['state']}: resolved → {r['chapter_urls'][0].split('/codes/')[-1][:40]}")
        else:
            r["licensed"] = False
            print(f"  {r['state']}: container has no matching article → not licensed")
    fp.write_text(json.dumps(d, indent=1, ensure_ascii=False))
    print(f"\n{prof}: Pass-2 written → {fp}")
    print(f"USAGE: {json.dumps(usage_summary())}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", help="single profession (one call per state)")
    ap.add_argument("--pass2", action="store_true", help="expand umbrella-flagged states in the Pass-1 candidate file (needs --profession; uses Justia)")
    ap.add_argument("--all", action="store_true", help="batched: map ALL professions (cheap; one call per state per ~20 professions)")
    ap.add_argument("--professions", default="", help="batched: comma-separated profession subset")
    ap.add_argument("--states", default="", help="comma-separated subset; default all")
    args = ap.parse_args()
    states = [s.strip().upper() for s in args.states.split(",") if s.strip()] or ALL_STATES

    if args.pass2:
        if not args.profession:
            ap.error("--pass2 needs --profession")
        run_pass2(args.profession.lower())
        return

    if args.all or args.professions:
        alldefs = yaml.safe_load((CONFIG_DIR / "professions.yaml").read_text())
        names = ([k for k in alldefs if not k.startswith("_")] if args.all
                 else [s.strip() for s in args.professions.split(",") if s.strip()])
        run_batched(names, states)
        return
    if not args.profession:
        ap.error("give --profession, or --all / --professions for batched mode")
    prof = args.profession.lower()
    defn = load_profession(prof)
    states = [s.strip().upper() for s in args.states.split(",") if s.strip()] or ALL_STATES

    rows = []
    for st in states:
        r = map_state(prof, defn, st)
        if r is None:
            continue
        rows.append(r)
        flag = "UMBRELLA→expand" if r["umbrella_container_url"] else ("licensed" if r["licensed"] else "not-licensed")
        print(f"  {st}: {flag} | {len(r['chapter_urls'])} chap | {r['basis'][:70]}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{prof}.json"
    out.write_text(json.dumps({"profession": prof, "states": rows}, indent=1, ensure_ascii=False))
    lic = sum(1 for r in rows if r["licensed"])
    umb = sum(1 for r in rows if r["umbrella_container_url"])
    print(f"\n{prof}: {lic}/{len(rows)} licensed ({umb} umbrella-to-expand) → {out}")
    print(f"USAGE: {json.dumps(usage_summary())}")


if __name__ == "__main__":
    main()
