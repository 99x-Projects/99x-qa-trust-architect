# Observability Plan — {{workItemKey}} {{title}}

> Stage 2.4 · {{isoDate}} · Domain context v{{domainVersion}} · Stack: {{detected observability stack}}

## 1. Existing instrumentation (impacted code)
| Where | What is emitted | Convention |
|---|---|---|
| src/Leave/LeaveService.cs | `logger.LogInformation("LeaveSubmitted …")` | PascalCase event names; `leave.` metric prefix |

## 2. Signals
| ID | Risk / AC | Type | Name | Fields / dimensions (no PII, low cardinality) | Purpose | New / exists |
|---|---|---|---|---|---|---|
| SIG-01 | R-01 / AC-03 | metric | `leave.request.rejected` | reason | detect limit regressions | new |
| SIG-02 | R-03 / INT-email | span | `smtp.send` | outcome, duration | integration health | exists |

## 3. Alerts
| Name | Signal | Condition (query sketch) | Window | Threshold rationale | Severity | Route | Runbook |
|---|---|---|---|---|---|---|---|
| Leave rejections spike | SIG-01 | `customMetrics \| where name == "leave.request.rejected" \| summarize count() by bin(timestamp, 15m)` | 15 min | > 3× 7-day average (tune after 2 weeks) | Sev3 | #team-leave | {{link}} |

## 4. SLOs
| SLI | Objective | Window | Error budget owner |
|---|---|---|---|
| Leave submit success = 2xx / all submit requests | 99.5% | 30 days | {{team}} |

## 5. Dashboard panels
- {{KPI, error rate, p95 latency, integration health, top rejection reasons}}

## 6. Synthetic checks (production, safe-path only)
| Journey | Steps | Frequency | Account / tenant | Success criteria |
|---|---|---|---|---|

## 7. Dev asks (instrumentation / testability)
| DA | Ask | Serves | Create on platform? |
|---|---|---|---|
| DA-03 | Emit `leave.request.rejected` with `reason` | SIG-01 | ask at G3 |

## 8. Verification checks (run in Phase 3)
| OBS | Check | Environment | Phase |
|---|---|---|---|
| OBS-01 | Submit 21-day request → `leave.request.rejected{reason=limit}` within 5 min, no PII in properties | test | 3.2a |
| OBS-02 | Stop mail catcher → alert "Email failures" fires | test | 3.2a |

## 9. Not observable (accepted)
| Risk | Reason | Compensating control |
|---|---|---|

## Self-check
- [ ] High risks → signal or not-observable + control
- [ ] Conventions followed; no PII; low-cardinality dimensions
- [ ] Alerts complete (condition, window, rationale, severity, route)
- [ ] SLOs for NFR targets in scope
- [ ] OBS check per new/changed signal
