# G3 — Test Design Approved

**When:** after 2.1 (+2.2–2.4 per tier). **Record:** `ITEM_DIR/gates/G3.md`.

## Checklist
| # | Item | Evidence |
|---|---|---|
| C1 | Every AC has ≥ 1 TC | test-case-index.md coverage matrix |
| C2 | High-risk AC have negative + boundary TCs | test-case-index.md |
| C3 | Every TC traces to ≥ 1 AC; no duplicates | test-case-index.md |
| C4 | Expected results specific/observable; provisional basis tagged | test-cases/*.yaml |
| C5 | Existing coverage reused (not duplicated) | `existingCoverage` fields |
| C6 | Test data sets defined; no PII/secrets (if 2.2 ran) | test-data.md |
| C7 | Every TC classified for automation; manual-only justified (if 2.3 ran) | automation-gap.md |
| C8 | High risks have production signals (if 2.4 ran) | observability-plan.md |
| C9 | G2 approved/overridden and not stale (or tier light) | qa-state.md |

## On approval → sync
- `upsertTestCase` for each TC (Gherkin → steps per adapter mapping), store `externalIds`
- `linkItems` TC ↔ work item (Tested By)
- Optional (ask): automation backlog items from 2.3
- `setGateStatus G3`
