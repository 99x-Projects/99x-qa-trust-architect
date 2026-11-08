---
name: qa-gate
description: Run a QA Trust Architect gate (G0–G5) for a work item or the project — build the gate pack (checklist met/unmet with evidence, open questions, pending DCPs, overrides), let the approver interrogate the artifacts, record the decision (approved, approved-with-risks, rejected, overridden) with audit trail, and sync to the platform. Use when the user wants to review, approve, sign off or reject QA artifacts.
argument-hint: "<G0|G1|G2|G3|G4|G5> [work-item-id]"
---

# /qa-gate

`FRAMEWORK_ROOT` = two levels up from this skill's base directory. Arguments: `$ARGUMENTS`

Gates must run **in this conversation** (never delegate the decision).

1. Read `core/core-workflow.md` §0–1, `core/gate-protocol.md`, and the gate checklist
   `gates/<Gx>-*.md`. G0 is project-level; G1–G5 need a work item (default: most recent, confirm).
2. G5 → not implemented yet (v4): say so and stop. **G4:** if `3-execution/test-summary-report.md`
   is missing or older than the latest run/defect file, offer to (re)generate it first (delegate
   `summary` to `qa-trust-architect:execution-analyst`); refresh defect states from the platform.
   Use the decision wording GO / GO with risks / NO-GO from the G4 checklist.
3. **Approver:** check `gates.approvers` (default any tester). Ask for / confirm the approver's
   name (suggest `git config user.name`). If restricted and the user isn't listed → advisory:
   warn and allow with recorded override; blocking: stop.
4. **Read:** evaluate every checklist item against the artifacts — honestly, citing file/section.
   Present the gate pack (format in gate-protocol §2 Step 1), including pending DCPs from this
   item, open questions, earlier overrides, stale gates, and the domain version.
5. **Analyse:** answer the approver's questions from the artifacts and domain context. If they
   want fixes before deciding, make them (or delegate to the stage's agent), then re-evaluate.
6. **Decide:** ask for exactly one of approved / approved-with-risks / rejected (+ return stage)
   / overridden (+ reason). `approved` only if all items are met.
7. **DCPs in the pack:** ask accept/reject/defer for each (bulk allowed); apply via `/qa-domain`
   accept/reject logic.
8. **Record:** `gates/<Gx>.md` from `templates/gate-record.md` (with artifact sha256 hashes),
   `audit.md` line, `qa-state.md` gate table.
9. **Sync:** if approved/approved-with-risks and platform enabled with `syncMode: on-gate`,
   delegate to `qa-trust-architect:sync-agent` with the gate's sync set. Show the dry-run list
   and confirm with the user before the first platform write in this session.
10. Report the decision and the next step (`/qa-continue`).
