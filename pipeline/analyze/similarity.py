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
MIN_COMPARABLE = 5        # neighbors need at least this many comparable fields


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


# ---------------------------------------------------------------- load matrix

def load_matrix(profession: str):
    p = DATA_DIR / f"{profession}.json"
    if not p.exists():
        sys.exit(f"no published data: {p}")
    d = json.loads(p.read_text())
    mp = d["map_prep"]
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

    # neighbors + distinctiveness
    sims = {}
    for a in states:
        row = []
        for b in states:
            if a == b:
                continue
            s, n = similarity(a, b, fields, M, sem_for, cont_stats)
            if s is not None and n >= MIN_COMPARABLE:
                row.append((round(s, 3), b, n))
        row.sort(reverse=True)
        sims[a] = row
    distinct = {a: round(1 - (statistics.mean([s for s, _, _ in sims[a]]) if sims[a] else 0), 3)
                for a in states}

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

    return {
        "profession": profession,
        "states": states,
        "n_discriminating_fields": len(fields),
        "neighbors": {a: [{"state": b, "sim": s, "n": n} for s, b, n in sims[a][:6]] for a in states},
        "distinctiveness": dict(sorted(distinct.items(), key=lambda kv: kv[1], reverse=True)),
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
