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

## 4. Plan — G2

`/qa-continue 1234` → `risk-gap-analyst` writes `risk-assessment.md`, `gap-analysis.md`,
`test-plan.md` → `/qa-gate G2 1234`.

## 5. Design — G3

`/qa-continue 1234` → `test-designer` writes `2-design/test-cases/TC-*.yaml` (Gherkin or rule
table, each traced to an AC) and `test-data.md`; `automation-analyst` writes `automation-gap.md`;
observability plan if relevant → `/qa-gate G3 1234`.

On approval: a requirement-based suite is created in your Test Plan and test cases are
created/updated with steps and linked to the story (*Tested By*). IDs are written back into
the YAML files so re-syncing updates instead of duplicating.

## 6. Check status any time

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
