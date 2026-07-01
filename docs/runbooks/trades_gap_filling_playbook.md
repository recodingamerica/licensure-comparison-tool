# Trades gap-filling playbook (#53)

How we turned the "trade licensing gaps" from an unfillable blob into a tractable,
mostly-mechanical pipeline. Written 2026-06-29/30. Trades = hvac, electrician,
plumbing, architecture (held-out professions; same methods apply to any occupation).

## The core finding

Most "gaps" (states where the scrape returns blank) are **false negatives, not
absences** — the license exists but lives somewhere our title-keyword matcher
didn't look. Atharv's gap-analysis called this; we confirmed and quantified it.
The failure modes, in rough order of frequency:

1. **Number-labeled articles.** Some states' occupational codes label articles by
   number only — MI Occupational Code "Article 20" *is* the Architects board, but
   the label says "Article 20", so keyword matching is blind to it.
2. **Folded into one contractor chapter.** TN licenses electricians ("Limited
   Licensed Electrician") and plumbers *as contractor classifications* under Title
   62 Ch 6 — no separate chapter. The contractor corpus already covers them.
3. **Buried in a giant container title.** NE's Engineers & Architects Regulation
   Act is §81-3401+ inside the 2,576-section chapter-81 (a state-government title).
4. **Wrong title entirely.** The trade is under Labor / Public Health & Safety /
   Fire Protection, not "Professions & Occupations".
5. **Genuine local-only nulls.** Electricians/plumbers in IL/IN/NY/PA are licensed
   only by cities — correct to be blank. DO NOT manufacture a state license here.

## The LLM tools (and their failure modes)

- `discover/audit_corpus.py` — the post-pull gate. Verdicts whether a pulled corpus
  IS the occupation's licensing law. **Wired into `pull_all --gate`.** It caught the
  egg-refrigeration and architects-instead-of-hvac mis-pulls live. NOTE its sampler
  was once truncation-biased (only saw the corpus head) — fixed to sample
  representatively (full citation index + strided text). Any audit that truncates
  must sample representatively, or it flags whatever sorts first.

## These lessons are encoded in code, not just here

Prefer running the tool over re-deriving the technique:
- `discover/mechanical_cross_ref.py` — the keyword-density sibling cross-ref (#3 below),
  as a CLI. `--all-trades [--apply]`. LLM-free; catches what the LLM cross-ref refuses.
- `discover/probe_justia.py` — the CDP structure-poke (#1 below) as a reusable tool:
  `--url <U> --links [--match REGEX]` to read structure, `--url <U> --text` to confirm
  what a number-labeled article actually is. Bakes in suppress_origin + the year-prefix
  + the don't-run-during-a-harvest caveat.
- `ingest/pull_all.py --limit-sections` — the runaway guard (#4), defaults to 500 + flags.
- `discover/audit_corpus.py` — the representative-sampling gate (don't head-truncate).
- `discover/verify_gap_states.py` — the skeptical sonnet verifier (licensed vs local-null).

## The LLM-FREE techniques (what to do when the API is capped)

Pulling, cleaning, and `build_frontend` are LLM-free; only trim/extract/map_prep/the
LLM mappers need the API. So you can do ALL the slow CDP discovery + pull work
during an API outage and leave only trim/extract for later.

### 1. Poke Justia structure over CDP (find chapters the tools miss)
Attach to the hand-started Chrome (CDP :9222) and read the page DOM. The articles
are often number-labeled, so READ THE TEXT to confirm (e.g. navigate to MI Art 20,
confirm §339.2002 "Boards of Architects…"). Connect with `suppress_origin=True`
(the CDP origin guard 403s otherwise):
```python
import websocket, json, urllib.request
page = next(t for t in json.load(urllib.request.urlopen("http://localhost:9222/json")) if t["type"]=="page")
ws = websocket.create_connection(page["webSocketDebuggerUrl"], suppress_origin=True)
# Page.enable; Runtime.enable; Page.navigate {url}; sleep; Runtime.evaluate {expression: querySelectorAll('a')…}
```

### 2. Section-scope inside a runaway title (don't pull the whole 2,576-section title)
Add the container chapter to the profession_index with a `section_slug_pattern` that
matches only the trade's section range. pull_text fetches the chapter index, filters
to the pattern, then fetches only those bodies:
```json
{"url": ".../nebraska/chapter-81/", "section_slug_pattern": "^statute-81-34",
 "label": "NE 81-34xx — Engineers & Architects Regulation Act (section-scoped)"}
```
NE architecture: 2,576 → 57 sections. NE electrician: `^statute-81-21` (State
Electrical Act). Find the range first via the CDP poke (#1).

### 3. Mechanical keyword-density cross-ref (LLM-free sibling reuse)
When a sibling `construction_trades/<state>` corpus exists, grep it for the trade's
licensing terms. High density = it covers the trade → wire `corpus_overrides.yaml`
`{trade: {STATE: construction_trades}}`. This caught TN electrician (83 mentions) +
plumbing (94) that the LLM cross-ref refused. Threshold ~8 licensing-term mentions.

`discover/mechanical_cross_ref.py` has two modes:
- **CONFIG mode** (default) — hand-curated licensing phrases + curated sibling pool.
  `--profession electrician [--apply]`, `--all-trades`, `--all`.
- **Brute-force** (`--brute-force`) — no CONFIG: uses the occupation's
  `professions.yaml` patterns and scans EVERY pulled corpus, picking the densest
  sibling per blank state. Finds shared boards nobody configured. Output is a
  review CANDIDATE (best-match, dry-run); `--min-score` tunes the threshold.
- **`--all-brute`** — brute-forces every incomplete occupation and writes a review
  worklist to `results/brute_force_candidates.md` (report-only; 209 candidates as
  of 2026-06-30). Use it as the July-1 head-start: review the worklist, then
  `--profession X --brute-force --apply` the confirmed ones. Eyeball each — a broad
  umbrella title scores high without being the right scoped chapter (e.g.
  `court_reporter ← architecture` was a co-located NH title, not a real link).

### 4. The runaway guard
Both `pull_all --limit-sections` and `pull_text --limit-sections` default to 500: a
whole-title over-match is capped + **loudly flagged** (capped_states), never silently
trusted. (`pull_text`'s default was added 2026-06-30 — it used to be `None`, so a
hand-pull could silently grab a 2,576-section title.) Pass `--limit-sections 0` to
disable. Still prefer section-scoping (#2) when you know the range.

## Operational gotchas (burned in, do not relearn)

- **`setsid` does not exist on macOS.** Use `caffeinate -i -s <cmd>` to keep the Mac
  awake + the CDP head-browser alive for an unattended harvest. See
  `reference_unattended_cdp_harvest` memory.
- **Don't run a heavy `build_frontend` (40MB payload + 50-state browse regen)
  concurrently with a CDP harvest** — resource contention silently killed the pull once.
- **Don't kill a "stuck" pull on no output.** pull_text buffers per-section output;
  run with `python -u` / `PYTHONUNBUFFERED=1` and check the live CDP tab URL — if it's
  advancing through the right sections, it's working, just quiet. (Killed a working
  NE pull this way.)
- **NH's Justia code is YEAR-PREFIXED** (`/codes/new-hampshire/2025/title-xxx/…`),
  unlike most states — un-prefixed URL guesses 404 to a login page. When a state's
  index "has no links", dump ALL `/codes/<state>/` hrefs first to learn its URL shape
  (NH listed only year folders). NH architecture = Title XXX Ch 310-A (joint
  Engineers/Architects/Surveyors board, 235 secs — trim scopes it to architecture).

## The finish (when the API is back)
1. Manually confirm the remaining licensed-but-uncovered states vs. the statute index.
2. Pull the confirmed state_licensed ones (CDP + caffeinate + section-scope/cap).
3. `clean → trim → extract` everything pulled/wired; `pull_all --gate` validates.
4. Mark the confirmed local-only states as correct-blanks (with the chapter-absence
   as evidence).

See also: `project_issues_52_53`, `reference_unattended_cdp_harvest`,
`reference_wa_duplicate_key_bug` (memory); commits 4a1fb0d, 740b263, 39b10bc,
d363197, 9146020, 29d2c60, b456603.
