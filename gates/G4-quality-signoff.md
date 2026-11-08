# G4 — Quality Sign-off (Go / No-Go)

**When:** after 3.5 Test summary report. **Record:** `ITEM_DIR/gates/G4.md`.
**Decides:** whether the work item is good enough to release from a quality point of view.
The test summary report's recommendation is input, not the decision.

## Checklist
| # | Item | Evidence |
|---|---|---|
| C1 | Exit criteria met, with numbers (test-plan §7 or quality-standards defaults) | test-summary-report.md §1 |
| C2 | All planned TCs executed (latest result) or deferred with reason + who agreed | execution-log.md |
| C3 | No open defects at or above the blocking severity (default Sev1/Sev2), or each accepted with a named risk and owner | defect-log.md, defects/*.yaml |
| C4 | No failed/blocked run left `untriaged`; every product failure has a DEF or a question | runs/*.yaml |
| C5 | Regression set executed and failures triaged (if 3.4 ran for the tier) | regression.md |
| C6 | Mandatory exploratory charters (`exploratory.sessions.mandatoryCharters`, default high-risk) run or skipped with reason; their findings triaged (`n/a` for light tier) | charters.md, sessions/*/session-report.md |
| C7 | Every AC has ≥ 1 passed TC, or the gap is a named residual risk | test-summary-report.md §4 |
| C8 | All earlier gate overrides / approved-with-risks / stale gates listed and acknowledged | test-summary-report.md §6 |
| C9 | DCPs and questions raised during execution reviewed (none pending at critical level) | `_proposals/`, questions.md |
| C10 | Test summary report complete; recommendation consistent with C1–C9 | test-summary-report.md |
| C11 | No credentials or personal data in runs, evidence names or defects | 3-execution/** |

`approved` requires all applicable items met. A **NO-GO** outcome is recorded as `rejected`
with `returnToStage` (usually 3.2a after fixes, or 3.3 for retests).

Decision wording at this gate:
- `approved` → **GO**
- `approved-with-risks` → **GO with risks** (each unmet item → named risk + owner)
- `rejected` → **NO-GO**
- `overridden` → proceed without sign-off (advisory mode; reason required; highlighted everywhere)

## On approval → sync
1. `publishTestRun` for runs not yet `published` (grouped per cycle; manual and automated
   results that map to platform test cases).
2. `setGateStatus G4` → e.g. `qa-gate:G4-approved`.
3. `addComment` on the work item: decision (GO / GO with risks), exit criteria summary, open
   defects with accepted risks, link to the report path in the repo.
