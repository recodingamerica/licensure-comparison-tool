# Verified absences (correct-blanks) — how it works & how to tweak

Some (profession, state) pairs have **no state-level license** — the profession is
regulated locally, or not at all. These are *correct answers*, not data gaps. Rather
than hard-code a bespoke "blank" concept, we represent them as ordinary
`regulatory_model = market_forces` records (the pipeline's existing "no state
regulation" value) that are **transparently marked** as research-asserted, and are
**controlled by a single off-switch**.

## The line we hold
- **Overrides** (`state_structure.yaml` per-profession `url`) tell the pipeline *where
  the statute lives*; the LLM **derives** the values. Always prefer this.
- **Verified absences** *assert* the value because there is **no statute to point at**.
  Only for confirmed local-only / not-regulated cases, and always marked as such.
- For a genuine null with no statute at all, `verify_gap_states` (LLM) can instead
  *derive* the absence from the state's statute index — preferred where feasible.

## Where to tweak

1. **Add / remove a case** — edit `pipeline/config/verified_absences.yaml`:
   ```yaml
   electrician:
     IL: {basis: local_only, citation: "65 ILCS 5/11-33-1", note: "…"}
   ```
   `basis` ∈ {`local_only`, `not_regulated`, `contractor_only`}. `citation` is the
   local-enabling hook if one exists, else `""`. Then regenerate:
   ```
   python -m pipeline.extract.apply_verified_absences   # writes structured/<prof>/<state>.json
   python -m pipeline.publish.build_frontend --profession <prof> --payload-only
   ```
   (`apply_verified_absences` never overwrites a real extracted record unless `--force`.)

2. **The OFF SWITCH** — `pipeline/config/publish_options.yaml`:
   ```yaml
   include_verified_absences: true   # false = the whole feature off
   ```
   `false` → every verified-absence row falls back to an ordinary coverage gap ("no
   credential found"), exactly as if we'd never asserted it. One parameter, site-wide.
   (Verified: electrician covered = 44 with it on, 39 with it off.)

## How it looks in the UI
Every payload row carries `data_basis` (`extracted` | `verified_absence`). A
verified-absence row shows, in its state-detail dialog:
- an amber **"Not state-regulated · research-verified"** badge in the title, and
- a banner: *"No state license… This row is hand-verified research, not a statute
  extraction — there is no state statute to quote."* + the `note`.

So it is never mistaken for a statute extraction. Source: Atharv #53 findings, in
`docs/lit_review/sources/trades_53/`.
