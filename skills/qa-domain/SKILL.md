---
name: qa-domain
description: Build, refresh, query and govern the QA Trust Architect domain context of the application under test — build, refresh (staleness/AI-DLC changes), deepen a feature, ask a question about the domain, and review/accept/reject Domain Change Proposals (DCPs). Use when the user asks about the app's business rules, roles, features, or wants to review domain updates.
argument-hint: "build | refresh | deepen <F-id> | ask <question> | review | accept <DCP-ids|all-auto|all> | reject <DCP-id> <reason>"
---

# /qa-domain

`FRAMEWORK_ROOT` = two levels up from this skill's base directory. Read
`core/core-workflow.md` §0–1 and `core/domain-change-protocol.md` first.
Arguments: `$ARGUMENTS`

## build
Delegate to `qa-trust-architect:domain-analyst` (task `build`). If G0 is already approved,
use task `refresh` instead and say so.

## refresh
Delegate to `domain-analyst` (task `refresh`): recompute source hashes, mark stale facts,
raise re-verify DCPs, sync AI-DLC changes (`integrations/aidlc/integration.md` §2). Report counts.

## deepen <F-id>
Delegate to `domain-analyst` (task `deepen`). Output is DCPs.

## ask <question>
Answer from the domain context only (load via `core/context-loader.md`). For every fact used,
show its ID and status; say clearly when an answer rests on provisional facts. If unknown,
offer to add a question to `PROJECT_DIR/questions.md`.

## review
1. List pending DCPs grouped by level (critical → review), oldest first, flag conflicts and
   those older than `staleAfterDays`.
2. For each (or as a batch, if the user prefers): show the change diff, evidence, and **impact
   list** (artifacts referencing the fact — Grep the QA root for the fact ID).
3. Ask the user: accept / reject (reason) / defer.

## accept / reject
Apply per `domain-change-protocol.md` §7 (on accept: update file, propagate `needs-review`
flags, bump `domainVersion` minor once per batch, archive DCP, audit, optional platform
notification via sync-agent). Approver = the current user (confirm name once per session).
Respect `domain.owners` for critical levels: if an owner is configured and the user is not
that owner, warn (advisory) and record the override.
