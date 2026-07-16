"""Discovery flywheel — find occupations NOT yet in the taxonomy. Mines every chapter/
section label for occupation-ish names that no profession pattern matches, then Haiku
classifies each as a real licensed occupation vs boilerplate (topics, boards, funds).
Output is the clean list of occupations to ADD to professions.yaml, then locate + pull.

  python -m pipeline.discover.gap_harvest.discover

Writes gap_harvest/discovered_occupations.json (name -> weight). The ~1,000-gap list is a
FLOOR; this is what turns it into a growing census. Loop until a round finds nothing new.
"""
from __future__ import annotations
import glob, json, logging, re, collections

import anthropic
from pipeline.config.loaders import load_professions
from pipeline.discover.match_profession import label_matches
from pipeline.discover.gap_harvest import _common as C

log = logging.getLogger(__name__)

_STRIP = re.compile(r'^\s*(chapter|article|part|subchapter|division|title)\s+[\dA-Za-z.\-]+\s*[-–.:]*\s*', re.I)
_SKIP = re.compile(r'general provision|^definition|penalt|^fees|repeal|reserved|miscellaneous|in general', re.I)
SYS = ("You classify U.S. state statute chapter titles. For each, decide if it names a "
       "DISTINCT LICENSED OCCUPATION — a kind of worker who must hold a state license, "
       "certification, or registration to practice (e.g. 'Opticians', 'Bail Bond Agents'). "
       "Return null for anything that is NOT a licensed-worker type: general topics, "
       "statutes/acts, business/entity types, insurance products, procedures, government "
       "bodies, boards, funds. Reply ONLY a JSON array, one object per input: "
       '{"i": <index>, "occ": "<canonical occupation name>" | null}.')


def _candidate_labels(profs: dict) -> collections.Counter:
    """Occupation-ish chapter labels that match no existing profession, by recurrence."""
    pats = [((v or {}).get("patterns") or [], (v or {}).get("excludes") or [])
            for k, v in profs.items() if not k.startswith("_")]
    cand: collections.Counter = collections.Counter()
    for f in glob.glob("pipeline/results/hierarchy/*.json"):
        try:
            chs = json.load(open(f)).get("chapters", [])
        except (OSError, json.JSONDecodeError) as e:
            log.warning("gap-discover: skipping unreadable hierarchy file %s (%s)", f, e)
            continue
        for c in chs:
            lab = (c.get("label", "") or "").strip()
            core = _STRIP.sub("", lab).strip().strip(".")
            if len(core) < 5 or _SKIP.search(core):
                continue
            if any(label_matches(lab, p, e) for p, e in pats):
                continue
            cand[core.lower()] += 1
    return cand


def main():
    profs = load_professions()
    ours = sorted(k for k in profs if not k.startswith("_"))
    cand = _candidate_labels(profs)
    recurring = [c for c, n in cand.most_common() if n >= 2]
    print(f"recurring candidate labels (>=2 states): {len(recurring)}", flush=True)

    client = anthropic.Anthropic()
    found: dict[str, int] = {}
    B = 50
    for i in range(0, len(recurring), B):
        batch = recurring[i:i + B]
        lines = "\n".join(f"{j}. {t}" for j, t in enumerate(batch))
        try:
            r = client.messages.create(
                model=C.MODEL, max_tokens=4000,
                system=SYS + f"\nWe ALREADY track these, don't return them: {', '.join(ours)}.",
                messages=[{"role": "user", "content": f"Classify these {len(batch)} titles:\n{lines}"}])
            txt = r.content[0].text
            arr = json.loads(txt[txt.find("["):txt.rfind("]") + 1])
            for o in arr:
                if o.get("occ"):
                    key = o["occ"].strip().lower()
                    found[key] = found.get(key, 0) + cand.get(batch[o["i"]], 1)
        except Exception as e:
            print(f"  batch {i // B + 1} error: {type(e).__name__}: {e}", flush=True)

    occs = dict(sorted(found.items(), key=lambda x: -x[1]))
    C.save_json("discovered_occupations.json", occs)
    print(f"\n{len(occs)} candidate occupations not in our {len(ours)}:")
    for name, weight in list(occs.items())[:30]:
        print(f"  {weight:3d}  {name}")


if __name__ == "__main__":
    main()
