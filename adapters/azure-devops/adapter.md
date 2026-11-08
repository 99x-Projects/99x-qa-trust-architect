# Azure DevOps Adapter (MVP)

**Config:** `platform.azure-devops` in `qa-trust.config.yaml`.
**Access, in order of preference:**
1. **Azure DevOps MCP server** (`.mcp.json` → `azure-devops`) — work items, comments, links,
   test plans where the server exposes them. Use the tool whose name matches the
   operation (e.g. work-item get/update/comment, test plan/suite/case tools). Check the
   available tool list at runtime; tool names vary by server version.
2. **Azure CLI** (`az boards`, `az devops invoke`) if logged in.
3. **Helper script** `scripts/ado_testcase.py` (stdlib Python, PAT from `ADO_PAT` env var)
   for Test Plans operations: `upsert-testcase`, `ensure-suite`, `add-to-suite`.

Never print or store the PAT.

## Credentials (`.env`)
- Secrets live in the project's env file (`secrets.envFile`, default `.env`), created from
  the plugin's `config/.env.example`. Organisation/project/test plan stay in `qa-trust.config.yaml`.
- Precedence: process environment > env file. The env file must be gitignored.
- The helper script loads it itself: always pass `--env-file <secrets.envFile>` and
  `--org-url/--project` from config.
- The MCP server and `az` CLI do **not** read `.env`. For them either log in interactively
  (`az login` / the MCP server's own auth flow), or export the variables in the shell before
  starting Claude Code, or set them in the project's `.claude/settings.local.json` → `env`
  (gitignored by Claude Code).

## Operations

| Operation | How |
|---|---|
| `testConnection` | MCP list projects / `az devops project show -p <project>` |
| `getWorkItem` | MCP get work item (expand relations) / `az boards work-item show --id <id> --expand relations` |
| `getLinkedItems` | Follow `relations` (`System.LinkTypes.Hierarchy-Reverse` = parent, `-Forward` = child, `System.LinkTypes.Related`, `ArtifactLink` = PR/commit) |
| `queryWorkItems` | WIQL via MCP / `az boards query --wiql "<WIQL>"` |
| `getFieldValues` | `az devops invoke --area wit --resource fields` or MCP field tools |
| `updateAcceptanceCriteria` | Update field `Microsoft.VSTS.Common.AcceptanceCriteria` (HTML; render Markdown → HTML, Gherkin in `<pre>`) |
| `addComment` | MCP add comment / `az devops invoke --area wit --resource comments` |
| `setGateStatus` | `gateStatusField: tag` → replace any `qa-gate:Gx-*` tag in `System.Tags` with `qa-gate:Gx-<decision>` (tags are `; `-separated). `custom-field` → set `customFieldRef` to `Gx-<decision>` |
| `ensureSuite` | `scripts/ado_testcase.py ensure-suite --plan <testPlanId> --requirement <id>` → requirement-based suite (auto-shows Tested By cases) |
| `upsertTestCase` | `scripts/ado_testcase.py upsert-testcase --input <tc.json> --requirement <id>` |
| `linkItems` | Test case → story relation `Microsoft.VSTS.Common.TestedBy-Reverse` (done by upsert when `--requirement` given) |
| `listTestCases` | `az devops invoke --area testplan --resource suiteTestCase` or MCP test plan tools |
| `createWorkItem` | MCP create / `az boards work-item create --type Task --title ... --fields System.Tags=qa-automation` |
| `createDefect` | `scripts/ado_testcase.py create-bug --input <def.json> --key <workItemKey> [--requirement <storyId>] [--test-cases <ADO TC ids>] [--attach <files>...] [--type <defectType>]` — idempotent via tag `qa-def:<key>/<DEF-id>` |
| `getDefectStatus` | `scripts/ado_testcase.py get-states --ids 1,2,3` (or MCP get work items) |
| `updateDefect` | `scripts/ado_testcase.py comment --id <id> --text-file <md>` [+ `--state <state>`]; or MCP comment/update |
| `publishTestRun` | `scripts/ado_testcase.py publish-run --input <run.json> --plan <testPlanId> --suite <suiteId>` |

If `testPlanId` is null, ask the user which Test Plan to use (or to create one) the first
time `ensureSuite` runs; offer to save the answer into config.

## Test case conversion (canonical → ADO)

See `mapping.yaml` → `testCase`. Summary:
- **Rule-table TC:** each `steps[]` → ADO step (action / expected). `data` rows →
  rendered as a Markdown/HTML table in `System.Description` and `<col>` placeholders
  converted to `@col` parameters in step text. (Native shared parameters: v3.)
- **Gherkin TC:** `Given` lines → one step "Preconditions: …" (no expected);
  each `When`/`And` (before Then) → action step; `Then`/`And` (after Then) → expected result
  of the preceding action step. Scenario Outline `Examples` → same parameter handling as data rows.
  The original Gherkin is kept in `System.Description` for reference.
- Tags: `qa-trust`, `TC-xxx`, `AC-xx`, technique, `provisional` when basis is provisional.

The helper script performs these conversions; the agent passes the TC as JSON
(convert the YAML file to JSON first).

## Defects (canonical → ADO)

See `mapping.yaml` → `defect`. The helper builds:
- **Type** `platform.azure-devops.defectType` (default `Bug`; `Issue` in the Basic process —
  Basic has no Repro Steps/Severity fields, so steps go into Description and severity into a tag).
- **Title** `DEF-xxx <title>`; **Repro Steps** (HTML): numbered steps, expected (with AC/BR ids),
  actual, environment/build, traces, evidence list; **System Info**: environment, build.
- **Severity** via `mapping.yaml → severity`; **Priority** 1–4.
- **Tags** `qa-trust; qa-def:<key>/<DEF-id>; <feature ids>`.
- **Links** `System.LinkTypes.Related` → story (`defectLinkToRequirement: related`);
  `Microsoft.VSTS.Common.TestedBy-Forward` → each ADO test case.
- **Area/Iteration** copied from the story when `copyAreaIteration: true`.
- **Attachments**: each evidence file uploaded (`wit/attachments`) and linked as `AttachedFile`.

## Test runs (canonical → ADO)

`publish-run` input:
```json
{ "name": "ADO-1234 CY-01 build 1.4.2 (test)", "build": "1.4.2", "environment": "test",
  "results": [ { "testCaseId": 8812, "outcome": "failed", "comment": "RUN-003: …",
                 "bugIds": [9921], "durationMs": 360000, "runBy": "Jane Tester" } ] }
```
It finds the test point of each test case in the suite, creates a run for those points, updates
each result (outcome `passed→Passed, failed→Failed, blocked→Blocked, skipped/not-run→NotExecuted`,
state Completed, comment, associated bugs) and completes the run. Output:
`{"runId": 77, "results": {"8812": 100000}}` → stored on each `RUN-xxx.yaml` under
`externalIds.azure-devops`. Test cases not in the suite are reported back as `skipped`
(run `ensure-suite`/`add-to-suite` first).
