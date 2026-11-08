# 3. Credentials & test accounts

## The rules

1. **Secrets live only in a `.env` file in the project under test**, which must be gitignored.
   Never in `qa-trust.config.yaml`, never in `docs/qa/**`, never in `environments.yaml`.
2. **Shell / OS environment variables win** over the `.env` file. Use this for CI or to
   override a value temporarily.
3. **You type secrets into files yourself.** The framework never asks you to paste a token or
   password into the chat, and never prints or stores them in artifacts.
4. Config files hold only **non-secret** connection details (organisation URL, project,
   Test Plan ID) and **references** to secrets (e.g. `env:TEST_EMPLOYEE_PASS`).

The template is `config/.env.example`. Change the file name/location with
`secrets.envFile` in `qa-trust.config.yaml`.

## Azure DevOps PAT

### 1. Create the token

1. In Azure DevOps, open **User settings → Personal access tokens → New Token**.
2. **Organization:** the one in `platform.azure-devops.organization`.
3. **Expiration:** as short as your team's policy allows (e.g. 30–90 days).
4. **Scopes** → *Custom defined*:

   | Scope | Access | Why |
   |---|---|---|
   | Work Items | Read & Write | Read stories; write acceptance criteria, tags, comments, links |
   | Test Management | Read & Write | Create suites and test cases in Test Plans |

   Read-only trial? Use *Work Items: Read* only and set `storage.platform.enabled: false`
   (repo-only) — nothing is written to ADO.
5. Copy the token once — ADO won't show it again.

### 2. Put it in `.env`

```dotenv
# .env in the project under test (gitignored)
ADO_PAT=<your token>
ADO_ORG=your-org                          # organisation NAME only — used by the MCP server
# Optional overrides of qa-trust.config.yaml:
ADO_ORG_URL=https://dev.azure.com/your-org
ADO_PROJECT=YourProject
```

Quotes are optional; `export KEY=value` lines and trailing ` # comments` are accepted.

### 3. Non-secret settings stay in `qa-trust.config.yaml`

```yaml
platform:
  azure-devops:
    organization: "https://dev.azure.com/your-org"
    project: "YourProject"
    testPlanId: 1234            # or null to be asked on first sync
```

### How each tool gets the credentials

The framework talks to ADO in three ways. **Only the helper script reads `.env` itself.**

| Route | Used for | Reads `.env`? | How to give it credentials |
|---|---|---|---|
| Helper script `ado_testcase.py` | Test suites & test cases | ✅ yes (`--env-file`) | Nothing extra — `ADO_PAT` from `.env` |
| Azure DevOps MCP server (`.mcp.json`) | Work items, comments, links | ❌ no | `ADO_ORG` must be in the **environment of the shell that starts Claude Code** (it is expanded in `.mcp.json`). The server signs you in with its own (browser) login flow. |
| Azure CLI (`az boards`, `az devops`) | Fallback | ❌ no | `az login` / `az devops login`, or `AZURE_DEVOPS_EXT_PAT` in the shell |

To put `ADO_ORG` (or other variables) into the shell, pick one:

```powershell
# PowerShell — current session only
$env:ADO_ORG = "your-org"
claude --plugin-dir <path-to>/99x-qa-trust-architect
```

```bash
# bash/zsh — current session only
export ADO_ORG=your-org
claude --plugin-dir <path-to>/99x-qa-trust-architect
```

…or per project in `.claude/settings.local.json` (Claude Code keeps this file out of git):

```json
{ "env": { "ADO_ORG": "your-org" } }
```

### Rotating / revoking

- Expired or rotated token → edit `ADO_PAT` in `.env`; nothing else changes.
- Suspect a leak → revoke in ADO immediately, create a new one, update `.env`.
- Different person on the same project → each tester uses **their own** `.env` with their own PAT,
  so the ADO history shows who made each change.

## Test accounts (usernames & passwords)

Test accounts are needed when a tester or the AI logs into the application under test —
manual execution (`/qa-execute`), exploratory sessions and the live crawl (`/qa-explore`,
`/qa-domain crawl`, both through the Playwright MCP browser).

**The AI never sees or types a test account password.** It only knows *which* account a role
uses (the env-var name). Logging in is done by a person — in the browser window, or once up front
to record a reusable login session (below).

### 1. Values go in `.env` — one pair per role and environment

```dotenv
# Test accounts — names are your choice; keep ROLE + ENV in the name
TEST_EMPLOYEE_USER=employee1@test.example.com
TEST_EMPLOYEE_PASS=<password>
TEST_MANAGER_USER=manager1@test.example.com
TEST_MANAGER_PASS=<password>
STAGING_MANAGER_USER=...
STAGING_MANAGER_PASS=...
```

### 2. `environments.yaml` holds only references

`docs/qa/_project/domain/environments.yaml` (part of the reviewed domain context):

```yaml
environments:
  - name: test
    url: "https://test.example.com"
    agentsAllowed: true
    accounts:
      - { role: ROLE-employee, ref: "env:TEST_EMPLOYEE_USER", passwordRef: "env:TEST_EMPLOYEE_PASS" }
      - { role: ROLE-manager,  ref: "env:TEST_MANAGER_USER",  passwordRef: "env:TEST_MANAGER_PASS" }
  - name: prod
    url: "https://app.example.com"
    agentsAllowed: false        # agents never touch prod by default
```

Roles (`ROLE-…`) match `personas-roles.yaml`, so the AI can say "log in as the manager — the
account in `TEST_MANAGER_USER`" without ever reading the value. The `.env` entries are a shared,
gitignored place for testers to find the right account; nothing in the framework reads them.

### 3. How the browser gets logged in

Set `exploratory.auth.strategy` in `qa-trust.config.yaml`:

**`manual` (default — simplest and safest).** At the start of each session the AI opens the
application's login page in the Playwright browser window and asks you to log in as the role.
You type the credentials into the browser yourself; the AI checks the page shows you signed in
and carries on (autonomous mode starts only after that). The plugin's `playwright` MCP server runs
`--isolated`, so the login is forgotten when the browser closes.

**`storage-state` (for repeated or autonomous sessions).** Record a login once per role and
environment, then let a dedicated MCP server reuse it:

1. Record the session — a browser opens, you log in, close the browser:
   ```bash
   npx playwright codegen --save-storage=.auth/test-employee.json https://test.example.com
   ```
2. Add a per-role server to the **project's** `.mcp.json` (next to the plugin's default one):
   ```json
   {
     "mcpServers": {
       "playwright-employee": {
         "command": "npx",
         "args": ["-y", "@playwright/mcp@latest", "--isolated",
                  "--storage-state", ".auth/test-employee.json", "--output-dir", ".playwright-mcp"]
       }
     }
   }
   ```
3. Point the role at it in `qa-trust.config.yaml`:
   ```yaml
   exploratory:
     auth:
       strategy: storage-state
       roles:
         ROLE-employee: { mcpServer: playwright-employee }
   ```
4. Re-record when the session expires (you'll see the login page at the start of a session).

`.auth/*.json` files contain live session cookies — treat them like passwords: keep `.auth/`
gitignored, never commit or share them, delete them when the environment is refreshed. The AI never
opens them.

### 4. What the AI may do in the browser

- Only environments in `exploratory.environments.allowed` **and** marked `agentsAllowed: true` in
  `environments.yaml`; **production is always refused**.
- Only the environment's own web address plus `exploratory.allowedOrigins` (e.g. your SSO login page).
- Never click actions matching `exploratory.guards.blockActions` (delete, pay, send email, …) without
  asking you — in autonomous mode it skips them and lists them in the report.
- Time box and action limit per session (`maxSessionMinutes`, `maxActions`).
- Free text it enters is prefixed `QA-SES-xxx-…`, and records it creates are listed for cleanup.

### Good practice for test accounts

- Dedicated test accounts per role — never personal or production accounts.
- Least privilege: exactly the role being tested.
- Only in environments listed in `exploratory.environments.allowed` (default `dev`, `test`, `staging`).
- Accounts without MFA, or with a test-friendly MFA method agreed with your security team.
- Rotate passwords in `.env` when the environment is refreshed.

## Checklist

- [ ] `.env` exists in the project under test and `git check-ignore .env` prints `.env`
- [ ] `.auth/` and `.playwright-mcp/` are gitignored
- [ ] `ADO_PAT` has only *Work Items* and *Test Management* scopes and an expiry date
- [ ] `ADO_ORG` is set in the shell (or `.claude/settings.local.json`) for the MCP server
- [ ] `environments.yaml` contains only `env:` references, no real usernames/passwords
- [ ] Production has `agentsAllowed: false`
