# Gate Protocol

A gate is a human checkpoint. The AI **prepares** the gate; a human **decides**.
Gate checklists live in `gates/Gx-*.md`. Gate records are written to
`ITEM_DIR/gates/Gx.md` (or `PROJECT_DIR/gates/G0.md` for G0).

## 1. Who can approve

- `gates.approvers.default: any-tester` → anyone listed in `gates.team.testers`
  (`"*"` = anyone) may approve any gate, including multiple gates on the same item.
- `gates.approvers.overrides` may restrict specific gates to roles/people.
- The AI must ask for the approver's name if it is not known from the session
  (git `user.name` is a sensible default — confirm it).

## 2. Flow: read → analyse → decide → record

### Step 1 — Read (AI builds the gate pack)
Present a compact pack:
```
Gate G2 — Test Plan Approved — ADO-1234 "Leave approval"
Tier: standard   Domain context: v1.14
Artifacts: risk-assessment.md · gap-analysis.md · test-plan.md
Checklist: 9/11 met
  ✗ C5 Exit criteria quantified         → test-plan.md §7 says "most tests pass"
  ✗ C8 All high risks have mitigation   → R-03 has none
Open questions: 1 (non-blocking)   Pending DCPs from this item: 2 (1 critical)
Overrides so far on this item: none
```
Evaluate each checklist item honestly against the artifacts. Cite the file/section.

### Step 2 — Analyse (approver interrogates)
Answer the approver's questions using the artifacts and domain context only, e.g.
"show ACs without negative cases", "why is R-02 rated high?". Offer to fix gaps
before the decision (that re-runs the stage's self-check).

### Step 3 — Decide
Ask the approver for exactly one decision:

| Decision | Meaning | Allowed when |
|---|---|---|
| `approved` | All checklist items met | 100% met |
| `approved-with-risks` | Proceed; unmet items accepted as named risks | any unmet item, reason given |
| `rejected` | Return to a stage | always; must name the stage to return to and why |
| `overridden` | Proceed without review (advisory mode skip) | advisory mode only; reason required |

Then process DCPs listed in the pack **individually** (accept / reject / defer) —
gate approval never auto-approves DCPs. Bulk accept is allowed if the approver says so.

### Step 4 — Record
1. Write `gates/Gx.md` from `templates/gate-record.md` (checklist results, decision,
   approver, timestamp ISO-8601, accepted risks, domain context version, artifact hashes).
   Produce the `artifacts:` list with `python <FRAMEWORK_ROOT>/hooks/qa_guard.py hash <ITEM_DIR> Gx`
   (canonical sha256 — ignores sync bookkeeping keys `externalIds`, `contentHash`, `published`).
2. Append to `audit.md`: `GATE Gx <decision> by <name> — <one-line reason>`.
3. Update `qa-state.md` gate table.
4. If platform enabled: set gate status via adapter `setGateStatus(item, "Gx", decision)`
   → tag e.g. `qa-gate:G2-approved` / `qa-gate:G2-overridden`.
5. If `approved` or `approved-with-risks` and `syncMode: on-gate`: run the gate's sync set.

## 3. Advisory vs blocking

- `gates.mode: advisory` (default): if the user asks to proceed to a stage beyond an
  undecided gate, show the unmet checklist, ask for a reason, record the gate as
  `overridden`, and continue.
- `blocking` (globally or per gate via `gates.perGate`): refuse to start later stages
  until the gate is `approved` or `approved-with-risks`.
- Overrides are always visible: listed in `/qa-status`, in later gate packs, and in the
  G4 test summary report.

## 4. Re-opening a gate

If an artifact covered by an `approved` / `approved-with-risks` gate changes, the gate becomes
`stale`. The **gate-stale hook** (`hooks/qa_guard.py`, `guards.gateStale`) does this automatically
after every write: it compares the file's canonical hash with the gate record (or, for files not in
the record, the gate's default coverage — G1 requirement/analysis/AC, G2 risk/gap/plan, G3
`2-design/`, G4 summary + runs), sets the gate row to `stale` in `qa-state.md`, appends
`GATE Gx stale (was …)` to `audit.md`, and tells you. Without hooks, do the same by hand.

Then tell the user. Two ways out:
- **Re-affirm** (`/qa-gate Gx --reaffirm`) — the change is not material (typo, formatting): the
  approver looks at the change, the previous decision is restored, the record's hashes are
  refreshed, audit `GATE Gx reaffirmed by <name> — <reason>`.
- **Re-run the gate** — material change: full read → analyse → decide → record.

The next gate pack and the G4 summary list stale and re-affirmed gates.
