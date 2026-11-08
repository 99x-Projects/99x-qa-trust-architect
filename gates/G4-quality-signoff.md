# G4 — Quality Sign-off (Go / No-Go)  *(planned: v2)*

**When:** after Phase 3. **Record:** `ITEM_DIR/gates/G4.md`.

## Checklist (draft)
| # | Item |
|---|---|
| C1 | Exit criteria from test-plan met (with numbers) |
| C2 | All planned TCs executed or deferred with reason |
| C3 | No open defects above agreed severity, or accepted with named risk |
| C4 | Regression set executed; failures triaged |
| C5 | Exploratory sessions completed for high-risk charters |
| C6 | All earlier gate overrides listed and acknowledged |
| C7 | Pending DCPs from execution reviewed |
| C8 | Test summary report complete |

## On approval → sync
`publishTestRun`, `setGateStatus G4`, summary comment with Go/No-Go.
