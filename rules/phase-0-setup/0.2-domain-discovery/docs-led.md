# Domain Discovery — Docs-led (Scenario A: requirement documents exist)

**Principle:** documents lead, evidence verifies.

## Steps

1. **Ingest documents** listed in `domain.discovery.sources.docs` (+ AI-DLC artifacts if mapped):
   BRDs, SRS, functional specs, wiki pages, user manuals, AC on epics/stories.
   - Record each document: path/URL, title, version/date, last modified.
   - **Version check:** if several versions of the same spec exist, ask which is current
     (one question). Flag docs older than the most recent significant code change
     in the related area as `possibly-outdated`.
2. **Extract facts** → glossary terms, roles & permissions, features, business rules,
   journeys, entities/states, NFR statements. Status `documented`, `verified: false`.
   Quote the source sentence in `sources[].quote` (short).
3. **Cross-verify** each documented fact against evidence (see `evidence-led.md` §2 for
   where to look): validators, error messages, tests, permissions, schema, (v2) live app.
4. **Classify:**

| Result | Action |
|---|---|
| Doc and evidence agree | `verified: true`, confidence per `corroboration.md` |
| Doc only (no evidence found) | `verified: false`; DISC entry: "not implemented, or doc wrong?" |
| Evidence only (not in docs) | add as `observed` fact; flag "undocumented behaviour" |
| Doc and evidence conflict | `status: disputed`; DISC entry + targeted question |

5. **Fill detail gaps.** Docs usually describe happy paths. Mine edge-case rules
   (limits, validations, error handling) from evidence as `observed` facts.
6. **Questions:** only for discrepancies and version ambiguity — do not re-ask things the
   docs state clearly and the evidence confirms.

## Pitfalls
- Treating an aspirational doc ("phase 2 will support…") as current behaviour → check tense
  and roadmap language; tag `future` and exclude from oracles.
- Several docs contradicting each other → `disputed`, single question listing all sources.
