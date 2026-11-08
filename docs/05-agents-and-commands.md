# 5. Agents & commands

## How they fit together

- **Commands (`/qa-*` skills)** run in your main Claude Code conversation. They orchestrate
  the lifecycle, ask you questions and run gates — anything that needs a human.
- **Specialist agents** are delegated the heavy analysis for a stage. They read only the
  rule files and domain slices they need (via the context loader) and return a short summary.
- **Only the sync agent writes to the work item platform.** All other agents write files in
  the repo.
- **Gate decisions are never delegated** to an agent — a tester always decides.

```
You ──/qa-start──► orchestrator (main session) ──► requirement-analyst ──► questions.md / AC
                          │                                                     │
                          ├──/qa-gate G1 ◄──────── you decide ◄─────────────────┘
                          ├──► risk-gap-analyst ──► risk, gaps, test plan ──► /qa-gate G2
                          ├──► test-designer ─────► test cases, test data
                          ├──► automation-analyst ► automation gap ─────────► /qa-gate G3
                          └──► sync-agent ────────► Azure DevOps (on gate approval)
         domain-analyst ── maintains the domain context used by all of the above
```

## Commands

| Command | What it does | When to use |
|---|---|---|
| `/qa-init [--rebaseline]` | Phase 0: workspace detection, config, domain discovery, QA reverse engineering, quality standards, prepares G0 | Once per project (or to re-baseline) |
| `/qa-domain build \| refresh \| deepen <F-id> \| ask <question> \| review \| accept … \| reject …` | Build and maintain the domain context; ask questions about the app; govern DCPs | Any time; `review` before gates when DCPs are pending |
| `/qa-start <id \| url \| aidlc-unit> [--tier …]` | Fetches the work item, converts it, picks the tier, runs stages 1.1–1.3 up to G1 | Start QA on a story/bug/feature |
| `/qa-continue [id] [--tier …]` | Reads `qa-state.md`, processes your answers, runs the next stages up to the next gate | After answering questions or approving a gate |
| `/qa-gate <G0…G5> [id]` | Builds the gate pack (checklist with evidence, open questions, pending DCPs), lets you interrogate it, records the decision, triggers sync | At each gate |
| `/qa-status [id \| --project]` | Item: tier, stages, gates, open questions, AC coverage, sync state. Project: G0, domain version, pending DCPs, stale facts, AI-DLC status | "Where are we?" |
| `/qa-sync [id] [--what ac\|tests\|gates\|all] [--check]` | Pushes artifacts to the platform on demand; `--check` reports drift | When `syncMode` isn't `on-gate`, or to re-push |
| `/qa-execute [id] [--tc …] [--set planned\|regression\|retest] [--sheet \| --ingest] [--import <file>]` | Opens a test cycle (build + environment, entry criteria), runs test cases step by step in chat or via an offline execution sheet, imports JUnit/TRX results, records `RUN-xxx` files with evidence | Phase 3, after G3 |
| `/qa-defect [id] list \| confirm \| reject \| duplicate \| defer \| accept \| refresh \| retest` | Reviews drafted defects; **you confirm** before anything is created in ADO; refreshes bug states; retests fixes | Phase 3 |
| `/qa-explore …` | *(v2 slice B)* Exploratory testing via Playwright MCP | Not yet implemented |

## Agents

### domain-analyst — *knows the application*
- **Stages:** 0.2 domain discovery (and 0.3 when delegated); lazy deepening; refresh.
- **Does:** builds glossary, roles & permissions, feature map, business rules, entities &
  state machines, journeys, integrations, environments, risk hotspots, known quirks;
  docs-led or evidence-led per feature; corroborates facts across sources; detects conflicts;
  writes the targeted interview; drafts DCPs for every change after G0.
- **Output:** `docs/qa/_project/domain/*`, `discrepancies.md`, `questions.md`, DCPs.

### requirement-analyst — *catches requirement defects early*
- **Stages:** 1.1 intake, 1.2 requirement analysis, 1.3 acceptance criteria.
- **Does:** converts the work item to the canonical model; checks completeness, ambiguity,
  consistency, testability, NFRs and alignment with the domain context; asks what it can't
  resolve; writes acceptance criteria in **Gherkin** or **rule tables** (per criterion).
- **Output:** `1-inception/requirement.md`, `requirement-analysis.md`, `acceptance-criteria.md`,
  item `questions.md`. **Gate:** G1.

### risk-gap-analyst — *decides where effort goes*
- **Stages:** 1.4 risk & impact, 1.5 gap analysis, 1.6 test strategy & plan, 2.4 observability design.
- **Does:** scores risk (impact × likelihood) and blast radius using the feature map,
  hotspots and code; finds requirement, coverage, automation, NFR, environment, domain and
  observability gaps; produces a right-sized test plan per tier; designs what to log/measure.
- **Output:** `risk-assessment.md`, `gap-analysis.md`, `test-plan.md`, `2-design/observability-plan.md`.
  **Gate:** G2 (and contributes to G3).

### test-designer — *writes traceable test cases*
- **Stages:** 2.1 test case design, 2.2 test data & environment.
- **Does:** derives test cases from approved AC using equivalence partitioning, boundary
  values, decision tables, state transitions, pairwise, permission matrices and error guessing;
  every case traces to an AC; marks cases based on provisional facts; defines data sets and
  environment/account needs (by role reference, never secrets).
- **Output:** `2-design/test-cases/*.yaml`, `test-case-index.md`, `test-data.md`. **Gate:** G3.

### automation-analyst — *finds the automation gap*
- **Stage:** 2.3 automation gap.
- **Does:** recommends the right level per test case (unit / API / contract / UI / manual /
  exploratory), scores automation value, maps to existing automated tests
  (`feature-test-map.yaml`), identifies framework gaps, proposes an automation backlog.
- **Output:** `2-design/automation-gap.md` (backlog items can become ADO tasks on sync). **Gate:** G3.

### sync-agent — *the only one that writes to Azure DevOps*
- **When:** after a gate is approved (`syncMode: on-gate`) or on `/qa-sync`.
- **Does:** dry-run first (shows what will be written), then idempotent create/update:
  acceptance criteria field, gate status tag/field, comments, requirement-based suite, test
  cases with steps, *Tested By* links; stores platform IDs and content hashes back in the repo
  files; reports drift. Overridden gates don't sync unless you ask.
- **v2:** creates **confirmed** defects only (Bug with repro steps, severity, evidence attachments,
  links to story and test cases; idempotent via a `qa-def:` tag), publishes test runs to Test Plans,
  reads defect states.
- **Never** prints or stores credentials.

### execution-analyst — *turns execution into evidence*
- **Stages:** 3.2a (cycle preparation, sheet ingestion), 3.3 (triage, defect drafting), 3.4 regression, 3.5 test summary.
- **Does:** checks entry criteria and builds the execution list; parses filled execution sheets and
  JUnit/TRX result files (`scripts/import_results.py`) into run records; classifies every failure
  (product defect, test defect, environment, data, flaky, known quirk, provisional oracle); drafts
  defects with an **oracle check** (only approved AC / confirmed rules can fail a test), known-quirk
  and duplicate checks; selects regression from the risk assessment and feature-test map; writes the
  test summary report with exit criteria computed from the runs and a GO / GO with risks / NO-GO
  recommendation.
- **Never** creates or confirms defects, and never decides G4.
- **Output:** `3-execution/runs/`, `execution-log.md`, `defects/`, `defect-log.md`, `regression.md`,
  `test-summary-report.md`. **Gate:** G4.

### exploratory-tester — *(v2)*
- **Stage:** 3.2b. Charter-based exploratory / focused testing of the web app through the
  Playwright MCP server, using the domain context as oracle, capturing evidence and proposing
  defects (with your confirmation), new test cases and DCPs. Design in
  `rules/phase-3-execution/3.2b-exploratory-playwright.md`.

## Which agent runs at which stage

| Stage | Agent | Gate |
|---|---|---|
| 0.1 Workspace detection | orchestrator (`/qa-init`) | |
| 0.2 Domain discovery | domain-analyst | |
| 0.3 QA reverse engineering | orchestrator or domain-analyst | |
| 0.4 Quality standards | orchestrator | **G0 QA Baseline** |
| 1.1–1.3 Intake, analysis, AC | requirement-analyst | **G1 Ready for Test Design** |
| 1.4–1.6 Risk, gaps, plan | risk-gap-analyst | **G2 Test Plan Approved** |
| 2.1–2.2 Test cases, data | test-designer | |
| 2.3 Automation gap | automation-analyst | |
| 2.4 Observability design | risk-gap-analyst | **G3 Test Design Approved** |
| Sync after any gate | sync-agent | |
| 3.1 Automation implementation | v4 (non-blocking stub) | |
| 3.2a Manual execution | you, via `/qa-execute` (execution-analyst prepares/ingests) | |
| 3.2b Exploratory | exploratory-tester (v2 slice B) | |
| 3.3 Defects | execution-analyst drafts → **you confirm** (`/qa-defect`) → sync-agent creates | |
| 3.4 Regression | execution-analyst + you (run/import) | |
| 3.5 Test summary | execution-analyst | **G4 Quality Sign-off** |
| 4.x Operations | v4 | G5 (v4) |

Not every stage runs for every item — the tier decides (`core/routing-rules.md`):

| Tier | Typical items | Runs |
|---|---|---|
| Light | Bugs, hotfixes | 1.1, lite 1.2–1.3, **G1**, 2.1, **G3** (no risk/gap/plan, no G2) |
| Standard | User stories | All of Phase 1 (one-page plan), **G1–G3**; 2.2 and 2.4 only if needed |
| Comprehensive | Epics, features, payments/PII/security | Everything, full plan, blast radius |

Items touching a risk hotspot, a critical business rule or > 3 integrations are escalated one
tier automatically. Going down a tier is only ever by your explicit `--tier` override.
