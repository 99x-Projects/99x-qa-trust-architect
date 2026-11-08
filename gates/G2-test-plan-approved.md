# G2 — Test Plan Approved

**When:** after 1.4–1.6 (standard & comprehensive tiers). **Record:** `ITEM_DIR/gates/G2.md`.
**Comprehensive tier:** product owner participation recommended.

## Checklist
| # | Item | Evidence |
|---|---|---|
| C1 | Every AC appears in the risk assessment (or marked low-risk) | risk-assessment.md |
| C2 | Every high risk has a mitigation | risk-assessment.md |
| C3 | (brownfield) Impacted areas and regression candidates listed | risk-assessment.md §impact |
| C4 | All gap types assessed; each gap has closure or accepted reason | gap-analysis.md |
| C5 | Scope in/out stated; out-of-scope justified | test-plan.md §1 |
| C6 | Approach maps test levels/types to risks | test-plan.md §2 |
| C7 | Exit criteria quantified | test-plan.md §7 |
| C8 | Environment/data needs identified with owners | test-plan.md §4 |
| C9 | G1 approved or overridden (not stale) | qa-state.md |

## On approval → sync
- `setGateStatus G2`
- `addComment`: risk summary (counts high/med/low), gap summary, link to test-plan.md
- ADO: create/ensure test suite for the work item (adapter `ensureSuite`)
