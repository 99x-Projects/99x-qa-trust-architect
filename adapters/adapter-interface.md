# Adapter Interface

Every work item platform adapter implements these operations against the canonical
model in `schemas/`. Agents call operations **by name**; the adapter's `adapter.md`
says how to perform each one (MCP tool, CLI, or helper script) and `mapping.yaml`
says how fields map.

| Operation | Input | Output | Used by | Release |
|---|---|---|---|---|
| `testConnection` | – | ok / error | 0.1 | MVP |
| `getWorkItem` | platformId | canonical work item | 1.1 | MVP |
| `getLinkedItems` | platformId, relations | canonical work items | 1.1 | MVP |
| `queryWorkItems` | query (type, area, date range, tags) | list | 0.2 (tracker history), 0.3 | MVP |
| `getFieldValues` | field | allowed values | 0.4 (severity mapping) | MVP |
| `updateAcceptanceCriteria` | platformId, markdown | ok | G1 sync | MVP |
| `addComment` | platformId, markdown | comment id | gates, DCP notify | MVP |
| `setGateStatus` | platformId, gate, decision | ok | gates | MVP |
| `ensureSuite` | work item | suite id | G2 sync | MVP |
| `upsertTestCase` | canonical TC (+ externalId?) | platform id | G3 sync | MVP |
| `linkItems` | from, to, relation | ok | G3 sync | MVP |
| `listTestCases` | scope (plan/suite/area) | list (id, title, steps) | 0.3 | MVP |
| `getTestCase` | platform id | canonical TC + hash | drift detection | v3 |
| `createWorkItem` | type, fields | id | automation backlog (2.3) | MVP (optional) |
| `createDefect` | canonical defect (status confirmed + confirmedBy) | id | 3.3 | v2 |
| `getDefectStatus` | platform ids | id → state | 3.3, 3.5, /qa-status | v2 |
| `updateDefect` | id, comment, optional state | ok | 3.3 retest (tester-confirmed) | v2 |
| `publishTestRun` | runs of one cycle (TC platform ids, outcomes) | run id, result ids | G4 sync, `/qa-sync --what runs` | v2 |

## Rules for all adapters
1. **Idempotent upserts.** If the canonical object has `externalIds.<platform>`, update;
   else create and write the new ID back into the repo file.
2. **Never store secrets** in repo files. Credentials come from environment variables
   or the MCP server's own auth.
3. **Content hash.** After a successful upsert store `contentHash` (sha256 of the
   canonical content) so drift can be detected later.
4. **Fail soft.** On error, keep repo artifacts as they are, record `SYNC` failure in
   `audit.md` and in `qa-state.md` sync table, and tell the user. Never block the gate decision.
5. **Confirm outward writes the first time** in a session (show what will be written).
6. Respect `storage.sourceOfTruth`: when `platform`, read back from the platform before
   editing repo files and treat the platform copy as authoritative on conflicts.
7. **Defects need a human.** `createDefect` and `updateDefect` refuse input without
   `confirmedBy` (create) or an explicit tester confirmation from the orchestrator (update).
