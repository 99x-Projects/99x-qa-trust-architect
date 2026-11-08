---
name: qa-start
description: Start the QA Trust Architect lifecycle for a work item (or AI-DLC unit) — fetch it from Azure DevOps/Jira/GitHub, convert to the canonical model, decide the tier, and run Phase 1 (intake, requirement analysis, acceptance criteria) up to gate G1. Use when the user wants to start QA, analyse requirements, or write acceptance criteria for a story/bug/feature.
argument-hint: "<work-item-id | url | aidlc-unit> [--tier light|standard|comprehensive]"
---

# /qa-start

`FRAMEWORK_ROOT` = two levels up from this skill's base directory. Arguments: `$ARGUMENTS`

1. Read `FRAMEWORK_ROOT/core/core-workflow.md` and bootstrap (§1). If config is missing →
   tell the user to run `/qa-init` and stop. If G0 is not decided, warn (advisory) and ask
   whether to proceed; if yes record `G0 overridden` with reason.
2. Resolve the work item: ID or URL → platform via adapter (`getWorkItem`, `getLinkedItems`);
   AI-DLC unit name → per `integrations/aidlc/integration.md` §2. Convert to canonical JSON
   per the adapter `mapping.yaml`.
3. If `ITEM_DIR` already exists with a `qa-state.md`, switch to `/qa-continue` behaviour.
4. Create `ITEM_DIR` from templates (`qa-state.md`, `audit.md`, `questions.md`, `gates/`,
   `1-inception/`, `2-design/`).
5. Delegate stages 1.1 → 1.2 → 1.3 to `qa-trust-architect:requirement-analyst`
   (one delegation for all three, or one per stage if the item is large). Pass the canonical
   work item JSON, tier override if given, paths, config excerpts.
6. Update `qa-state.md` (stages, tier) and `audit.md`.
7. Report (≤ 10 lines): tier + reason, REQ/AC counts, requirement quality score, open
   questions (blocking), DCPs raised, and next step:
   - blocking questions → "Answer in `<ITEM_DIR>/questions.md`, then `/qa-continue`"
   - otherwise → "Review and run `/qa-gate G1`"
