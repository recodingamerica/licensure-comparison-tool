# Handoff plan — extending occupation coverage after we hand this over

**Question this answers:** can someone else realistically add the occupations we
haven't done, and what needs to happen to make that possible?

**Short answer:** Yes — but only the *automated 80%* is turnkey. The remaining
~20% (coverage QA + Justia operation) needs a person with specific skills and
~half a day per occupation today. Two enablers below would cut that materially.
Pair this with the step-by-step in [[adding_a_new_occupation]] and the
gotchas in [[reference_concurrent_pull_corruption]] / [[reference_pipeline_stage_order]].

---

## 1. What's turnkey vs. what needs a human

| Stage | Automated? | Human effort |
|---|---|---|
| Register profession (`professions.yaml`) | manual, trivial | 5 min — display name, abbrev, family, match patterns |
| Match → `profession_index` (`match_profession`) | **automated** | 0 — pure pattern match, no fetch. Gets the easy ~85% of states |
| Pull statute text (Justia/official) | semi-automated | **the operational bottleneck** — needs the CDP Chrome up, manual first-challenge solve, ONE-pull-per-Chrome discipline |
| Umbrella / coverage gap recovery | **manual + judgment** | **the analytic bottleneck** — find states the matcher missed (licensing hidden in a contractor/occupational-code umbrella, or a differently-labeled chapter) |
| clean → trim → extract | **automated** (LLM batch) | 0 beyond kicking it off; ~$1–4/occupation |
| map_prep + bucket_text | **automated** (LLM) | 0 beyond kicking it off; ~$2–4/occupation |
| Build + publish (`refresh_all`, preview, prod) | **automated** | 0 beyond one config edit (`build_state_browse.py` list) + the deploy |

So the pipeline *itself* is in good shape. The two things that don't automate are
**(A) running Justia** and **(B) finding the coverage the matcher misses.**

## 2. The two real bottlenecks (and why)

**A. Justia operation.** Justia is behind a Cloudflare fingerprint wall. Our only
working path is CDP-attaching to a real Chrome the operator starts and solves the
first challenge in (see [[official_source_migration]]). Consequences for a handoff
person: they must run that Chrome, occasionally re-solve a challenge, and never run
two Justia pulls at once (now guarded by a flock, but they need to understand it).
Per-section pulls are slow and *look* frozen (no per-section logging) — easy to
mistake for a hang. This is learnable in an hour but is not "press a button."

**B. Coverage QA — the matcher's blind spot.** `match_profession` matches profession
keywords against chapter *labels*. It misses two big cases:
  1. **Umbrella-nested licensing** — the trade/profession is an *article inside* a
     unified "Occupational Code / Contractors / Construction Industries" chapter
     whose label doesn't contain the profession keyword (e.g. NM ch 60 art 13, MI
     ch 339, MN ch 326B). Invisible to a label match.
  2. **Classification-under-one-board** — the profession is licensed only as a
     classification under a single contractor board (CA CSLB, AZ ROC, NV NSCB); the
     statute is the contractor law, not a profession-named chapter.
  Recovering these is exactly the manual work this session did for the 4 trades:
  grep the local `results/hierarchy/<state>.json`, fetch a container TOC, decide
  whether it's really licensed and where, patch the `profession_index` node
  *surgically* (NOT by re-running `match_profession`, which wipes manual additions).
  This needs licensing-domain judgment and is the part that least resembles a script.

## 3. Skill profile the handoff person needs
- Comfortable on a Python CLI, reading/patching JSON, basic git.
- Willing to operate the CDP-Chrome Justia flow (solve a challenge, watch a log).
- Enough legal-domain sense to judge "is this occupation state-licensed here, and
  which chapter is the license" — or access to someone who can spot-check.
- They do **not** need to understand the LLM internals; extract/map_prep/publish are
  invoke-and-wait.

## 4. Enablers to build (to make handoff realistic) — prioritized
1. **Coverage-gap finder script (highest leverage).** Systematize what was done by
   hand this session: for a profession, grep every state's `hierarchy/` for the
   profession's keywords + known umbrella containers, diff against `profession_index`,
   and emit a ranked "licensed-but-unmapped candidates" list with the chapter URL +
   a licensed-state count vs. an external reference (IJ/NCSL as a *pointer*, per
   [[external_data_as_pointer_not_source]]). This turns the analytic bottleneck into
   "review a candidate list" instead of "investigate 50 states from scratch."
2. **A guarded/operator-friendly Justia pull wrapper.** `/tmp/guarded_repull.sh`
   (restore-HEAD-and-retry on partials) should be promoted into the repo with docs,
   plus a one-command "start the debug Chrome" helper, so the operator isn't
   re-deriving the flow. The flock + grind child-kill (shipped this session) already
   removed the worst footgun.
3. **A per-occupation checklist run** that chains match → pull → clean → trim →
   extract → map_prep → bucket_text → build for a single profession with the gates
   (`check_consistency`, count-vs-reality) built in, so the operator runs one thing
   and reviews the gates.

## 5. Recommended operating model: "map as they come in"
- Don't try to backfill all ~75 professions before handoff. Instead:
  - Hand over with the published set + the 4 trades + the runbook + the gap-finder.
  - When a new occupation is needed, the operator runs the per-occupation chain
    (mostly automated), then spends the residual time on coverage QA using the
    gap-finder's candidate list.
- **Realistic effort per occupation today:** ~0.5 day (mostly Justia operation +
  coverage QA). With the gap-finder built: closer to ~1–2 hours of review + invoke.
- **Batchable:** the LLM stages (extract/map_prep) run unattended and cheaply, so an
  operator can queue several occupations' pulls, then batch the downstream overnight.

## 6. What's already done that de-risks the handoff
- `professions.yaml` already defines ~75 professions (match patterns ready) — the
  matcher will give a first-pass mapping for any of them with no new config.
- The frontend is fully dynamic: a new occupation needs **one** code edit
  (`build_state_browse.py` list) + the publish command; everything else
  (`core_professions()`, routes, professions.json) auto-includes it.
- Operational footguns fixed this session: concurrent-pull corruption (flock),
  orphaned grind child (child-kill), pull_md runaway (section cap).
- The broad CDP-Justia *harvest* (`_cdp_grind.py`) is already pulling text for the
  unpublished professions in the background — so for many occupations the **text may
  already be on disk**, leaving only clean→trim→extract→publish + coverage QA.

## 7. Open risks to flag to whoever takes this
- Justia could re-block; the official-source parsers ([[official_source_migration]])
  are the fallback but cover ~39/50 states.
- Coverage QA is judgment-heavy; without the gap-finder, quality depends on the
  operator's diligence. The count-vs-reality check (licensed-state count per
  profession vs. a known reference) is the cheapest guardrail — bake it in.
- `match_profession` re-runs are destructive to manual additions — document loudly.
