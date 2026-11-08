---
name: qa-continue
description: Resume the QA Trust Architect lifecycle for a work item from its qa-state.md — process answered questions, then run the next stage(s) up to the next gate. Use when the user has answered questions, approved a gate, or says continue/next for a QA work item.
argument-hint: "[work-item-id] [--tier <tier>]"
---

# /qa-continue

`FRAMEWORK_ROOT` = two levels up from this skill's base directory. Arguments: `$ARGUMENTS`

1. Read `core/core-workflow.md`; bootstrap. If no work item given, use the most recently
   updated `qa-state.md` under the QA root and confirm it with the user.
2. `--tier` given → record `TIER-OVERRIDE` in audit, regenerate stage list (`routing-rules.md`).
3. **Answers:** process answered questions (`core-workflow.md` §4) — delegate re-work to the
   agent that owns the affected stage.
4. **Next stage:** from `qa-state.md`, find the first stage not `done`/`skipped`.
   - If a gate precedes it and is undecided: in `advisory` mode explain the unmet gate and ask
     "run `/qa-gate Gx` now, or proceed (override)?" — on proceed, record `overridden` with
     reason per `core/gate-protocol.md` §3. In `blocking` mode, stop.
   - Stage not implemented: if its rule file says **non-blocking** (3.1, 3.2b until slice B) → mark
     `not-implemented`, say so in one line, continue; otherwise say so, mark it, stop.
5. Run stages until the next gate by delegating (`core-workflow.md` §9):
   1.4–1.6 → `risk-gap-analyst`; 2.1–2.2 → `test-designer`; 2.3 → `automation-analyst`;
   2.4 → `risk-gap-analyst`. Skip stages the tier excludes.
   **Phase 3** needs the tester: 3.2a → hand over to `/qa-execute` (tell the user, don't simulate
   execution); 3.3 → `/qa-defect` for drafts awaiting confirmation; 3.4 → delegate
   `select-regression` to `execution-analyst`, then ask the tester to run it (`/qa-execute --set
   regression` / `--import`); 3.5 → delegate `summary` to `execution-analyst` once 3.2a–3.4 are
   done (or the tester says execution is complete), then point to `/qa-gate G4`.
6. Check DCP impact flags (`followUps` in `qa-state.md`) and mention them.
7. Report (≤ 10 lines) and point to the next gate.
