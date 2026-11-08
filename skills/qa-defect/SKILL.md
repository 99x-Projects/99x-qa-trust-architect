---
name: qa-defect
description: Manage QA Trust Architect defects for a work item (stage 3.3) — list drafts and open defects, confirm/reject/mark duplicate/defer drafted defects (a tester must confirm before anything is created on Azure DevOps), create confirmed defects on the platform with evidence and links, refresh their platform status, retest fixes, and record accepted risks. Use when a tester wants to review, log, retest or close bugs found during testing.
argument-hint: "[work-item-id] list | draft <RUN-id> | confirm [DEF-ids|all-drafts] | reject <DEF> <reason> | duplicate <DEF> <platform-id> | defer <DEF> <reason> | accept <DEF> <risk> | refresh | retest <DEF>"
---

# /qa-defect

`FRAMEWORK_ROOT` = two levels up from this skill's base directory. Arguments: `$ARGUMENTS`

Read `core/core-workflow.md` §0–1 and `rules/phase-3-execution/3.3-defect-management.md`.
Resolve the work item (default: most recent, confirm). Confirm the tester's name once.

| Sub-command | Behaviour |
|---|---|
| `list` (default) | Show `defect-log.md` sections: drafts, open, not-raised (oracle). |
| `draft <RUN-id>` | Delegate `triage` + `draft-defects` for that run to `qa-trust-architect:execution-analyst`. |
| `confirm [ids\|all-drafts]` | For each draft show title, severity, expected vs actual (with AC/BR), oracle check, known quirk, possible duplicates. Ask per defect: confirm / edit / reject / duplicate / defer. `all-drafts` still lists every defect before one confirmation. On confirm set `confirmedBy/At`, audit `DEFECT-CONFIRMED`; then, if the platform is enabled, delegate creation to `qa-trust-architect:sync-agent` (operation `createDefect`, dry run shown first in the session) and write back IDs (`status: logged`). |
| `reject <DEF> <reason>` | `status: rejected`, resolution; if the cause was a wrong TC → mark the TC `needs-review`. |
| `duplicate <DEF> <id>` | `status: duplicate`, resolution `duplicate of <id>`; optionally add a comment with the new evidence to the existing platform defect (ask). |
| `defer` / `accept <DEF> <risk>` | Requires reason/named risk and owner; `accepted` is recorded for G4 C3. Never for Sev1 without explicit "yes, accept Sev1". |
| `refresh` | Read platform states (adapter `getDefectStatus`) → `platformState`, map to `fixed`; summarise changes. |
| `retest <DEF>` | Run the linked TC(s) via `/qa-execute <id> --tc … --set retest` (retestOf DEF). Pass → `retest-passed`, offer a platform comment/state change (confirm); fail → `retest-failed`, offer re-activation with comment (confirm). |

Afterwards delegate `refresh-logs`; report ≤ 8 lines. Never create, close or reopen anything on
the platform without the tester saying yes in this conversation.
