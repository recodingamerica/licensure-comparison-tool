# Silent / Silent-ish Caps Audit — 2026-07-01

Scope: every `.py` under `pipeline/` except `.venv/`, `results/batches/`,
`publish/web/`. 99 files examined. Grepped for slice truncations, `MAX_`,
`_CAP`, `limit`, `depth`, `truncat`, `sample`, `head(`, `break` in loops,
`.pop` inside enumeration.

---

## Category A — Silent Data Loss

These truncations drop source data with **no loud warning and no record in the
output artifact**.

| # | File : line | Literal / constant | What it silently drops | Fix recommendation |
|---|---|---|---|---|
| A1 | `ingest/trim_state.py:48,104` | `SECTION_TEXT_CAP = 6000` → `text[:SECTION_TEXT_CAP]` | Any section whose statute text exceeds 6 000 chars is silently shortened before the keep/drop LLM sees it. The trimmed corpus is then written with the FULL text (read verbatim from `clean/`), so only the LLM's input is cut — but if the decisive language is in chars 6001+, the LLM may wrongly **drop** a section that should be kept, causing that section to vanish from `trimmed/` and never reach extraction. No field in the output artifact records that the LLM was shown a truncated view. | Raise the cap to match typical LLM context (≥30k chars). If a single section genuinely dwarfs that, log a loud WARNING with the citation and char count, and keep the section unconditionally (or add `trim_degraded`-style flag to the trimmed corpus). Either way, add a `"shown_truncated": True` key per affected section in the trimmed output so downstream can audit it. |
| A2 | `discover/suggest_scope_rules.py:66,389-390` | `MAX_TEXT_PER_SECTION = 2000` → `text[:MAX_TEXT_PER_SECTION]` | The anchor-section text sent to the LLM that proposes umbrella scope rules is silently cut at 2 000 chars. No record in the generated `_RULES` code or in any artifact that the prompt was truncated. If an applicability clause appears after char 2 000, the LLM proposes wrong/incomplete scope regexes. | Same approach: raise or remove the cap; add `[…truncated at 2000 chars]` marker; since this is a tool-output LLM call (no stored artifact), at minimum log a WARNING with the section citation and how many chars were cut. |
| A3 | `discover/suggest_scope_rules.py:68,619-622` | `MAX_TEXT_PER_UNDET = 500`; `result[:MAX_UNDET_IN_REFINEMENT]` (10) | The refinement pass caps (a) each undetermined section's text at 500 chars and (b) the number of sections sent to refinement at 10. If there are >10 undetermined sections, the 11th onward are never reconsidered and stay `undetermined` — silently excluded from scope assignment. No artifact records which sections were dropped from the refinement call. | Log which sections were excluded from refinement; write the full list of undetermined URLs that were skipped into the LLM-scope output file so the operator can judge/rerun. Raise the text cap or rely on the model context window. |
| A4 | `discover/audit_corpus.py:48,111,114-122` | `MAX_CHARS = 30000`; `index[:6000]`; body budget cuts | `_corpus_sample` sends at most 30k chars to the LLM that verdicts corpus correctness. The strided sampler stops adding sections once `used + chunk > budget`. For very large corpora, later sections (which may be the profession's OWN chapter, sorted after a big umbrella chapter) are silently omitted from the sample. The audit writes a verdict to `corpus_audit/<profession>.json` that could be wrong without any note that the corpus was truncated. | Add `n_sections_sampled` / `n_sections_total` fields to the verdict JSON, and include a `sample_truncated: true` flag when the budget ran out before all sections were covered. Log it visibly per state. |
| A5 | `extract/discover_schema.py:152-168` | `--max-states 10` default; `states[:args.max_states]` | Schema discovery only feeds the first N alphabetical states to the LLM. States outside the sample are permanently excluded from informing the schema — any profession-specific field that only appears in states AL/AZ/CA/CO/CT/DE/FL/GA/HI/IA (the first 10 alphabetically) is discoverable, but fields found exclusively in WY or WI are invisible. The generated `discovered/<profession>.json` carries `states_supporting` lists that look complete but are actually alphabet-gated. No field in the artifact records which states were excluded from schema discovery. | Add a `states_sampled` / `states_excluded` list to the discovered JSON. Log the excluded states at WARNING level. Long-term: sample randomly or representatively rather than alphabetically, or raise the default. |
| A6 | `analyze/gen_semantics.py:73` | `sorted(vs)[:12]` | When building the field-inventory for the LLM that assigns `importance` and `closeness_kind`, observed values are capped at 12 per field. For fields with >12 distinct values the LLM proposes `order` lists based on an incomplete value set; unusual values from the tail will be absent from the `order` list in `field_semantics/<profession>.yaml`, causing them to be treated as unknown in similarity scoring. No record in the artifact of the cap. | Log a WARNING if `len(vs) > 12` for any field. Include the full value count in the `inv` entry so the LLM can note the truncation, or raise the cap (12 values × short strings is a tiny input). |

---

## Category B — Loud / Flagged (but log-only, no artifact record)

These truncations are not silent — they log a warning — but they do **not**
record the truncation in the output file, so a downstream reader of the
artifact cannot tell it was affected.

| File : line | Literal | Behaviour | Gap |
|---|---|---|---|
| `ingest/pull_text.py:1934-1940` + `ingest/pull_all.py:155-160` | `section_cap = args.limit_sections` | When `--limit-sections N` is passed and a state hits the cap, the corpus **is** written and a loud `log.warning` fires. `capped_states` is printed at the end. But the written corpus file (`text/<profession>/<STATE>.json`) contains **no flag** that it was capped. A reader of the file (or a downstream `clean→trim→extract` run) cannot tell the corpus is truncated. | Add `"section_cap_hit": true` and `"section_cap": N` to the corpus JSON so downstream stages and the `corpus_status` tool can detect this automatically. |
| `ingest/pull_text.py:1776-1791` (Justia per-section path) | same `limit_sections` guard | Same issue — the warning fires but no artifact field records the cap. | Same fix as above. |
| `discover/audit_corpus.py:176` | `reason[:90]` | The audit log truncates the reason string at 90 chars. The written `corpus_audit/<profession>.json` contains the full reason, so this is display-layer only. | Cat. C, not B — no data loss. Listed for completeness. |

---

## Category C — Legitimate Mechanics

All confirmed-safe: batching chunk sizes, LLM retry counts, pagination,
display-layer top-Ns, detection thresholds that only flag, and label-truncation
for console/log readability.

| File : line | Literal | Why it's safe |
|---|---|---|
| `_batch.py:22,61,92` / `_llm.py:14,146` | `max_tokens=16000` etc. | LLM **output** token limits. Don't drop source data; only constrain model response length. |
| `_llm.py:148` | `max_retries=2` | Retry mechanic. |
| `discover/expand_containers.py:106` | `out[:5000]` | Container children list. Comment documents the prior `[:300]` was the problem; 5 000 is a pragmatic safeguard against malformed pages returning thousands of spurious links. Not a corpus-completeness decision. |
| `discover/expand_containers.py:73-85` | `max_depth=2` | Controls how many levels of Justia hierarchy to recurse. Documented; operator-settable via `--max-depth`. What's below depth 2 is unknown-unknown territory, not silently dropped data that was known to exist. |
| `ingest/pull_text.py:1490,1507` | `max_depth=2` in `collect_section_targets` | Same — section-target recursion depth. |
| `discover/llm_scope_fallback.py:66,229-230` | `MAX_SECTIONS_PER_CALL=12`; `batch = secs[i:i+12]` | Batching mechanic — all sections are processed across batches; nothing is dropped. |
| `discover/llm_scope_fallback.py:65,182` | `MAX_TEXT_PER_SECTION=2000` | Text cap for scope-classification LLM only; the full text is already stored on disk. The scope metadata (classification) is what's affected, not the corpus. A separate concern from trim_state (where a wrong drop removes the section from the pipeline). Borderline B, but classified C because the underlying text is preserved on disk. |
| `discover/umbrella_from_citations.py:86,140-143` | `min_profs=3`, `min_refs=5` defaults | Selection thresholds that **flag** chapters as umbrella candidates. Chapters below the threshold are excluded from the umbrella pull list, but they're not data we've ever pulled — they're candidates. Operator-tunable. |
| `eval/corpus_status.py:243,274,377,381` | `min_refs=5`, `min_profs` | Same — detection thresholds only. |
| `ingest/trim_state.py:49` | `MAX_RETRIES=2` | Retry count. |
| `discover/migrate_mapping_overrides.py:59` | `MAX_ADDS=310` | Sanity-check gate that aborts migration if the add count is out of expected range. Not a data-drop; a correctness guard. |
| `map_prep/bucket_text.py:177,355,365` | `str(v)[:600]`, `item.strip()[:80]`, `desc[:400]` | Raw values stored in the map_prep intermediate files for LLM bucketing. The full structured value is in `structured/<profession>/`. These truncations only affect what's sent to the harmonization LLM; they don't affect what's stored in or published from the corpus. |
| `map_prep/harmonize_universal.py:129` | `str(raw)[:600]` | Same as above. |
| `analyze/similarity.py:214,240,251,270` | `MAX_NOVEL_STATES=15` | Cap on how many states appear in the Compare-tab novel-policies list. Display-layer; the underlying structured data is unaffected. |
| `analyze/similarity.py:535-536,549-550,569,599,602,605,607` | `[:6]`, `[:8]`, `[:3]`, `[:2]`, `[:5]`, `[:6]` | Display-layer top-N for notes, neighbors, drivers in the similarity JSON. The full `scored`, `distinctiveness`, etc. arrays are written to the JSON; these slice only the CLI debug printout and prose notes. |
| `publish/state_similarity.py:126,129,176` | `[:5]`, `[:3]`, `[:3]` | Report-only top-N display. |
| `discover/harvest_occupations.py:238,242,247,255` | `[:8]`, `[:3]`, `[:25]`, `[:40]` | Console display truncations. Output files (`candidates.json`, `variants.json`, `plural_candidates.json`) get the full data. |
| `extract/discover_schema.py:137-138` | `[:8]` in `states_str` | Markdown preview display only; the full `states_supporting` list is in the JSON. |
| `publish/build_tag_sheet.py:207` | `words[:1].upper()` | First char capitalisation — not truncation. |
| `publish/build_frontend.py:501,891` | `[:60]`, `[:3]` | Label truncation for display fields only; full text is in the sections array. |
| `publish/_browse_tree.py:155` | `[:60]` | Fallback slug construction for orphan sections. Display label only. |
| `publish/db/load.py:172,200` | `[:60]` | DB slug construction from label as fallback. |
| `publish/generate_field_dictionary.py:45,102,104` | `MAX_DEPTH=3` | JSON schema introspection depth. Only affects the field dictionary display; not the underlying data. |
| `publish/generate_field_dictionary.py:147,197` | `[:200]`, `[:60]` | Quote/value display truncation in field dictionary only. |
| `_batch.py:117,176,183` / `_llm.py:68,212,215,219` | `str(e)[:120]` etc. | Error message display truncation in log lines. |
| `eval/corpus_status.py:388` | `profs[:5]` | Display-only in CLI output. |
| `discover/audit_corpus.py:86` | `pats[:4]` | Display label only. |
| `ingest/pull_regulations.py:83` | `secs[:6]` | Sample print of first 6 sections for CLI sanity check. |
| `discover/match_sections.py:182,207,235` | `[:70]`, `[:60]`, `[:70]` | Console display truncation. |
| `ingest/pull_all.py:229` | `reason[:90]` | Log line display only. |
| `discover/llm_scope_fallback.py:357-358` | `[:60]`, `[:80]` | Log display. |
| `ingest/pull_text.py:400,479,689,805,844` etc. | `[:300]`, `[:200]` etc. | Label extraction: these build the `label` field of a `Section` object from the first N chars of the section heading/first-line. The label is metadata; the full `text` field is stored separately and is not truncated. |
| `analyze/classify_novel_direction.py:95` | `(quote or '')[:400]` | Log display only. |
| `discover/assign_umbrella_scope.py:290` | `ev or tail[:160].strip()` | Fallback evidence snippet stored per scope entry — an informational field, not the corpus text. |
| `ingest/pull_regulations.py:62,68` | `[:120]`, `[:80]` | Log / dedup key construction for regulations puller. |
| `discover/umbrella_from_citations.py:157` | `top['label'][:38]` | Console display only. |
| `discover/expand_containers.py:105` | `lab[:140]` | Label field of hierarchy node, not corpus text. |
| `publish/build_gap_matrix.py:91` | `val_str[:200]`, `quote[:200]` | Gap matrix display fields; full structured record exists in `structured/`. |
| `publish/refresh_all.py:128` | `str(e)[:120]` | Error log display. |
| `ingest/pull_umbrella_text.py:189-193` | `len(section_targets) > 100` warning | Explicitly NOT a cap — the comment documents this. Pulls all sections and logs loudly when count > 100. Cat. C. |

---

## Prioritized Category-A Fix List

Ordered by severity (potential for invisible bad decisions that corrupt stored
data or published output):

1. **A1 — `trim_state.py` `SECTION_TEXT_CAP = 6000`** (CRITICAL)
   The trim LLM decides keep/drop for every section. If a section's operative
   licensing language is after char 6 000, the LLM may drop it. That section
   then disappears permanently from `trimmed/` and never reaches extraction.
   This is the same class of bug as the `MAX_SECTIONS_PER_CHAPTER = 50`
   umbrella truncation (invisible months of data loss). Fix first.

2. **A5 — `discover_schema.py` `--max-states 10` (alphabetical)** (HIGH)
   Schema discovery affects every subsequent extraction for the profession.
   Fields that only appear in states starting with letters N–W are invisible
   to the schema, so the extraction model is never asked to find them. The
   `states_supporting` lists in the artifact look complete but are
   alphabet-gated. Fix: add `states_sampled` / `states_excluded` to the
   artifact; sample randomly or raise the default.

3. **A4 — `audit_corpus.py` `MAX_CHARS = 30000` sample** (HIGH)
   A wrong `correct_licensure_text` verdict (because the profession's chapter
   was past the budget) silently certifies a bad corpus, blocking re-discovery.
   Fix: add `n_sections_sampled` / `n_sections_total` and `sample_truncated`
   to the verdict JSON.

4. **A3 — `suggest_scope_rules.py` `MAX_UNDET_IN_REFINEMENT = 10`** (MEDIUM)
   Sections beyond 10 stay `undetermined` permanently. `undetermined` sections
   are excluded from injection into the extraction prompt
   (`load_umbrella_text`), so their law is invisible to the extractor. Fix:
   record skipped URLs in the LLM-scope output file.

5. **A6 — `gen_semantics.py` `sorted(vs)[:12]`** (MEDIUM)
   Rare values missing from the `order` list in `field_semantics/` are treated
   as unknown by similarity scoring, degrading state comparisons for professions
   with rich enum fields. Fix: log a WARNING; raise or remove the cap.

6. **A2 — `suggest_scope_rules.py` `MAX_TEXT_PER_SECTION = 2000`** (LOW-MEDIUM)
   This only affects the scope-rules code generation tool (run rarely,
   human-reviewed). But wrong regex proposals propagate into
   `_scope_rules.py` silently. Fix: raise to ≥ 6 000 chars; log WARNING
   when section text is cut.

---

## Counts

| Category | Count |
|---|---|
| A — Silent Data Loss | 6 |
| B — Loud/logged but no artifact record | 2 |
| C — Legitimate mechanics | ~50 |
