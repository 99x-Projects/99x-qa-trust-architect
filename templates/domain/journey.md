---
id: J-04
name: "{{Leave request to approval}}"
features: [F-leave-request, F-leave-approval]
roles: [ROLE-employee, ROLE-manager]
status: inferred                 # documented | observed | inferred | confirmed | disputed
confidence: medium
sources:
  - { type: test, ref: "e2e/leave.spec.ts", hash: null }
lastVerified: "{{isoDate}}"
priority: high                   # usage/risk priority
---

# J-04 — {{name}}

## Steps
| # | Actor | Action | System response | Page / API | Rules |
|---|---|---|---|---|---|
| 1 | Employee | Opens "New leave" | Form shown with balance | /leave/new | – |
| 2 | Employee | Submits dates | Request status = Submitted | POST /api/leave | BR-012, BR-015 |

## Variants & alternative paths
- {{e.g. manager requests own leave → department head approves}}

## Failure paths
- {{e.g. overlapping request → error message}}
