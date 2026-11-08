# Regression — {{workItemKey}} {{title}}

> Stage 3.4 · {{isoDate}} · Domain context v{{domainVersion}} · Tier {{tier}}

## 1. Selection
Impacted features: {{F-ids from risk-assessment (scope + adjacent)}}

| # | Test | Type | Feature | Reason selected | Source |
|---|---|---|---|---|---|
| 1 | tests/LeaveTests.cs::MaxDays | automated (unit) | F-leave-request | covers impacted rule BR-012 | feature-test-map |
| 2 | TC-014 (ADO-1180) | manual | F-leave-approval | adjacent feature, P1 | earlier item |

**Not covered by any regression test:** {{impacted areas without tests → GAP refs}}

## 2. How to run
| Group | Command / suite | Where | Result file |
|---|---|---|---|
| Unit/API | `{{dotnet test --filter Category=Leave --logger trx}}` | local / CI pipeline {{name}} | `**/TestResults/*.trx` |
| UI | `{{npx playwright test leave --reporter=junit}}` | CI | `test-results/junit.xml` |
| Manual | `/qa-execute {{workItemKey}} --set regression` | tester | runs/*.yaml |

## 3. Results
| Group | Total | Passed | Failed | Skipped | Pass rate | Source |
|---|---|---|---|---|---|---|

## 4. Failure triage
| Test | Run | Failure class | Evidence | Action |
|---|---|---|---|---|
| | | product-defect / test-defect / environment / data / flaky | | DEF-xxx / fix test / rerun |

## Self-check
- [ ] Every impacted feature has ≥ 1 regression test or a recorded gap
- [ ] Every failure triaged (no `untriaged`)
- [ ] Flaky tests re-run per `execution.flakyReruns` before being classed
