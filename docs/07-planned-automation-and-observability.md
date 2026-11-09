# 7. Planned: automation generator & observability agents (v4)

> **Status: design proposal.** Nothing on this page is implemented yet. The stage rules
> (`rules/phase-3-execution/3.1-automation-implementation.md`, `rules/phase-4-operations/*`) are
> non-blocking stubs today. This page describes how the two planned capabilities plug into what
> already exists, so current artifacts are produced in a shape they can consume.

## Why they come last

Both capabilities consume artifacts the earlier stages already produce:

| Already produced today | Consumed by |
|---|---|
| 2.3 automation backlog `AB-xx`, each TC's `automation` block (level, target framework, path, test name with `TC-xxx`, pipeline stage, `extends`, blockers) | **automation-engineer** (3.1) |
| 2.2 data sets `DS-xx` and the repo's builders/seeds (`qa-profile.yaml → testData`) | automation-engineer |
| Live crawl app map (pages, roles, element labels) | automation-engineer (UI tests) |
| 2.4 signals `SIG-xx`, alerts, SLOs, synthetics, `OBS-xx` checks | **observability-analyst** (4.1, 4.2) |
| 3.5 test summary residual risks, G4 accepted risks | observability-analyst (what to watch first), 4.3 escape analysis |
| Run records, defects, gate records, audit | 4.4 metrics |

## A. Automation script generator — stage 3.1

**Agent:** `automation-engineer` · **Command:** `/qa-automate <id> [AB-01,AB-02 | --all-now]`
· **Gate:** none of its own — the pull request review is the checkpoint, and G4 uses the results.

### Flow

```
AB-xx (automate-now) ─► plan ─► generate ─► run red/green ─► import results ─► PR for review
        │                 │          │              │                │                 │
  TC automation block  extend or  repo's own     must pass, and    links runs to   traceability table,
  DS-xx data set       new file   conventions    must fail when    TC-xxx; TC      dev + tester review
                                                 behaviour broken  status→automated
```

1. **Plan per backlog item.** If the item says `extends: tests/Api/LeaveTests.cs::Submit_valid`,
   add a case there; otherwise create the file at `target.path`. Show the plan before writing code.
2. **Generate in the repo's style.** Read neighbouring tests first: framework, naming, page objects,
   fixtures, builders, assertion library. No new dependencies without asking.
   - API / unit / contract: request + assertions mapped one-to-one to the TC's expected results.
   - UI: Playwright (or the repo's framework), locators by role and label taken from the app map;
     `data-testid` only if it exists. No fixed sleeps.
   - Data from the TC's data set via the repo's builders; relative dates; secrets only via env refs.
   - Test name contains the TC id (`TC-004_rejects_21_days`), so results import in 3.4 without mapping.
3. **Run red/green.** The test must pass on the current build *and* fail when the behaviour it
   guards is broken. The agent proves the second part by temporarily inverting the key assertion
   (or running against the known defect build) and records it. A test that cannot fail is rejected.
4. **Stability.** Run each new test 3× (configurable). Any inconsistency → `quarantined`, reason
   recorded, not merged into the PR pipeline stage.
5. **Record.** Import the run results (`scripts/import_results.py`), set the TC's
   `automation.status: automated`, `automation.implementedIn: <file>::<test>`, and close the AB item.
6. **Pull request.** On a branch `qa/automation/<item>`, with a traceability table
   (AB → TC → AC → test), the red/green evidence and the pipeline stage. The PR is created only after
   you confirm. Nothing is pushed to the default branch.

### Guardrails

- Writes only inside the test folders detected in 0.1 (new guard `automationPaths`); app code is read-only.
- Never weakens an assertion to make a test pass. A failing test against the current build is a
  defect candidate (3.3), not something to "fix" in the test.
- The secret scan and secret-file guards apply to generated code.
- Dev asks (`DA-xx`) that block an item (missing test IDs, no data API) are reported, not worked around.

## B. Observability agents — Phase 4

**Agent:** `observability-analyst` (with `exploratory-tester` for production smoke)
· **Command:** `/qa-release <id> verify | observe | escapes | retro`
· **Gate:** **G5 Release Closure**.

It connects **read-only** to the monitoring stack detected in 0.1 (Application Insights / Log
Analytics, OpenTelemetry back ends, Prometheus/Grafana, Datadog, Elastic, Sentry) through that
stack's MCP server or CLI. Credentials go in `.env` with read-only scopes, like the ADO PAT.

### 4.1 Release verification (day 0)

- Confirms the deployed version and feature flag states match the release.
- Runs the **safe-path synthetics** from 2.4 against production: read-only journeys, or writes only
  into a test tenant. Production is used only if `environments.yaml` marks it
  `readOnlySmoke: true`; the browser guard still refuses destructive actions.
- Result: `4-operations/release-verification.md`.

### 4.2 Observability validation (day 0–2)

For every `SIG-xx` in the observability plan:

| Check | Example |
|---|---|
| Emitted in production | `leave.request.rejected` has data points since the release |
| Shape as designed | dimensions = `reason` only; cardinality below the limit |
| No personal data | property **names** sampled, values never pulled; aggregates only |
| Dashboards populated | each panel in the plan returns data |
| Alerts in place | the rule exists with the designed condition, window, severity and route; where a safe trigger exists (a test alert or staging), it fires |
| SLO baseline | first-week value captured against the objective |

Gaps become defects (confirmed by you, as in 3.3) or dev asks. Result: `4-operations/observability-validation.md`.

### 4.3 Escape analysis (watch window, default 14 days)

- Watches production defects and incidents linked to the item or its features.
- For each escape asks *why testing missed it*: no AC, no test case, test passed against a wrong
  oracle, environment or data parity, not executed, accepted risk materialised.
- Proposes follow-ups: new TCs, regression additions, DCPs (e.g. raise a feature's risk hotspot),
  quality-standards changes. You accept or reject each one.

### 4.4 Retrospective & metrics

AC coverage, automation ratio vs target, defect detection % (found before vs after release), escape
rate, gate cycle time, override rate. Stored as a metrics snapshot per item and rolled up per project
in `/qa-status --project`.

### G5 Release Closure (draft checklist)

| # | Item |
|---|---|
| C1 | Production smoke passed |
| C2 | Observability signals verified; alerts tested |
| C3 | Escaped defects analysed; follow-up TCs/DCPs raised |
| C4 | Retrospective notes captured; metrics snapshot stored |

## How the loop closes

```
production signals ─► 4.3 escapes ─► DCPs (hotspots, rules) ─► domain context v+1
        ▲                                                          │
        │                                                          ▼
   2.4 signal design ◄── 1.4 risk scoring of the next work item ◄──┘
```

Every escape makes the next item's risk scoring and test design sharper, and every automated
`AB-xx` moves a manual test case into the pipeline for good.

## What you can do today to be ready

- In 2.3, keep `automation.target` filled for automate-now items, and test names containing the TC id.
- In 2.4, write alert conditions as real query sketches in your stack's language.
- Mark production in `environments.yaml` with `agentsAllowed: false` (it stays that way; 4.1 will use
  a separate `readOnlySmoke` flag).
- Record dev asks for missing test IDs and data APIs early — they unblock both generators.
