# 4. Running on an existing project

An existing (brownfield) project already has code, maybe tests, maybe documents, and
certainly knowledge in people's heads. QA Trust Architect first **learns the application**
(domain context), then **inventories the QA you already have**, and only then starts on new
work items.

## Overview

```
/qa-init
  0.1 Workspace detection ─ stack, tests, CI, platform, docs coverage, AI-DLC
  0.2 Domain discovery ──── skeleton for ALL features (cheap)
                            deep for top-risk / top-usage features
                            per feature: docs-led  OR  evidence-led
                            → targeted interview questions
  0.3 QA reverse engineering ─ existing tests ↔ features, coverage gaps
  0.4 Quality standards
/qa-gate G0  → domain version 1.0.0
/qa-start <id> → remaining features are deepened lazily, when a work item touches them
```

You don't have to learn the whole app up-front: **skeleton everywhere, depth where it
matters, the rest on demand**.

## Scenario A — the project has requirement documents

Set (or leave `auto` to choose per feature):

```yaml
domain:
  discovery:
    mode: docs-led
    sources:
      docs: ["docs/**/*.md", "requirements/**", "specs/**"]   # point at your docs
```

How it works:
1. Documents are read and facts extracted with `status: documented`.
2. Each documented fact is **checked against evidence** — code, tests, data model, tracker
   history. Matching evidence → `verified: true`, higher confidence.
3. Where docs and code disagree, nothing is silently chosen: the conflict goes to
   `discrepancies.md` with a question for you ("Docs say 20 days max, code enforces 25 —
   which is right?").
4. Features with no document fall back to evidence-led (Scenario B).

Tips:
- Docs in Confluence/SharePoint/Word? Export them (Markdown or PDF) into a folder in the repo,
  or a temporary folder, and add it to `sources.docs`.
- Old documents are still useful — conflicts with the code are exactly the things worth testing.

## Scenario B — no written requirements

```yaml
domain:
  discovery:
    mode: evidence-led
    sources: { tests: true, code: true, dataModel: true, trackerHistory: { lookbackMonths: 12 } }
```

How it works:
1. Behaviour is reconstructed from **evidence**: validation logic, error messages, UI labels,
   role/permission checks, state enums and transitions, existing tests, API contracts, and
   closed bugs/stories in the tracker.
2. Each fact gets `status: observed` (seen in code/tests) or `inferred` (deduced), with
   sources and a confidence level. **High confidence needs ≥ 2 independent sources**
   (`corroboration.highConfidence`).
3. Uncertain or high-impact facts become a **targeted interview** in `questions.md` — at most
   ~20 questions, highest impact first, multiple choice with a suggested answer. Answering
   turns facts into `confirmed`.
4. **Optional live crawl** (`sources.liveApp: true`, or `/qa-domain crawl` any time): the AI
   browses the running test environment per role through Playwright MCP — read-only, you log in —
   and maps pages, navigation and what each role can see. Results arrive as DCPs; permissions seen
   this way are recorded as *observed*, never confirmed.

> **Important:** code tells you what the system *does*, not what it *should* do.
> Observed/inferred facts can guide testing, but only **confirmed** (or verified documented)
> facts can be the oracle that decides a test has failed.

## Scenario C — the project uses AWS AI-DLC

Detected automatically when `aidlc-docs/aidlc-state.md` (or AI-DLC rule files) exist.
Companion mode (MVP):

- **Read-only** — never edits `aidlc-docs/` or AI-DLC's state/audit files.
- AI-DLC reverse-engineering outputs, requirements, stories and designs are used as
  documentation → those features are discovered **docs-led**.
- A QA work item can be an AI-DLC **unit** (`integrations.aidlc.keyBy: unit`, layout
  `{intent}/{unit}/`) or a tracker work item linked to units (`keyBy: workItem`).
- QA stages wait for their AI-DLC prerequisite (e.g. AC design after AI-DLC stories); you can
  proceed anyway — it's advisory and logged.
- When AI-DLC artifacts change, Domain Change Proposals are raised automatically.

If your AI-DLC layout differs, adjust the glob patterns in `integrations/aidlc/mapping.yaml`.

## Stage 0.3 — what you get about your existing tests

- `qa-baseline.md`: test inventory by type (unit/API/UI/manual), frameworks, CI execution,
  flaky/disabled tests, obvious gaps.
- `feature-test-map.yaml`: which tests cover which feature — used later by impact analysis,
  regression selection and the automation gap stage.

## Keeping the domain up to date

After G0 the domain context only changes through **Domain Change Proposals (DCPs)**:

| Command | Use |
|---|---|
| `/qa-domain refresh` | Re-scan for changes (code, docs, AI-DLC) and staleness; raise DCPs |
| `/qa-domain deepen F-<id>` | Deepen one feature now instead of waiting for a work item |
| `/qa-domain crawl [--env test] [--role all]` | Re-map pages per role from the running app (new screens → DCPs) |
| `/qa-domain review` | Walk through pending DCPs |
| `/qa-domain accept <ids \| all-auto \| all>` / `reject <id> <reason>` | Decide |

Review level per DCP is set by `domain.proposals`: *auto* (e.g. page lists, code links),
*review* (glossary, journeys…), *critical* (business rules, permissions, states — may require a
named owner via `domain.owners`). Accepting bumps the domain version and flags artifacts that
relied on the changed facts. A direct edit to a domain file after G0 triggers a guard prompt —
accepting a DCP opens a short apply window so the normal route is never interrupted.

## Practical adoption plan

1. **Pilot on one area** — run `/qa-init`, but pick 1–2 features for deep discovery.
2. **Answer the interview** with a BA/PO/senior dev in the room — 30–60 minutes typically
   settles most questions.
3. **Approve G0 with risks** if needed — gates are advisory; record what's still uncertain.
4. **Take 2–3 real stories** through `/qa-start` → G1 → G2 → G3.
5. Tune `qa-trust.config.yaml` (tiers, layout, approvers) and `quality-standards.md`, then roll
   out to the team.
