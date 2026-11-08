---
session: SES-001
charter: CH-01
workItemKey: "{{ADO-1234}}"
type: exploratory              # focused | exploratory | re-verification | smoke
mode: autonomous               # autonomous | guided | pair
tester: "{{name}}"             # who ran / supervised it
role: ROLE-employee
environment: test
build: "{{build}}"
started: "{{isoDateTime}}"
ended: "{{isoDateTime}}"
durationMinutes: 0
actions: 0
domainVersion: "{{domainVersion}}"
stoppedBecause: charter-covered  # charter-covered | time-box | action-limit | safety-stop | tester
---

# Session Report — SES-001 · CH-01 {{charter title}}

## Summary
{{3–5 sentences: what was explored, what was found, overall impression of quality in this area.}}

## Charter coverage
| Area / heuristic | Explored | Notes |
|---|---|---|
| Boundaries on duration | ✔ | 0, 1, 20, 21, 365 |
| Permissions via direct URL | ✗ | not reached — time box |

## Findings
| # | Type | Summary | Oracle | Severity (suggested) | Evidence | Follow-up |
|---|---|---|---|---|---|---|
| F1 | defect-candidate | 21-day request accepted | AC-03 / BR-012 (confirmed) | Sev2 | evidence/F1-accepted.png | DEF draft |
| F2 | question | Approver can edit dates after approval | BR-020 (observed — provisional) | – | evidence/F2.png | Q-09, DISC-004 |
| F3 | app-map | New page "/leave/calendar" | – | – | evidence/F3.png | DCP (auto) |
| F4 | tc-suggestion | Double submit creates two requests? (not reproduced) | – | – | log 10:42 | ask tester |

Types: defect-candidate · question · quirk-candidate · app-map · tc-suggestion · automation-candidate · observation

## Skipped for safety (needs a tester)
| Time | Action | Reason |
|---|---|---|
| 10:37 | Click "Delete request" | matches blockActions: delete |

## Test data created (for cleanup)
| Entity | Identifier | Notes |
|---|---|---|
| Leave request | QA-SES-001-a | 21 days, pending |

## Console / network issues observed
| Time | Page | Kind | Detail (redacted) |
|---|---|---|---|

## Session log
| Time | Action | Target | Observation |
|---|---|---|---|
| 10:31 | navigate | /leave/new | form shown, 4 fields |
