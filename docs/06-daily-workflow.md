# 6. Daily workflow — one work item end to end

Example: Azure DevOps user story **1234 "Submit leave request"**, standard tier.

## 1. Start

```
/qa-start 1234
```

- Fetches the story (and parent/linked items) and converts it to the canonical model.
- Picks the tier (here *standard*) — override with `--tier`.
- Loads only the relevant domain slices (features, rules, roles touched by the story).
  If a feature is still `skeleton`, it is deepened first (lazy deepening → DCPs).
- `requirement-analyst` runs 1.1 → 1.3 and writes:

```
docs/qa/ADO-1234/
  qa-state.md                      ← where the item is
  questions.md                     ← what the AI needs from you
  audit.md                         ← every decision
  1-inception/requirement.md
  1-inception/requirement-analysis.md
  1-inception/acceptance-criteria.md
```

## 2. Answer questions

Open `docs/qa/ADO-1234/questions.md`:

```markdown
### Q3 — Maximum leave days per request (blocking)
The story says "reasonable length"; code enforces 25, old spec says 20.
A) 20   B) 25   C) No limit   D) Other
Suggested: B (matches current behaviour, BR-012 observed)
[Answer]: A — HR policy changed in 2025
```

Then `/qa-continue 1234`. Answers update the artifacts; answers that change domain
knowledge become DCPs.

## 3. Gate G1 — Ready for Test Design

```
/qa-gate G1 1234
```

You get a gate pack: checklist met/unmet with evidence, open questions, pending DCPs,
risks. Ask anything ("show me AC-03's edge cases", "why is NFR-2 a gap?"). Decide:

| Decision | Meaning |
|---|---|
| approved | Move on |
| approved-with-risks | Move on; risks recorded and carried to later gates |
| rejected | Fix and re-run the gate |
| overridden | Proceed despite unmet items (advisory mode); reason recorded; not synced unless requested |

On approval the sync agent shows a dry run, then writes the acceptance criteria to the story's
*Acceptance Criteria* field and sets the tag `qa-gate:G1-approved`.

If an artifact covered by an approved gate changes later, the gate is marked **stale**
automatically and you are told. Trivial edit → `/qa-gate G1 1234 --reaffirm`; real change → run the
gate again.

## 4. Plan — G2

`/qa-continue 1234` → `risk-gap-analyst` writes `risk-assessment.md`, `gap-analysis.md`,
`test-plan.md` → `/qa-gate G2 1234`.

## 5. Design — G3

`/qa-continue 1234` → the design stages run:

| Stage | Artifact | Example content |
|---|---|---|
| 2.1 Test cases | `2-design/test-cases/TC-*.yaml` | `TC-004` boundary: 20 days accepted, 21 rejected (traces AC-03, BR-012) |
| 2.2 Test data & env | `test-data.md`, `data-sets/DS-*.yaml` | `DS-02` employee with 18 days balance, start date *today + 7*, exclusive (TC mutates it); email capture needed → entry criterion, owner Dev lead |
| 2.3 Automation gap | `automation-gap.md` | TC-004 → API level, value 14 → automate now as `AB-01` in `tests/Api/LeaveTests.cs`, test name `TC-004_rejects_21_days`, PR pipeline; TC-009 already covered by `LeaveValidatorTests.cs:42` |
| 2.4 Observability | `observability-plan.md` | `SIG-01` metric `leave.request.rejected{reason}`; alert on a 3× spike; `OBS-01` check: submit 21 days → metric appears within 5 min, no PII |

Standard tier runs 2.2 and 2.4 only when needed (non-initial state, several roles, integrations,
time, flags; high risks needing production signals) → `/qa-gate G3 1234`.

On approval: a requirement-based suite is created in your Test Plan and test cases are
created/updated with steps and linked to the story (*Tested By*). IDs are written back into
the YAML files so re-syncing updates instead of duplicating. Optionally, automation backlog items
(`AB-xx`) and dev asks (`DA-xx`) are created as tagged work items.

## 6. Execute — Phase 3

```
/qa-execute 1234
```

- Tell it the **build** and **environment**; it checks the test plan's entry criteria and lists the
  manual test cases to run (highest priority first), plus the observability checks `OBS-xx`.
- **In chat:** it shows one test case at a time — steps, expected results, data, and which test
  account role to use (e.g. "the account in `TEST_EMPLOYEE_USER`" — it never shows passwords).
  You answer `all pass`, `step 3 fail: saved without a warning`, `blocked: env down`, and give an
  evidence file path for failures. Each result is saved straight away as `3-execution/runs/RUN-xxx.yaml`.
- **Offline:** `/qa-execute 1234 --sheet` writes an execution sheet you fill in; then
  `/qa-execute 1234 --ingest`.
- **Automated results:** `/qa-execute 1234 --import TestResults/run.trx` (JUnit XML or TRX). Tag
  automated tests with their `TC-xxx` id to link them automatically.

### Exploratory testing in the browser

```
/qa-explore 1234 charters          # charters from the item's risks and gaps
/qa-explore 1234 run CH-01         # asks the mode
```

| Mode | What happens |
|---|---|
| **autonomous** | You log in in the browser window; the AI explores the charter alone within its time box and writes a session report |
| **guided** | The AI drives the browser, shows what it sees and proposes probes; you steer ("now try it as a manager", "try 0 days") |
| **pair** | You drive the browser; say "note" or "check this" and the AI snapshots the page, compares it with the rules and logs it |

Findings are classified like test failures: only violations of approved AC / confirmed rules (or
crashes, 5xx, console errors) become defect drafts; the rest become questions, quirk candidates,
app-map updates or test-case suggestions. `/qa-explore 1234 retest DEF-001` re-verifies a fix in the
browser.

## 7. Defects

Each failure is triaged. Only failures against an **approved AC or confirmed business rule** become
defect drafts; a failure that rests on a provisional fact becomes a question instead, and a match
with `known-quirks.md` is not a defect.

```
/qa-defect 1234 confirm
```

You see each draft (title, severity, expected vs actual, possible duplicates in ADO) and confirm,
edit, reject, mark duplicate or defer. **Only confirmed defects are created** in ADO — as a Bug with
repro steps, severity, evidence attachments, and links to the story and test case. When the
developer resolves it: `/qa-defect 1234 retest DEF-001`.

## 8. Regression, summary and G4

`/qa-continue 1234` → the regression set is selected (existing automated tests first) with the
exact commands to run; import the results with `--import`. Then the **test summary report** is
written: exit criteria with real numbers, defects, coverage, overrides, residual risks and a
recommendation.

```
/qa-gate G4 1234
```

Decide **GO** (approved), **GO with risks** (approved-with-risks), or **NO-GO** (rejected — back to
execution). On GO, run results are published to the ADO Test Plan and a summary comment is posted on
the story.

## 9. Check status any time

```
/qa-status 1234          # this item
/qa-status --project     # whole project: G0, domain version, pending DCPs, active items
```

## Tips

- **Anyone on the team can run any gate** (unless `gates.approvers` restricts it) — the
  decision and approver are recorded in `audit.md`.
- **Commit `docs/qa/`** with your normal work — it is the reviewable history of QA decisions.
- **Pending DCPs** don't block you: provisional facts can guide tests but can't fail them.
  Review them with `/qa-domain review` before G3.
- **Repo-only mode** (`storage.platform.enabled: false`) is a good way to trial the flow
  without writing anything to ADO.
- **Guard hooks** run in the background: a blocked write or a "qa-guard" prompt explains why
  (secret in a file, direct domain edit, production URL, destructive click). See `hooks/README.md`.
