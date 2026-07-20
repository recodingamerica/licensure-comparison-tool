# Over-broad worklist triage — 2026-07-20

`over_broad_auto.json` listed 151 rows (~5× duplicated) → **26 unique cells**. Checked
each against the *current* committed corpus size (not the stale `leaves` count in the
worklist). Only **5 were genuinely still over-broad**; the other 21 are already
scoped/small, empty, or recorded absences from prior sessions (money_transmitter/NE,
loan_broker/NE, radiologic_technology/MA, pawnbroker/MA, EMT/LA, health_facility_admin/AZ,
landscape_architecture/NE, athlete_agent/NE, alcohol_drug_counseling/HI, etc. — the
worklist never got refreshed after those were fixed).

## The 5 that were still big — resolution

| cell | was | verdict | action |
|---|---|---|---|
| acupuncture/KY | 391 | over-broad (shared ch-311) | **SCOPED** → §§311.671–311.686 (16 secs) |
| polygraph_examiner/MA | 325 | not a license | **ABSENCE** (not_regulated) |
| athletic_training/CA | 196 | real reg, corpus incomplete | **DEFERRED** — needs a targeted fetch |
| construction_trades/CA | 333 | false positive | leave (correct chapter) |
| insurance_producer/CA | 219 | false positive | leave (correct chapter) |

### Done this session (scrape-side only, no LLM)
- **acupuncture/KY** — the corpus reused the whole 391-section ch-311 (Physicians). The
  acupuncturist licensure law is the contiguous block §§311.671–311.686. Added a
  `narrow-hand` `section_url_list` (16 URLs) to `profession_index/acupuncture.json` (the
  durable fix — a future pull fetches only those), and filtered the committed `text/` +
  re-ran deterministic `clean_text` locally to match. Both stages now = 16 sections.
- **polygraph_examiner/MA** — MA does not license polygraph examiners. The only statute,
  Mass. Gen. Laws c.149 §19B, is an employee-protection provision (bars employer
  lie-detector use), exactly the shape already recorded as an absence for DE. Added
  `MA: {basis: not_regulated}` to `verified_absences.yaml` and removed the wrong 325-section
  ch.149 (Labor) `text/`+`clean/` corpus.

### False positives — NOT over-broad, do not scope
- **construction_trades/CA** (§7000–7191) = the Contractors State License Law, the correct
  and complete chapter for the trades. Big ≠ wrong.
- **insurance_producer/CA** (§1621–1758.993) = Ch. 5 "Production Agencies," the correct
  insurance-agent licensing chapter.

### Deferred — needs a fetch (do in a clean window, not during the annual refresh)
- **athletic_training/CA** — this is a *real* regulation: CA recently enacted athletic-trainer
  **title protection** at BPC §2529.8.1 (confirmed by reading the section text). But the
  committed corpus (reused Medicine ch-5) captured only §2529.8.1 — it is missing the rest
  of the athletic-trainer article (§2529.7 definitions, §2529.8, etc.). Completing it needs
  a targeted pull of that article, which would compete with the running annual refresh's
  fetcher, so it's deferred. Next step: fetch the ch-5 index, enumerate the §2529.7–2529.9x
  article, add a `narrow-hand section_url_list`, then pull → clean.

## Note
The scrape-side fixes above leave `trimmed/`/`structured/` unbuilt for acupuncture/KY (they
were never built — these were unfinished cells). Downstream clean→trim→extract for
acupuncture/KY (and applying the two new absences via `apply_verified_absences`) belongs to
the POST-RUN pass, not done here (user scoped this to the scraping side only).
