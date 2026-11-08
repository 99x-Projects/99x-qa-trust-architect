---
name: qa-sync
description: Sync QA Trust Architect artifacts for a work item with the configured platform (Azure DevOps in MVP) — push acceptance criteria, test cases, suites, links, gate status; or check drift. Use when the user wants to publish/push QA artifacts to ADO/Jira/GitHub on demand.
argument-hint: "[work-item-id] [--what ac|tests|gates|all] [--check]"
---

# /qa-sync

`FRAMEWORK_ROOT` = two levels up from this skill's base directory. Arguments: `$ARGUMENTS`

1. Read `core/core-workflow.md` §1, §7 and `adapters/adapter-interface.md`.
2. If `storage.platform.enabled: false` → say so and stop.
3. Build the operation set from `--what` (default `all` = everything whose gate is approved /
   approved-with-risks). Warn if syncing artifacts behind an undecided/overridden gate and ask.
4. Delegate to `qa-trust-architect:sync-agent`; show its dry-run list; confirm with the user;
   execute.
5. `--check`: report drift between repo hashes and the platform (MVP: test cases only, best effort).
6. Report results.
