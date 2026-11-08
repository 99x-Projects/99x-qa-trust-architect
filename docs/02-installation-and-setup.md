# 2. Installation & setup

## Prerequisites

| Tool | Needed for | Check |
|---|---|---|
| **Claude Code** | Everything | `claude --version` |
| **Git** | Detecting project history, tracking artifacts | `git --version` |
| **Python 3.8+** | Azure DevOps test case helper (`adapters/azure-devops/scripts/ado_testcase.py`, standard library only) | `python --version` |
| **Node.js 18+** (`npx`) | Azure DevOps MCP server | `npx --version` |
| Azure CLI + `azure-devops` extension *(optional)* | Fallback route for some ADO operations | `az devops -h` |
| Azure DevOps access | Read work items; write work items and Test Plans | A PAT — see [page 3](03-credentials-and-test-accounts.md) |

## Step 1 — Get the plugin

Clone the framework once, anywhere on your machine:

```bash
git clone https://github.com/99x-Projects/99x-qa-trust-architect.git
```

## Step 2 — Start Claude Code in the project under test with the plugin loaded

Open a terminal **in the project you want to test** (not in the plugin folder) and run:

```bash
claude --plugin-dir <path-to>/99x-qa-trust-architect
```

Check it loaded: type `/qa-` — you should see `qa-init`, `qa-start`, `qa-gate`, …

> Installing through a plugin marketplace (`/plugin install`) will be possible once a
> marketplace entry is published. Until then use `--plugin-dir`.

## Step 3 — Prepare secrets *before* `/qa-init`

1. Copy the template into the project under test:
   ```bash
   cp <path-to>/99x-qa-trust-architect/config/.env.example .env
   ```
2. Make sure `.env` is gitignored in **that** project (add `.env` and `.auth/` to its `.gitignore`).
3. Fill in `ADO_PAT` (and `ADO_ORG`) in your editor.
4. For the Azure DevOps MCP server, also set `ADO_ORG` in your shell — see
   [page 3](03-credentials-and-test-accounts.md#how-each-tool-gets-the-credentials).

`/qa-init` will offer to create `.env` for you if it is missing, but it will never ask you
to paste a token into the chat — you always fill it in yourself.

## Step 4 — Run `/qa-init`

`/qa-init` runs **Phase 0**:

| Stage | What happens | You do |
|---|---|---|
| 0.1 Workspace detection | Detects project type, stack, tests, CI, platform, environments, AI-DLC, observability, secrets file | Answer a few multiple-choice setup questions (platform/org/project, Test Plan ID, artifact folder, testers, allowed environments, AI-DLC mode) |
| Connection test | Reads one work item you name | If it fails you can continue in repo-only mode |
| 0.2 Domain discovery | `domain-analyst` builds the domain context (skeleton for all features, deep for the riskiest) | Wait — large repos take a while |
| 0.3 QA reverse engineering *(existing projects)* | Inventories existing tests, maps them to features, finds coverage gaps | — |
| 0.4 Quality standards | Drafts definitions of done, severity scale, AC style, naming | Review |

It creates in the project under test:

```
qa-trust.config.yaml                 ← framework config (commit this)
.env                                 ← secrets (never commit)
docs/qa/_project/
  qa-profile.yaml                    ← what was detected
  questions.md                       ← interview questions for you
  domain/                            ← domain context (glossary, roles, features, rules, …)
  qa-baseline.md, feature-test-map.yaml   ← existing projects only
  quality-standards.md
  audit.md
```

## Step 5 — Answer questions and approve the baseline (G0)

1. Open `docs/qa/_project/questions.md` and fill in the `[Answer]:` slots
   (each question has options and a suggested answer).
2. Optional: `/qa-domain review` to go through what was learnt.
3. `/qa-gate G0` — read → analyse → decide. Approving G0 sets the domain version to `1.0.0`.

You are ready to start on work items: see [Daily workflow](06-daily-workflow.md).

## Configuration reference

`qa-trust.config.yaml` lives at the root of the project under test. The fully commented
example is `config/qa-trust.config.example.yaml`; the schema is
`schemas/qa-trust.config.schema.json`. The settings you are most likely to change:

| Setting | Default | Change it to… |
|---|---|---|
| `storage.repo.path` | `docs/qa` | Put QA artifacts somewhere else |
| `storage.repo.layout` | `{workItemKey}/` | Group by epic: `{epic}/{workItemKey}/`; AI-DLC: `{intent}/{unit}/` |
| `storage.platform.enabled` | `true` | `false` for repo-only |
| `storage.syncMode` | `on-gate` | `on-demand` (only via `/qa-sync`) or `manual` |
| `secrets.envFile` | `.env` | A different env file path |
| `platform.azure-devops.testPlanId` | `null` | An existing Test Plan ID (otherwise you're asked the first time) |
| `platform.azure-devops.gateStatusField` | `tag` | `custom-field` + `customFieldRef` |
| `gates.mode` / `gates.perGate` | `advisory` | e.g. `{ G4: blocking }` |
| `gates.approvers` | any tester | Restrict a gate, e.g. `{ G4: ["qa-lead"] }` |
| `acceptanceCriteria.formats` | Gherkin + rule table | Restrict to one |
| `routing.rules` | bugs → light, epics/payments/PII → comprehensive | Your own tier rules |
| `domain.discovery.mode` | `auto` | Force `docs-led` or `evidence-led` |
| `domain.owners` | any tester | e.g. `{ business-rules: ["product-owner"] }` |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `/qa-*` commands don't appear | Start Claude Code with `--plugin-dir` pointing at the plugin folder (the one containing `.claude-plugin/`). |
| "Config missing — run /qa-init" | You are not in the project root, or `/qa-init` has not been run there. |
| Connection test fails (401) | PAT missing/expired or wrong scopes — see [page 3](03-credentials-and-test-accounts.md). |
| MCP server fails to start | `ADO_ORG` not set in the shell that started Claude Code, or Node.js/`npx` missing. The helper script and repo-only mode still work. |
| `.env` warning: not gitignored | Add `.env` to the project's `.gitignore` — `/qa-init` offers to do this. |
