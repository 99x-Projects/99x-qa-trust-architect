---
gate: "{{G1}}"
scope: "{{workItemKey | project}}"
decision: "{{approved | approved-with-risks | rejected | overridden}}"
decidedBy: "{{name}}"
decidedAt: "{{isoDateTime}}"
mode: "{{advisory | blocking}}"
domainVersion: "{{domainVersion}}"
returnToStage: null            # when rejected
artifacts:
  - { path: "1-inception/acceptance-criteria.md", hash: "{{sha256}}" }
---

# {{G1}} — {{gate name}} · {{scope}}

## Checklist
| # | Item | Result | Evidence / note |
|---|---|---|---|
| C1 | {{item}} | ✔ met | {{ref}} |
| C2 | {{item}} | ✗ unmet | {{ref}} |

**Met:** {{x}}/{{y}}

## Decision
**{{decision}}** by {{name}} at {{isoDateTime}}
Reason: {{reason}}

## Accepted risks (approved-with-risks / overridden)
| Unmet item | Risk accepted | Follow-up |
|---|---|---|

## DCPs reviewed in this gate
| DCP | Level | Decision |
|---|---|---|

## Sync performed
| Operation | Result |
|---|---|
