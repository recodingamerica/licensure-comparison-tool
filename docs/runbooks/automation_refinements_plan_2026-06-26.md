# Automation arc — state + refinement plan (2026-06-26, survives /clear)

## What we built this arc (all committed to data/pull-all + main)
A self-improving "add/maintain occupations" loop, grounded only in our own text:

| Tool | File | One-liner |
|---|---|---|
| **discover_occupations** | `pipeline/discover/discover_occupations.py` | LLM reads each state's chapter structure → untracked occupations, flags ones hidden inside another act. Output: `results/discover_occupations/_candidates.json` (**781 found, 265 nested**). |
| **parent_corpus** | `pipeline/ingest/clean_text.py::corpus_profession_for` | a nested occupation with `parent_corpus: <parent>` in professions.yaml reads `text/<parent>/` — **no new Justia pull**. |
| **register_occupation** | `pipeline/discover/register_occupation.py` | auto-drafts a professions.yaml entry from a name; self-validates parent_corpus against real text. |
| **add_occupation** | `pipeline/discover/add_occupation.py` | **one command**: register → clean → trim → discover_schema → extract → [--publish] map_prep/build. Validated on dental_assistant. |
| **gap_loop** | `pipeline/discover/gap_loop.py` | audits each EMPTY field against OUR text → `answerable_missed` (re-extract) / `not_in_text` (corpus wishlist + likely_source) / `genuinely_na`. `summary` rolls it up. |
| **pull_regulations** | `pipeline/ingest/pull_regulations.py` | pulls admin rules (official SPA via CDP render-with-wait) as a supplementary source. |

**Key findings:**
- The gap_loop (self-grounded) showed a systematic class of empty fields (CE hours, pharmacology, CPR/BLS, record retention, jurisprudence) lives in the **administrative RULES**, not the statute. `regulations.justia.com` is **title-only** — the official state SPA (e.g. adminrules.utah.gov) has the full text, rendered via our CDP Chrome + a wait-for-content.
- **End-to-end POC proven:** pulled UT optometry R156-16a → merged → re-extract → `pharmacology_training_hours_required = 100` filled, cited to R156-16a-302a (was absent).
- Demo occupations registered (WIP, not core/published): `dental_hygienist` (UT extracted, hygienist-correct), `dental_assistant` (UT/CA/NY).

See also: `docs/runbooks/automation_handoff_assessment.md` (the stage-by-stage "what's hands-off" doc).

## Refinements — prioritized (the resume list)
1. **pull_regulations section-split robustness** (highest — it's what makes admin-rules reliable). POC filled pharmacology but MISSED CE-hours/CPR — `split_sections` / the SPA render didn't capture R156-16a-304's body. Fix the section boundary detection + confirm all sections' text renders (poll longer / per-section nav). Re-run the optometry-UT POC and confirm CE-hours (30) fills.
2. **Clean supplementary-merge wiring** — make regulations a proper supplementary source like `umbrella_text` (build_frontend/extract already merge umbrella), NOT the manual append used in the POC.
3. **Per-(profession, state) rule mapping** — today the admin-rule URL (R156-16a) is hardcoded. Needs discovery: map each profession→admin-rule-number per state (LLM over the regulations index, like `llm_map_profession`). Each state's admin-rule system differs (official-source-migration-style work).
4. **Validate discovery precision** — the 781 candidates have visible noise (Attorney, Notary). Spot-check a sample vs OPLR's actual occupation list; tighten the discover prompt.
5. **Wire gap_loop's re-extract action** — `answerable_missed` fields (e.g. optometry NY missed laser_procedures) → auto targeted re-extract, capped rounds.
6. **Bulk discover→process** — run `add_occupation` over the top-N nested candidates (Hygienist, Barber, Esthetician, Pharmacy Tech, Vet Tech…) for near-free coverage (no Justia).

## Operational state (for resume)
- **Grind:** running (resumed), **~88.4%**, ~35/73 professions complete. caffeinate ON. Resume cmd if it dies: `JUSTIA_CDP_URL=http://127.0.0.1:9222 PULL_HOST_DELAY=3 pipeline/.venv/bin/python pipeline/results/batches/_cdp_grind.py >> pipeline/results/batches/_cdp_grind.log 2>&1 &`
- **Debug Chrome:** open on :9222 (profile `$HOME/chrome-justia-debug`). Relaunch if closed: `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222 --user-data-dir="$HOME/chrome-justia-debug" &`. **Use `127.0.0.1:9222` not `localhost`** (IPv6/::1 connect fails). After many rapid CDP connects it can wedge (`setDownloadBehavior … not supported`) → kill+relaunch Chrome fixes it.
- **Deploys:** prod (utah-licensing.vercel.app) is current with the Novel-policies tab, Architects+Engineers, harmonization, build_state_browse perf fix. The automation tools above are pipeline-side (not deployed).
- **Branch:** work on `data/pull-all`; `main` is fast-forwarded to match after each push.

## Resume in one line
Start at refinement #1: harden `pull_regulations.split_sections` + the SPA render so all rule sections' text is captured, then re-run the UT-optometry merge POC and confirm CE-hours fills. Then #2 (clean merge wiring) and #3 (rule mapping).
