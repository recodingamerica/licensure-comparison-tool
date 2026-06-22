"""Per-profession similarity + outlier analysis.

For one profession, builds a state x field matrix from the published JSON's
`map_prep.rows` (each row is a normalized (field, state) value), then uses the
reviewable field_semantics config (importance weights + per-field value closeness)
to compute, deterministically:

  - neighbors:      per state, the most-similar states (importance + value-distance
                    weighted agreement, coverage-normalized)
  - distinctiveness: per state, 1 - mean similarity to all others (overall "weird")
  - kind_outliers:  (state, field) where the state's value is far from the modal
                    value AND held by few states — "doing something categorically rare"
  - stringency_outliers: on ordinal/continuous fields, states whose level sits
                    unusually high/low vs the distribution — "much stricter/looser"

The math can't infer field importance or how close two categories are; those come
from config/field_semantics.yaml (universal baseline) + config/field_semantics/
<profession>.yaml (per-profession importance + profession_specific closeness).

Usage:
  python -m pipeline.analyze.similarity --profession optometry [--focus UT]
  python -m pipeline.analyze.similarity --profession optometry --json   # write results/analysis/<prof>.json
"""
from __future__ import annotations

import argparse
import json
import itertools
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
DATA_DIR = REPO / "pipeline" / "publish" / "web" / "public" / "data"
SEM_PATH = REPO / "pipeline" / "config" / "field_semantics.yaml"
SEM_PROF_DIR = REPO / "pipeline" / "config" / "field_semantics"
OUT_DIR = REPO / "pipeline" / "results" / "analysis"

RARE_SHARE = 0.20         # kind outlier: value held by <= this share of states
STRINGENCY_Z = 1.5        # stringency outlier: |z| beyond this on an ordinal/continuous field
CORE_IMPORTANCE = 0.4     # a field joins the "core" comparison set if it matters >= this
CORE_COVERAGE = 0.6       # ...AND at least this fraction of states actually answer it


# ---------------------------------------------------------------- config

def load_semantics(profession: str) -> dict:
    """Merged field-config: _defaults + universal + per-profession overrides."""
    base = yaml.safe_load(SEM_PATH.read_text())
    defaults = base.get("_defaults", {})
    fields = dict(base.get("universal", {}))
    prof_path = SEM_PROF_DIR / f"{profession}.yaml"
    if prof_path.exists():
        pf = yaml.safe_load(prof_path.read_text()) or {}
        for k, v in (pf.get("fields") or {}).items():
            # deep-merge per field so a per-profession entry doesn't drop the
            # universal `phrase` (or other keys) it didn't restate.
            if isinstance(fields.get(k), dict) and isinstance(v, dict):
                fields[k] = {**fields[k], **v}
            else:
                fields[k] = v
    return {"defaults": defaults, "fields": fields}


def field_cfg(sem: dict, field: str) -> dict:
    return sem["fields"].get(field, sem["defaults"])


# ---------------------------------------------------------------- closeness

def _ordinal_rank(order: list, v: str):
    try:
        return order.index(v)
    except ValueError:
        return None


def value_distance(cfg: dict, va, vb, cont_stats) -> float | None:
    """0 (identical) .. 1 (maximally different); None if not comparable."""
    if va is None or vb is None:
        return None
    cl = cfg.get("closeness", {"kind": "nominal"})
    kind = cl.get("kind", "nominal")
    sa, sb = str(va), str(vb)
    if kind == "ordinal":
        order = cl.get("order", [])
        ra, rb = _ordinal_rank(order, sa), _ordinal_rank(order, sb)
        if ra is None or rb is None or len(order) < 2:
            return 0.0 if sa == sb else 1.0
        return abs(ra - rb) / (len(order) - 1)
    if kind == "continuous":
        try:
            fa, fb = float(va), float(vb)
        except (TypeError, ValueError):
            return 0.0 if sa == sb else 1.0
        rng = cont_stats.get("range") or 0
        return 0.0 if rng == 0 else min(1.0, abs(fa - fb) / rng)
    # nominal
    if sa == sb:
        return 0.0
    dmap = cl.get("distances") or {}
    for key in (f"{sa}|{sb}", f"{sb}|{sa}"):
        if key in dmap:
            return float(dmap[key])
    return 1.0


# ---------------------------------------------------------------- labels + prose
# The calculation owns the qualitative WORD (one controlled vocabulary); the note
# is template-assembled from those words. No LLM, fully reproducible.

def rarity_label(n_states: int, total: int) -> str:
    share = n_states / total if total else 1.0
    if n_states <= 2:
        return "almost unique"
    if share <= 0.15:
        return "rare"
    if share <= 0.33:
        return "uncommon"
    return "a minority view"


def stringency_label(z: float, direction: str) -> str:
    looser = "looser" if (z < 0 or "looser" in direction) else "stricter"
    return f"far {looser} than most" if abs(z) >= 2.5 else f"{looser} than most"


def band_for(state: str, ranked_keys: list) -> str | None:
    if state not in ranked_keys:
        return None
    r, t = ranked_keys.index(state) + 1, len(ranked_keys)
    return ("highly distinctive" if r <= t * 0.2 else
            "moderately distinctive" if r <= t * 0.5 else
            "fairly typical" if r <= t * 0.8 else "typical")


_BOOL_SUFFIX = [
    ("_required", "requires", "does not require"),
    ("_authorized", "authorizes", "does not authorize"),
    ("_permitted", "permits", "does not permit"),
    ("_allowed", "allows", "does not allow"),
    ("_prohibited", "prohibits", "does not prohibit"),
    ("_excluded", "excludes", "does not exclude"),
    ("_available", "offers", "does not offer"),
    ("_offered", "offers", "does not offer"),
    ("_exists", "has", "lacks"),
]
# leaf words too generic to stand alone — fold in the parent segment for meaning
# (e.g. continuing_education.required -> "continuing_education_required").
_GENERIC_LEAVES = {"required", "available", "exists", "offered", "permitted",
                   "authorized", "prohibited", "allowed", "excluded", "type"}


def clause(field: str, value, sem: dict) -> str:
    """field=value -> a readable verb phrase. Boolean fields use name-suffix rules;
    enum fields use an optional `phrase` template from field_semantics; else a
    plain 'label: value' fallback."""
    parts = field.split(".")
    leaf = parts[-1]
    if leaf in _GENERIC_LEAVES and len(parts) >= 2:
        leaf = f"{parts[-2]}_{leaf}"
    phrase = field_cfg(sem, field).get("phrase")
    human = str(value).replace("_", " ")
    if phrase:
        return phrase.format(value=human)
    v = str(value).lower()
    if v in ("true", "false"):
        for suf, yes, no in _BOOL_SUFFIX:
            if leaf.endswith(suf):
                base = leaf[: -len(suf)].replace("_", " ").strip()
                return f"{yes if v == 'true' else no} {base}"
        return f"{'has' if v == 'true' else 'lacks'} {leaf.replace('_', ' ')}"
    return f"{leaf.replace('_', ' ')}: {human}"


def build_note(state: str, prof_display: str, band: str, neighbors: list, findings: list, sem: dict) -> str:
    lead = f"{state} is {band} in {prof_display}"
    if neighbors:
        lead += f", most like {', '.join(neighbors)}"
    if findings:
        cls = [f"{clause(f['field'], f['value'], sem)} ({f['label']})" for f in findings]
        return lead + ". It " + " and ".join(cls) + "."
    return lead + ", with nothing that stands out."


# ---------------------------------------------------------------- load matrix

def load_matrix(profession: str):
    p = DATA_DIR / f"{profession}.json"
    if not p.exists():
        sys.exit(f"no published data: {p}")
    d = json.loads(p.read_text())
    mp = d.get("map_prep")
    if not mp:
        print(f"{profession}: no map_prep — nothing to compare; skipping.")
        raise SystemExit(0)
    kinds = {s["field_name"]: s["kind"] for s in mp["spec"]}
    M: dict[str, dict] = defaultdict(dict)
    for r in mp["rows"]:
        v = r.get("normalized")
        if v is None:
            continue
        M[r["field_name"]][r["state"]] = v   # M[field][state]
    states = sorted({s for f in M for s in M[f]})
    # continuous stats (range) per field, for distance scaling
    cont_stats = {}
    for f, sv in M.items():
        nums = []
        for v in sv.values():
            try:
                nums.append(float(v))
            except (TypeError, ValueError):
                pass
        if nums:
            cont_stats[f] = {"range": (max(nums) - min(nums)), "vals": nums}
    return d, M, states, kinds, cont_stats


# ---------------------------------------------------------------- analysis

def discriminating(M, states):
    """Fields that actually vary across states (uniform fields carry no signal)."""
    out = []
    for f, sv in M.items():
        if len({str(v) for v in sv.values()}) > 1:
            out.append(f)
    return out


def similarity(a, b, fields, M, sem, cont_stats):
    num = den = n = 0.0
    for f in fields:
        va, vb = M[f].get(a), M[f].get(b)
        if va is None or vb is None:
            continue
        d = value_distance(field_cfg(sem, f), va, vb, cont_stats.get(f, {}))
        if d is None:
            continue
        w = field_cfg(sem, f).get("importance", 0.5)
        num += w * (1 - d)
        den += w
        n += 1
    if n < 1 or den == 0:
        return None, 0
    return num / den, int(n)


def analyze(profession: str):
    d, M, states, kinds, cont_stats = load_matrix(profession)
    fields = discriminating(M, states)
    n_states = len(states)

    # CORE comparison set: important fields that MOST states actually answer, so
    # every pair is graded on the SAME questions. Otherwise overlap rides on
    # whatever sparse subset two states happen to share, and a state that answers
    # few questions scores a misleadingly high overlap.
    core_fields = [
        f for f in fields
        if field_cfg(sem_for, f).get("importance", 0.5) >= CORE_IMPORTANCE
        and len(M[f]) >= CORE_COVERAGE * n_states
    ]
    n_core = len(core_fields)
    core_have = {st: sum(1 for f in core_fields if st in M[f]) for st in states}
    # a state must answer most of the core to be compared at all; others are
    # surfaced as "not enough data" rather than given a fake score.
    sufficient = {st for st in states if n_core and core_have[st] >= CORE_COVERAGE * n_core}
    insufficient = sorted(set(states) - sufficient)

    # neighbors + distinctiveness — sufficient states only, over the core set
    sims = {}
    for a in states:
        if a not in sufficient:
            sims[a] = []
            continue
        row = []
        for b in sufficient:
            if a == b:
                continue
            s, n = similarity(a, b, core_fields, M, sem_for, cont_stats)
            if s is not None:
                row.append((round(s, 3), b, n))
        row.sort(reverse=True)
        sims[a] = row
    distinct = {a: round(1 - statistics.mean([s for s, _, _ in sims[a]]), 3)
                for a in sufficient if sims[a]}

    # kind outliers: rare value AND far from mode (weighted by importance)
    kind_out = []
    for f in fields:
        cfg = field_cfg(sem_for, f)
        if cfg.get("closeness", {}).get("kind") == "continuous":
            continue
        sv = M[f]
        cnt = Counter(str(v) for v in sv.values())
        tot = sum(cnt.values())
        mode = cnt.most_common(1)[0][0]
        for st, v in sv.items():
            share = cnt[str(v)] / tot
            dmode = value_distance(cfg, v, mode, cont_stats.get(f, {})) or 0
            if share <= RARE_SHARE and dmode > 0:
                kind_out.append({
                    "state": st, "field": f, "value": str(v),
                    "share": round(share, 3), "n_states": cnt[str(v)], "total": tot,
                    "importance": cfg.get("importance", 0.5),
                    "score": round(cfg.get("importance", 0.5) * dmode * (1 - share), 3),
                })
    kind_out.sort(key=lambda x: x["score"], reverse=True)

    # stringency outliers: ordinal/continuous fields, state level vs distribution
    string_out = []
    for f in fields:
        cfg = field_cfg(sem_for, f)
        cl = cfg.get("closeness", {})
        kind = cl.get("kind")
        levels = {}
        if kind == "ordinal":
            order = cl.get("order", [])
            for st, v in M[f].items():
                r = _ordinal_rank(order, str(v))
                if r is not None:
                    levels[st] = r
        elif kind == "continuous":
            for st, v in M[f].items():
                try:
                    levels[st] = float(v)
                except (TypeError, ValueError):
                    pass
        if len(levels) < 4:
            continue
        vals = list(levels.values())
        mu = statistics.mean(vals)
        sd = statistics.pstdev(vals)
        if sd == 0:
            continue
        for st, lv in levels.items():
            z = (lv - mu) / sd
            if abs(z) >= STRINGENCY_Z:
                string_out.append({
                    "state": st, "field": f, "value": str(M[f][st]),
                    "z": round(z, 2), "direction": "stricter/higher" if z > 0 else "looser/lower",
                    "importance": cfg.get("importance", 0.5),
                    "score": round(cfg.get("importance", 0.5) * abs(z), 3),
                })
    string_out.sort(key=lambda x: x["score"], reverse=True)

    # landscape: how much states differ + what separates them — computed over the
    # SAME core set and sufficient states as the overlap, so it's consistent.
    suf = sorted(sufficient)
    allpairs = []
    for a, b in itertools.combinations(suf, 2):
        s, n = similarity(a, b, core_fields, M, sem_for, cont_stats)
        if s is not None:
            allpairs.append(s)
    drivers = []
    for f in core_fields:
        cfg = field_cfg(sem_for, f)
        ds = []
        for a, b in itertools.combinations(suf, 2):
            va, vb = M[f].get(a), M[f].get(b)
            if va is None or vb is None:
                continue
            dd = value_distance(cfg, va, vb, cont_stats.get(f, {}))
            if dd is not None:
                ds.append(dd)
        if ds:
            sep, imp = statistics.mean(ds), cfg.get("importance", 0.5)
            drivers.append({"field": f, "separation": round(sep, 3), "importance": imp,
                            "drive": round(sep * imp, 3), "coverage": len(M[f])})
    drivers.sort(key=lambda d: d["drive"], reverse=True)
    landscape = {
        "pairwise_sim": ({
            "mean": round(statistics.mean(allpairs), 3), "min": round(min(allpairs), 3),
            "max": round(max(allpairs), 3), "stdev": round(statistics.pstdev(allpairs), 3),
            "pct_alike_90": round(sum(1 for p in allpairs if p >= 0.9) / len(allpairs), 3),
        } if allpairs else {}),
        "drivers": drivers[:8],
        "n_near_uniform": sum(1 for d in drivers if d["drive"] < 0.05),
        "n_states_total": len(states),
        "n_compared": len(suf),
    }
    # Qualitative spread band so the UI never has to quote a similarity %.
    _pa = landscape["pairwise_sim"]
    landscape["spread_label"] = (
        "narrow" if _pa and _pa["pct_alike_90"] >= 0.7
        else "moderate" if _pa and _pa["pct_alike_90"] >= 0.4
        else "wide"
    )

    for o in kind_out:
        o["rarity"] = rarity_label(o["n_states"], o["total"])
    for o in string_out:
        o["magnitude"] = stringency_label(o["z"], o["direction"])

    # Per-state agreement vs deviation on the higher-importance CATEGORICAL fields.
    #   typical_on: the state holds the majority value (where it agrees).
    #   differs_on: it doesn't — the values that make it distinctive, each with a
    #               label (ordinal extremes -> "far stricter than most"; otherwise
    #               how-rare the value is). Together these cover every high-value
    #               question the state answers, so a distinctive state shows many
    #               differs rows instead of an empty card.
    vcount = {f: Counter(str(v) for v in M[f].values()) for f in fields if M[f]}
    modes = {f: c.most_common(1)[0][0] for f, c in vcount.items()}
    string_by = {(o["state"], o["field"]): o["magnitude"] for o in string_out}

    def hi_cat_fields(st):
        for f in fields:
            cfg = field_cfg(sem_for, f)
            if cfg.get("importance", 0.5) < 0.4 or cfg.get("closeness", {}).get("kind") == "continuous":
                continue
            if st in M[f]:
                yield f, cfg

    typical, differs = {}, {}
    for st in states:
        tlist, dlist = [], []
        for f, cfg in hi_cat_fields(st):
            v = str(M[f][st])
            imp = cfg.get("importance", 0.5)
            if v == modes.get(f):
                tlist.append((imp, {"field": f, "value": v, "importance": imp}))
            else:
                tot = sum(vcount[f].values())
                label = string_by.get((st, f)) or rarity_label(vcount[f][v], tot)
                dlist.append((imp * (1 - vcount[f][v] / tot),
                              {"field": f, "value": v, "label": label, "importance": imp}))
        tlist.sort(key=lambda x: x[0], reverse=True)
        dlist.sort(key=lambda x: x[0], reverse=True)
        typical[st] = [x for _, x in tlist[:6]]
        differs[st] = [x for _, x in dlist[:8]]

    ranked = list(dict(sorted(distinct.items(), key=lambda kv: kv[1], reverse=True)))
    bands = {st: band_for(st, ranked) for st in sufficient}
    prof_display = d.get("display", profession)
    notes = {}
    for st in states:
        if st not in sufficient:
            notes[st] = f"{st} answers too few of the core questions to compare."
            continue
        nbs = [b for _s, b, _n in sims[st][:3]]
        notes[st] = build_note(st, prof_display, bands.get(st, "typical"), nbs, differs[st][:2], sem_for)

    return {
        "profession": profession,
        "states": states,
        "n_discriminating_fields": len(fields),
        "bands": bands,
        "notes": notes,
        # the fixed set of questions every overlap is graded on (importance + coverage gated)
        "core_fields": core_fields,
        "n_core": n_core,
        "core_importance_min": CORE_IMPORTANCE,
        "core_coverage_min": CORE_COVERAGE,
        # states that don't answer enough of the core to be compared
        "insufficient_states": insufficient,
        # how much of the core each compared state actually answers (0..1) — a
        # confidence signal: a distinctiveness score over few core answers is shaky.
        "core_coverage": ({st: round(core_have[st] / n_core, 2) for st in sufficient} if n_core else {}),
        "landscape": landscape,
        "neighbors": {a: [{"state": b, "sim": s, "n": n} for s, b, n in sims[a][:6]] for a in states},
        "distinctiveness": dict(sorted(distinct.items(), key=lambda kv: kv[1], reverse=True)),
        "typical_on": typical,
        "differs_on": differs,
        "kind_outliers": kind_out,
        "stringency_outliers": string_out,
    }


sem_for: dict = {}


def main() -> int:
    global sem_for
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True)
    ap.add_argument("--focus", default="UT", help="State to spotlight in the printed report")
    ap.add_argument("--json", action="store_true", help="Write results/analysis/<prof>.json")
    args = ap.parse_args()
    prof = args.profession.lower()
    sem_for = load_semantics(prof)
    res = analyze(prof)

    f = args.focus.upper()
    print(f"=== {prof}: similarity / outliers ({len(res['states'])} states, {res['n_discriminating_fields']} discriminating fields) ===")
    nb = res["neighbors"].get(f, [])
    print(f"\n[{f}] most similar: " + ", ".join(f"{x['state']} {x['sim']:.0%}({x['n']})" for x in nb[:5]))
    print(f"[{f}] distinctiveness rank: {list(res['distinctiveness']).index(f)+1} of {len(res['states'])} (score {res['distinctiveness'][f]})")
    print(f"\n[{f}] kind outliers (categorically rare):")
    for o in [o for o in res["kind_outliers"] if o["state"] == f][:6]:
        print(f"    {o['field'].split('.')[-1]:28s} = {o['value']!r}  ({o['n_states']}/{o['total']} states, imp {o['importance']})")
    print(f"[{f}] stringency outliers (much stricter/looser):")
    for o in [o for o in res["stringency_outliers"] if o["state"] == f][:6]:
        print(f"    {o['field'].split('.')[-1]:28s} = {o['value']!r}  {o['direction']} (z={o['z']})")
    print(f"\nmost DISTINCTIVE states overall: " + ", ".join(f"{s}({v})" for s, v in list(res['distinctiveness'].items())[:5]))

    if args.json:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUT_DIR / f"{prof}.json").write_text(json.dumps(res, indent=2))
        print(f"\nwrote {OUT_DIR / f'{prof}.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
