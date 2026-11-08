# G0 — QA Baseline (project-level)

**When:** after Phase 0 (`/qa-init` → 0.1–0.4). Re-run on major re-baseline.
**Record:** `PROJECT_DIR/gates/G0.md`. **Approvers:** per `gates.approvers` (default any tester).

## Checklist
| # | Item | Evidence |
|---|---|---|
| C1 | Project profile complete; platform & storage confirmed | `qa-profile.yaml`, config |
| C2 | Adapter connection tested (read one work item) | 0.1 log |
| C3 | Feature map covers the application's main areas; every feature has `depth` + `discoveryMode` | `feature-map.yaml` |
| C4 | Glossary, roles, entities present | domain files |
| C5 | Deep features have rules with status/confidence/sources | `business-rules.yaml` |
| C6 | All blocking interview questions answered | `_project/questions.md` |
| C7 | Discrepancies either resolved or explicitly carried as open | `discrepancies.md` |
| C8 | (brownfield) QA baseline + feature-test-map reviewed | `qa-baseline.md` |
| C9 | Quality standards agreed; exit criteria measurable | `quality-standards.md` |
| C10 | No secrets in any file | scan result |
| C11 | Integrations detected and mode agreed (e.g. AI-DLC companion) | `qa-profile.yaml` |

## Decision specifics
- Approval promotes **reviewed** facts to `confirmed` where the reviewer confirms them
  (bulk "confirm all high-confidence deep facts" allowed; record which).
- Sets `domainVersion: 1.0.0` (or next major on re-baseline).

## On approval → sync
None (project-level). Optionally post a summary comment to a configured "QA setup" work item.
