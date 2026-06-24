# Trades — remaining work (for tomorrow, 2026-06-24 handoff)

The 4 trades are **live in prod** (https://utah-licensing.vercel.app) with the
bulk of coverage. This is the short, precise list of what's left to call them 100%.
Counts as of tonight: construction 33, electrician 38, plumbing 40, hvac 25 states.

## ⏳ IN FLIGHT tonight (verify it landed)
- Final trade rebuild (map_prep + bucket_text + build for all 4) was running, then a
  prod deploy to push the latest coverage (FL/NC/OH/GA/HI/MN/WA/OR/ND) live.
  **First thing: check the prod blob has these states + redeploy if the build/deploy
  didn't finish.** (`curl .../data/electrician.json` → rows incl FL/NC/OH/WA/OR/ND.)

## 🔴 The 3 genuine trade residuals (hard tail — not quick wins)
1. **MI construction (residential builders)** — real (MI Occupational Code Act 299,
   **Article 24, §§339.2401–2412**). Justia URL
   `.../michigan/chapter-339/statute-act-299-of-1980/article-24/` **won't pull via
   `pull_text`** (failed twice, 0–1 sections — the MI statute-act/article page has a
   structure the puller doesn't handle). Index currently `construction/MI: matched=[]`.
   → Fix: add MI statute-act/article handling to `pull_text` (like the ND blob-split /
   MD pull_md special cases), OR pull from the MI official source. 1 record.
2. **WI + WV electrician/hvac (and WV plumbing)** — licensing exists but is **buried
   in broad regs with no clean chapter**: WI under ch 101 (Dept of Safety & Prof
   Services, a huge dept chapter); WV under the contractor act / scattered. Neither
   the LLM mapper nor manual hierarchy-grep could pin a specific licensing chapter.
   → Fix: manually locate the WI/WV trade licensing sections (likely a section-range
   under ch 101 / WV ch 21 or 30) and use `section_slug_pattern` scoping (like OK/LA).
3. **66 unverified evidence nodes** (mostly NV paraphrase — correct citations,
   non-verbatim quotes; UI flags them). **Parked by decision** — not wrong facts.
   → Optional fix: re-extract the worst records (NV especially) for verbatim quotes.

## ✅ Confirmed NOT gaps (don't re-chase — verified false positives)
- **NE** (mapper keeps flagging ch 38 = *health* professions), **NY/PA/NH/TX**
  (local-only / no state GC license), **AK/ND/OR/WA hvac** (HVAC folded into the
  contractor/electrical license — not separately licensed), **MD construction**
  (home-builder *registration*, not a license — removed). SD is fine (filled=7).
  Thin records (IL/NJ construction, OH plumbing, CT hvac) are legit-short statutes.

## 🟡 Forward-looking (separate from "trades 100%")
- **Coverage expansion for the other ~64 professions**: the full LLM coverage map is
  done (`results/profession_index/_llm_candidates/*.json`, all 80 professions, ~$5).
  Per profession the loop is: review candidates → `llm_map_profession --pass2` →
  `audit_llm_candidates` (guardrail) → `apply_llm_candidates --write` → pull → extract
  → publish. See [[adding_a_new_occupation]] DX cheat-sheet.
- **MD held-out downstream**: pharmacy/psychology/chiropractic/funeral/mental_health
  MD text is pulled but never clean→trim→extract'd.
- **Grind**: currently PAUSED (paused for tonight's coverage pulls). Resume for the
  broad-capture insurance: `JUSTIA_CDP_URL=http://localhost:9222 PULL_HOST_DELAY=3
  pipeline/.venv/bin/python pipeline/results/batches/_cdp_grind.py` + caffeinate.

## ⚠️ Operational gotcha that bit us tonight
A **homebrew `python@3.14` upgrade (3.14.2→3.14.6) broke the venv mid-session**
(symlink to the removed Cellar dir), causing silent failures. Fixed by repointing
`pipeline/.venv/bin/python3.14` → `/opt/homebrew/opt/python@3.14/bin/python3.14`
(stable opt path). If pipeline commands suddenly "no such file or directory" the
venv python, that's the cause — repoint the symlink. See [[reference_concurrent_pull_corruption]].
