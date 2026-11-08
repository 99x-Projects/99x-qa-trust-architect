# Test Data & Environment — {{workItemKey}} {{title}}

> Stage 2.2 · {{isoDate}} · Domain context v{{domainVersion}} · Tier {{tier}}

## 1. Data sets
| ID | Purpose | Entities / states | Key values | Shared / exclusive | Creation method | Lifecycle (create · reset) | Used by |
|---|---|---|---|---|---|---|---|
| DS-01 | Employee at the per-request limit | ENT-employee (balance 25), ENT-leave-request (none) | 20, 21 days from next working day | exclusive | API `POST /leave` via `LeaveBuilder` | per TC · cancelled after run | TC-001, TC-002 |

Machine-readable sets (optional): `data-sets/DS-xx.yaml`.

## 2. Privacy classification
| Field | Class | Value strategy |
|---|---|---|
| employee.name | personal | fake generator |
| employee.email | personal | `qa.<n>@example.com` |
| leave.reason | sensitive (may contain health info) | fixed neutral text "QA test" |

Masked production copy used: **no** / yes — approved by {{name}}, masking: {{fields + technique}}

## 3. Accounts (references only — no secrets)
| Role | test | staging | Notes |
|---|---|---|---|
| ROLE-employee | `env:TEST_EMPLOYEE_USER` | `env:STAGING_EMPLOYEE_USER` | |
| ROLE-manager | `env:TEST_MANAGER_USER` | – (missing → GAP-07) | |

## 4. Environment needs
| Need | Environment | Required state / setting | Stub / sandbox | Failure modes simulable | Status |
|---|---|---|---|---|---|
| Feature flag `newApprovalFlow` | test | on (TC-004 also off) | – | – | available |
| INT-email | test | capture inbox | mail catcher | provider down: no | to-create |
| Clock control | test | set date to 31 Dec | – | – | blocked |

Env-parity risks (differences from production that matter): {{list}}

## 5. Readiness → entry criteria
| Item | Status | Owner | Needed by | Entry criterion added |
|---|---|---|---|---|
| DS-01 | to-create | {{name}} | {{date}} | ✔ test-plan §6 |

## 6. Gaps raised
| GAP | Type | Description | TCs affected |
|---|---|---|---|

## Self-check
- [ ] Every TC/data row → data set; every set → TCs
- [ ] No hard-coded dates; mutating TCs use exclusive data
- [ ] All fields classified; no real PII; secrets as references only
- [ ] Integrations: stub/sandbox decision + failure-mode capability
- [ ] Non-available items have owner, date and entry criterion
