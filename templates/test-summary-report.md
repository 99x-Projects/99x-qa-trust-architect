# Test Summary Report — {{workItemKey}} {{title}}

> Stage 3.5 · {{isoDate}} · Tier {{tier}} · Domain context v{{domainVersion}}
> Build {{build}} · Environment {{environment}} · Cycles {{CY-01..}}

## Recommendation: {{GO | GO with risks | NO-GO}}
{{2–4 sentences: why. The recommendation is the AI's; the decision is taken at G4.}}

## 1. Exit criteria (test-plan §7, else quality-standards defaults)
| Criterion | Target | Actual | Met | Evidence |
|---|---|---|---|---|
| P1 TCs executed and passed | 100% | {{x}}% | ✔/✗ | execution-log.md |
| Planned TCs executed | ≥ 95% | | | |
| Open Sev1/Sev2 | 0 | | | defect-log.md |
| Regression pass rate (after triage) | ≥ 98% | | | regression.md |

## 2. Execution
| Set | Planned | Executed | Passed | Failed | Blocked | Deferred | Pass rate |
|---|---|---|---|---|---|---|---|
| Planned TCs | | | | | | | |
| Regression | | | | | | | |
| Retests | | | | | | | |

## 3. Defects
| Severity | Found | Open | Fixed & retested | Accepted / deferred | Rejected / duplicate |
|---|---|---|---|---|---|
| Sev1 | | | | | |
| Sev2 | | | | | |
| Sev3 | | | | | |
| Sev4 | | | | | |

Open defects carried forward: {{DEF — severity — accepted by / reason}}

## 4. Coverage & traceability
- AC covered by ≥ 1 passed TC: {{x}}/{{y}} — not covered: {{AC ids + reason}}
- High risks with passed mitigation tests: {{x}}/{{y}}
- Provisional-basis TCs executed: {{n}} (cannot fail; observations raised as questions: {{Q ids}})

## 5. Exploratory sessions
| Charter | Session | Findings | Report |
|---|---|---|---|
{{"none — 3.2b not run" if applicable}}

## 6. Gate history and overrides on this item
| Gate | Decision | By | Reason (if overridden / with risks) |
|---|---|---|---|

## 7. Domain impact
- DCPs raised during execution: {{ids, status}}
- Discrepancies opened: {{ids}}

## 8. Residual risks
| Risk | Why still open | Mitigation (monitoring, follow-up) | Owner |
|---|---|---|---|
