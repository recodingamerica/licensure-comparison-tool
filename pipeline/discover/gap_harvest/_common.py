"""Shared core for the gap-harvest package: state slugs, the web_search locator,
URL hygiene, and the data directory. Everything else in this package imports from here
so there's one definition of each — no copy-paste.

Data lives in results/gap_harvest/ (override with GAP_HARVEST_DIR). The web_search locator
needs the `web_search` tool on the Anthropic key; probe once before a big run.
"""
from __future__ import annotations
import os, re, json
from pathlib import Path

from pipeline._env import load_env
from pipeline.paths import RESULTS_DIR
from pipeline._records import read_json

load_env()

# --- data directory (single home for gap-harvest artifacts) --------------------
DATA_DIR = Path(os.environ.get("GAP_HARVEST_DIR", RESULTS_DIR / "gap_harvest"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

def data_path(name: str) -> Path:
    return DATA_DIR / name

def load_json(name: str, default=None):
    return read_json(data_path(name), {} if default is None else default)

def save_json(name: str, obj) -> None:
    data_path(name).write_text(json.dumps(obj, indent=1))

# --- state abbreviation -> Justia code slug ------------------------------------
STATE_SLUG = {
    "AL": "alabama", "AK": "alaska", "AZ": "arizona", "AR": "arkansas", "CA": "california",
    "CO": "colorado", "CT": "connecticut", "DE": "delaware", "FL": "florida", "GA": "georgia",
    "HI": "hawaii", "ID": "idaho", "IL": "illinois", "IN": "indiana", "IA": "iowa",
    "KS": "kansas", "KY": "kentucky", "LA": "louisiana", "ME": "maine", "MD": "maryland",
    "MA": "massachusetts", "MI": "michigan", "MN": "minnesota", "MS": "mississippi",
    "MO": "missouri", "MT": "montana", "NE": "nebraska", "NV": "nevada", "NH": "new-hampshire",
    "NJ": "new-jersey", "NM": "new-mexico", "NY": "new-york", "NC": "north-carolina",
    "ND": "north-dakota", "OH": "ohio", "OK": "oklahoma", "OR": "oregon", "PA": "pennsylvania",
    "RI": "rhode-island", "SC": "south-carolina", "SD": "south-dakota", "TN": "tennessee",
    "TX": "texas", "UT": "utah", "VT": "vermont", "VA": "virginia", "WA": "washington",
    "WV": "west-virginia", "WI": "wisconsin", "WY": "wyoming",
}
ALL_STATES = list(STATE_SLUG)

# --- URL hygiene ---------------------------------------------------------------
def normalize_url(url: str | None) -> str | None:
    """Justia code paths hyphenate title/chapter numbers; the model sometimes emits a
    dot (title-32.1 -> title-32-1). Dots never appear in valid Justia code slugs."""
    if not url or url == "null" or "law.justia.com/codes/" not in url:
        return url
    head, _, path = url.partition("/codes/")
    return head + "/codes/" + path.replace(".", "-")

def is_valid_for_state(url: str | None, state: str) -> bool:
    return bool(url) and url != "null" and "law.justia.com" in url \
        and f"/codes/{STATE_SLUG.get(state, '')}/" in url

# --- the web_search locator (one definition, prompt-selectable) ----------------
MODEL = "claude-haiku-4-5-20251001"

# strict: only licensure. recover: any chapter that ADDRESSES the occupation (incl.
# exemption/certification) — used to re-check nulls without inventing absences.
#
# Every mode also asks about MULTI-CHAPTER component-decomposition (added 2026-07-08
# after hvac/MA: sheet metal Ch112 + gas fitters Ch142 + refrigeration Ch146§85, no
# single chapter covers it). The single-URL answer stays the primary/best-guess target;
# `additional_urls` is a separate signal for a human to review before pulling, not
# something downstream auto-trusts — the model can name a plausible-sounding chapter
# it hasn't actually verified as readily as it can find the primary one.
_MULTI_CHAPTER_ASK = (
    " Also check whether this occupation is COMPONENT-DECOMPOSED — regulated across "
    "SEVERAL separate, non-contiguous chapters instead of one (e.g. HVAC in Massachusetts "
    "is split across sheet metal workers, gas fitters, and refrigeration technicians, each "
    "its own chapter). If you find evidence of this, list the other chapter URLs too.")
_PROMPTS = {
    "strict": (
        "You locate the primary licensing statute for an occupation on Justia. Given an "
        "occupation and a U.S. state, search law.justia.com and return the SINGLE Justia code "
        "URL for the CHAPTER, ARTICLE, or PART (a container that lists sections — NOT a single "
        "section, NOT a year-versioned page) that primarily governs that occupation's LICENSE/"
        "CERTIFICATION/REGISTRATION to practice in that state. Prefer the current year-less path "
        "like https://law.justia.com/codes/<state>/<title>/<chapter>/ . If the state genuinely "
        "does not license this occupation at the state level, return null." + _MULTI_CHAPTER_ASK),
    "recover": (
        "You locate any statute chapter that ADDRESSES an occupation on Justia — not only "
        "licensure. Return the SINGLE Justia code URL for the CHAPTER/ARTICLE/PART (a container "
        "listing sections, current year-less path, NOT a single section) that governs, certifies, "
        "registers, OR expressly EXEMPTS this occupation in that state. Return the chapter even if "
        "the occupation is exempt or only nationally-certified there. Return null ONLY if the "
        "state's code truly contains no chapter addressing this occupation at all." + _MULTI_CHAPTER_ASK),
    "chapter": (
        "You locate the CHAPTER-LEVEL container for an occupation's statute on Justia. Given an "
        "occupation and state, return the SINGLE Justia code URL for the CHAPTER or ARTICLE that "
        "lists MANY sections about it — go UP a level if the obvious hit is a single section or a "
        "narrow sub-part, so we capture the whole regime. Current year-less path. null if truly "
        "unlicensed." + _MULTI_CHAPTER_ASK),
}
_RESULT_LINE = (' End your reply with exactly one line: '
                'RESULT: {"url": "<url or null>", "label": "<chapter label>", '
                '"confidence": "high|med|low", "additional_urls": ["<url>", ...]}'
                ' (additional_urls: [] if none found)')

def locate(profession: str, state: str, profs: dict, mode: str = "strict") -> dict:
    """Return {url, label, confidence, additional_urls} for one (profession, state), or
    url=None. `profs` is load_professions() output. `mode` selects the prompt.
    `additional_urls` (possibly []) flags suspected multi-chapter component-decomposition
    for human review — not verified, not auto-pulled."""
    import anthropic
    client = anthropic.Anthropic()
    meta = profs.get(profession, {}) or {}
    disp = meta.get("display") or profession
    pats = ", ".join((meta.get("patterns") or [])[:4])
    slug = STATE_SLUG[state]
    q = (f"Occupation: {disp} (aka: {pats}). State: {state} ({slug}). "
         f"Find its chapter on law.justia.com/codes/{slug}/ .")
    system = _PROMPTS[mode] + _RESULT_LINE
    for attempt in range(2):
        try:
            r = client.messages.create(
                model=MODEL, max_tokens=1500, system=system,
                tools=[{"type": "web_search_20250305", "name": "web_search",
                        "max_uses": 4, "allowed_domains": ["law.justia.com"]}],
                messages=[{"role": "user", "content": q}])
            txt = "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
            m = re.search(r'RESULT:\s*(\{.*\})', txt, re.S)
            if m:
                res = json.loads(m.group(1))
                res["url"] = normalize_url(res.get("url"))
                res["additional_urls"] = [normalize_url(u) for u in (res.get("additional_urls") or [])
                                          if normalize_url(u)]
                return res
            return {"url": None, "label": "", "confidence": "parse_fail", "additional_urls": []}
        except Exception as e:
            if attempt == 1:
                return {"url": None, "label": "", "confidence": f"err:{type(e).__name__}", "additional_urls": []}
    return {"url": None, "label": "", "confidence": "err", "additional_urls": []}
