---
name: qa-status
description: Show QA Trust Architect status — for a work item (tier, stages, gates, open questions, AC coverage, overrides, sync state) or for the project (G0, domain version, pending/old DCPs, stale facts, discrepancies, AI-DLC integration, all active work items). Use when the user asks where QA stands or what's next.
argument-hint: "[work-item-id | --project]"
---

# /qa-status

`FRAMEWORK_ROOT` = two levels up from this skill's base directory. Arguments: `$ARGUMENTS`

Read-only (except refreshing stale flags). Read `core/core-workflow.md` §1 and §8.

**Work item view:** tier (+reason), stage table, gate table (incl. overridden/stale), questions
open/blocking, AC coverage (ACs with ≥ 1 TC, from `test-case-index.md`), provisional AC/TC count,
pending DCPs raised by the item, `followUps`, sync table summary, next step.
In Phase 3 also: current cycle (build/env), executed/passed/failed/blocked of planned TCs,
regression pass rate, untriaged failures, defects by status and severity (drafts awaiting
confirmation highlighted; refresh platform states first if `execution.defects.refreshStatusOnStatus`),
unpublished runs, exploratory charters (planned / done / skipped; mandatory high-risk ones outstanding)
and sessions with open findings.

**Project view** (`--project` or no active item): G0 status, `domainVersion`, features
skeleton/deep, rules by status, open discrepancies, pending DCPs by level with age (flag
> `staleAfterDays`), stale facts (recompute source hashes — sample if > 200 sources),
AI-DLC detection/mode and changed mapped artifacts, list of work items with current stage/gate.

Keep the output compact: tables, ≤ 30 lines.
