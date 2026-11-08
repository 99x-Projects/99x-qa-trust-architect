---
name: qa-execute
description: Execute QA Trust Architect test cases for a work item (Phase 3) — open a test cycle on a build and environment, check entry criteria, run manual test cases step by step in chat or via an offline execution sheet, import automated test results (JUnit/TRX), and record runs with evidence. Use when a tester wants to execute tests, record results, run regression, or import pipeline results.
argument-hint: "[work-item-id] [--tc TC-001,TC-002] [--set planned|regression|retest] [--sheet | --ingest] [--import <result-file>] [--env <name>] [--build <ver>]"
---

# /qa-execute

`FRAMEWORK_ROOT` = two levels up from this skill's base directory. Arguments: `$ARGUMENTS`

Execution needs a human — run it **in this conversation**; delegate only preparation,
ingestion, triage and imports to `qa-trust-architect:execution-analyst`.

1. Read `core/core-workflow.md` §0–1 and `rules/phase-3-execution/3.2a-manual-execution.md`.
   Bootstrap; resolve the work item (default: most recent, confirm).
2. **Preconditions:** G3 decided? If not: advisory → explain, ask to proceed (record `overridden`
   per `core/gate-protocol.md` §3); blocking → stop. Mark stage 3.2a `in-progress` (3.1 →
   `not-implemented`, non-blocking).
3. **Tester name:** confirm (suggest `git config user.name`).
4. **Cycle:** reuse the open cycle for the same build+environment, else open a new `CY-xx`
   (ask build/env; default env `execution.defaultEnvironment`). Delegate `prepare-cycle` to
   execution-analyst (entry criteria + execution list). Show entry criteria; unmet → ask to proceed
   (record met-with-risks).
5. **Mode:**
   - `--import <file>` → delegate `import-results` (3.4 §3); go to 7.
   - `--sheet` → delegate execution-sheet generation; tell the tester the file path and to run
     `/qa-execute <id> --ingest` when done. Stop.
   - `--ingest` → delegate `ingest-sheet`; ask the tester the ambiguous entries; go to 7.
   - otherwise ask interactive vs sheet if `execution.manualMode: ask`.
6. **Interactive loop** (3.2a §2): one TC at a time from the list (or `--tc`), show steps and the
   account **role reference** (never values), take per-step results, collect evidence paths, write
   `RUN-xxx.yaml` immediately, audit `RUN-RECORDED`. After each failure ask: draft defect now or at
   the end? Let the tester say `pause` at any time — the cycle stays open.
7. **Wrap-up:** delegate `refresh-logs`; for failures delegate `triage` + `draft-defects` (if
   `execution.defects.autoDraft`). Report (≤ 10 lines): executed/passed/failed/blocked, drafts awaiting
   confirmation (→ `/qa-defect confirm`), next step (`--set regression`, or `/qa-continue` for 3.4/3.5).
8. `execution.publishRuns: after-session` and platform enabled → offer `/qa-sync <id> --what runs`.
