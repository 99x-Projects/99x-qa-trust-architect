# Core Workflow — QA Trust Architect

This is the master rule file. The **orchestrator** — the main Claude Code session running
a `/qa-*` skill — reads it first on every invocation. Orchestration stays in the main
session because questions and gates need the human; heavy analysis stages are delegated
to specialist agents in `agents/` (see §9). All other rule files are loaded **on demand**,
one stage at a time.

`FRAMEWORK_ROOT` = the `qa-trust-architect` plugin folder (the skill resolves it from its
own base directory: two levels up). All framework paths below are relative to it; all
project paths are relative to the project root.

## 0. Prime directives

1. **AI proposes, humans decide.** Draft artifacts; never mark a gate approved yourself.
2. **Ask, don't assume.** Anything ambiguous goes to `questions.md` (see `question-protocol.md`).
   Do not invent business rules. If you must proceed on an assumption, write it as an
   explicit `ASSUMPTION-xx` in the artifact and as a question.
3. **Files are the memory.** Always read `qa-state.md` before acting and update it after
   every stage. Append every human decision to `audit.md`.
4. **Domain first.** Load domain context through `context-loader.md` before any analysis.
   Never write to domain files directly — raise a DCP (`domain-change-protocol.md`).
5. **Platform-neutral.** Work in the canonical model (`schemas/`). Talk to the work item
   platform only through the configured adapter (`adapters/<target>/adapter.md`).
6. **Trace everything.** Every AC, test case, risk, gap, defect carries IDs that link back
   to the requirement and forward to tests (see §5).
7. **Respect other workflows.** If an SDLC workflow integration is active (e.g. AI-DLC),
   follow `workflow-integration.md`; never modify that workflow's files unless write-back
   is enabled in config.

## 1. Bootstrapping each invocation

```
1. Read qa-trust.config.yaml (project root). If missing → tell user to run /qa-init. Stop.
2. Resolve paths:
     QA_ROOT      = storage.repo.path                      (default docs/qa)
     PROJECT_DIR  = QA_ROOT/_project
     DOMAIN_DIR   = domain.path                            (default QA_ROOT/_project/domain)
     ITEM_DIR     = QA_ROOT/<layout resolved for the work item>
3. If a work item is in scope: read ITEM_DIR/qa-state.md (create from template if new).
4. Check integrations (workflow-integration.md) — e.g. AI-DLC detected?
5. Determine next stage from qa-state.md + routing (routing-rules.md).
6. Load ONLY that stage's rule file + required templates + context slices.
```

## 2. Phases, stages and gates

| Phase | Stage | Rule file | Main output | Release |
|---|---|---|---|---|
| 0 Setup | 0.1 Workspace detection | `rules/phase-0-setup/0.1-workspace-detection.md` | `_project/qa-profile.yaml` | MVP |
| | 0.2 Domain discovery | `rules/phase-0-setup/0.2-domain-discovery/0.2-overview.md` | `_project/domain/*` | MVP |
| | 0.3 QA reverse engineering | `rules/phase-0-setup/0.3-qa-reverse-engineering.md` | `_project/qa-baseline.md`, `feature-test-map.yaml` | MVP |
| | 0.4 Quality standards | `rules/phase-0-setup/0.4-quality-standards.md` | `_project/quality-standards.md` | MVP |
| | **G0 QA Baseline** | `gates/G0-qa-baseline.md` | `_project/gates/G0.md` | MVP |
| 1 Inception | 1.1 Requirement intake | `rules/phase-1-inception/1.1-requirement-intake.md` | `1-inception/requirement.md` | MVP |
| | 1.2 Requirement analysis | `.../1.2-requirement-analysis.md` | `1-inception/requirement-analysis.md` | MVP |
| | 1.3 Acceptance criteria | `.../1.3-acceptance-criteria.md` | `1-inception/acceptance-criteria.md` | MVP |
| | **G1 Ready for Test Design** | `gates/G1-ready-for-test-design.md` | `gates/G1.md` | MVP |
| | 1.4 Risk & impact | `.../1.4-risk-impact-analysis.md` | `1-inception/risk-assessment.md` | MVP |
| | 1.5 Gap analysis | `.../1.5-gap-analysis.md` | `1-inception/gap-analysis.md` | MVP |
| | 1.6 Test strategy & plan | `.../1.6-test-strategy-plan.md` | `1-inception/test-plan.md` | MVP |
| | **G2 Test Plan Approved** | `gates/G2-test-plan-approved.md` | `gates/G2.md` | MVP |
| 2 Design | 2.1 Test case design | `rules/phase-2-design/2.1-test-case-design.md` | `2-design/test-cases/*.yaml` | MVP |
| | 2.2 Test data & env | `.../2.2-test-data-environment.md` | `2-design/test-data.md` | MVP (draft) |
| | 2.3 Automation gap | `.../2.3-automation-gap.md` | `2-design/automation-gap.md` | MVP (draft) |
| | 2.4 Observability design | `.../2.4-observability-design.md` | `2-design/observability-plan.md` | MVP (draft) |
| | **G3 Test Design Approved** | `gates/G3-test-design-approved.md` | `gates/G3.md` | MVP |
| 3 Execution | 3.1 Automation implementation | `rules/phase-3-execution/3.1-automation-implementation.md` | – (non-blocking stub) | v4 |
| | 3.2a Manual execution | `.../3.2a-manual-execution.md` | `3-execution/runs/RUN-*.yaml`, `execution-log.md` | v2 |
| | 3.2b Exploratory (Playwright MCP) | `.../3.2b-exploratory-playwright.md` | `3-execution/sessions/*` | v2 (slice B) |
| | 3.3 Defect management | `.../3.3-defect-management.md` | `3-execution/defects/DEF-*.yaml`, `defect-log.md` | v2 |
| | 3.4 Regression | `.../3.4-regression.md` | `3-execution/regression.md` | v2 |
| | 3.5 Test summary report | `.../3.5-test-summary.md` | `3-execution/test-summary-report.md` | v2 |
| | **G4 Quality Sign-off** | `gates/G4-quality-signoff.md` | `gates/G4.md` | v2 |
| 4 Operations | 4.1–4.4 | `rules/phase-4-operations/*` | `4-operations/*` | v4 |
| | **G5 Release Closure** | `gates/G5-release-closure.md` | `gates/G5.md` | v4 |

Stages not yet implemented exist as stubs. If routing reaches one, tell the user, record
`status: not-implemented` in `qa-state.md`, and stop — unless its rule file marks it
**non-blocking** (3.1, and 3.2b until slice B), in which case continue with the next stage.

Phase 3 stages are human-driven: the tester executes (`/qa-execute`) and confirms defects
(`/qa-defect`); 3.3 runs continuously alongside 3.2a/3.4.

## 3. Stage execution loop

For every stage:

```
a. Mark stage `in-progress` in qa-state.md.
b. Load stage rule file → follow its "Inputs", "Steps", "Output", "Self-check".
c. Load context slices declared by the stage (context-loader.md).
d. Produce the artifact from its template. Use IDs (§5).
e. Write open questions to questions.md. Raise DCPs for new/changed domain facts.
f. Run the stage self-check. Record results at the bottom of the artifact.
g. Mark stage `done` (or `blocked-on-questions` if any question is marked blocking).
h. Tell the user, in ≤10 lines: what was produced, open questions count, pending DCPs,
   and the next step (next stage, or "ready for /qa-gate Gx").
```

Never run past a gate automatically. When the next item is a gate, stop and prompt
the user to run `/qa-gate Gx`.

## 4. Answers to questions

When the user says questions are answered (or on `/qa-continue`):
1. Read `questions.md`; collect every question with a non-empty `[Answer]:`.
2. Apply each answer to the affected artifact(s); mark the question `resolved`.
3. Log in `audit.md`: `QUESTION-ANSWERED Q-xx by <name>`.
4. If answers change domain facts → raise DCPs.
5. Re-run the stage self-check.

## 5. ID & traceability conventions

| Entity | ID pattern | Scope |
|---|---|---|
| Question | `Q-01` | per work item (`questions.md`) |
| Assumption | `ASSUMPTION-01` | per work item |
| Requirement statement | `REQ-01` | per work item |
| Acceptance criterion | `AC-01` | per work item |
| Risk | `R-01` | per work item |
| Gap | `GAP-01` | per work item |
| Test case | `TC-001` | per work item (repo); platform ID in `externalIds` |
| Charter (v2) | `CH-01` | per work item |
| Execution cycle | `CY-01` | per work item |
| Test run | `RUN-001` | per work item (`3-execution/runs/`) |
| Defect | `DEF-001` | per work item (`3-execution/defects/`); platform ID in `externalIds`, tag `qa-def:<workItemKey>/DEF-001` |
| Data set | `DS-01` | per work item |
| Business rule | `BR-001` | project (domain) |
| Journey | `J-01` | project (domain) |
| Persona / role | `ROLE-<slug>` | project (domain) |
| Entity | `ENT-<slug>` | project (domain) |
| Feature | `F-<slug>` | project (domain) |
| Domain change proposal | `DCP-0001` | project (domain) |
| Discrepancy | `DISC-001` | project (domain) |

Trace chain: `REQ → AC → TC → RUN → DEF`, plus `AC ↔ BR`, `TC ↔ BR`, `R → TC`,
`GAP → (AC|TC|backlog item)`, `F ↔ (REQ, TC, code paths)`.

## 6. Tiers

See `routing-rules.md`. The tier is decided at 1.1 and recorded in `qa-state.md` with
its reason. The user may override with `/qa-continue --tier <tier>`; log the override.

## 7. Platform sync

If `storage.platform.enabled` and `syncMode: on-gate`, after a gate is **approved** (or
approved-with-risks) invoke the `sync-agent` for that gate's sync set (see each gate file,
section "On approval → sync"). Overridden gates do not sync unless the user asks.

## 8. Status reporting

`/qa-status` summarises: tier, current stage, gate table, question counts (open/blocking),
AC coverage (ACs with ≥1 TC), pending DCPs (by level and age), stale domain areas,
and integration status.

## 9. Delegation to agents

| Stages | Agent |
|---|---|
| 0.2, `/qa-domain build/refresh` | `domain-analyst` |
| 0.1, 0.3, 0.4 | inline (short) or `domain-analyst` for large repos |
| 1.1–1.3 | `requirement-analyst` |
| 1.4–1.6, 2.4 | `risk-gap-analyst` |
| 2.1–2.2 | `test-designer` |
| 2.3 | `automation-analyst` |
| Platform sync | `sync-agent` |
| 3.2a prep/ingest, 3.3 triage & drafting, 3.4, 3.5 | `execution-analyst` |
| 3.2a execution, 3.3 confirmation | inline (`/qa-execute`, `/qa-defect`) — a human executes/confirms |
| 3.2b (v2, slice B) | `exploratory-tester` |

When delegating, pass in the prompt: `FRAMEWORK_ROOT`, project root, resolved `ITEM_DIR`,
`DOMAIN_DIR`, the stage ID(s), tier, and the config excerpt the stage needs. Agents write
artifacts, questions and DCP files, and return a ≤ 15-line summary (outputs, counts,
blocking questions, DCPs raised). They never decide gates and never talk to the platform
except `sync-agent` (and read-only queries by `domain-analyst` / `requirement-analyst`).
The orchestrator then updates `qa-state.md`/`audit.md` and talks to the user.
