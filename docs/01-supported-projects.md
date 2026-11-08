# 1. Supported projects

## Project types

| Project type | Supported | How it is handled |
|---|---|---|
| **New project (greenfield)** — little or no code yet, requirements being written | ✅ MVP | Domain context is built *docs-led* from the PRD / specs / stories. No QA reverse engineering. |
| **Existing project with requirement documents** | ✅ MVP | *Docs-led* domain discovery: facts come from the documents, then are checked against code, tests and tracker history. Conflicts go to `discrepancies.md`. |
| **Existing project without written requirements** | ✅ MVP | *Evidence-led* domain discovery: facts are inferred from code, tests, data model, UI text, error messages and tracker history, then confirmed with you in a short targeted interview. |
| **Mixed** — some areas documented, some not | ✅ MVP | `discovery.mode: auto` picks docs-led or evidence-led **per feature**. |
| **Project already using AWS AI-DLC** | ✅ MVP (companion mode) | Detects `aidlc-docs/`, reads AI-DLC artifacts as documentation, never modifies them. Gate alignment and write-back come in v2. |

Detection is automatic in `/qa-init` (stage 0.1) and you confirm the result. See
[Existing projects](04-existing-projects.md) for details.

## Work item platforms

| Platform | Status | What it does |
|---|---|---|
| **Azure DevOps** (Boards + Test Plans) | ✅ MVP | Reads work items; writes acceptance criteria, gate status (tag or custom field), comments; creates requirement-based test suites and test cases linked to the story (*Tested By*). |
| **Repo only** (no platform) | ✅ MVP | Set `storage.platform.enabled: false`. All artifacts stay as files in the repo. Useful for trials or when you don't have write access yet. |
| **Jira + Xray** | 🔜 v2 | Design in `adapters/jira-xray/`. |
| **GitHub Issues** | 🔜 v3 | Design in `adapters/github/`. |

Artifacts are **always** written to the repo (default `docs/qa/`, configurable). The
platform is a sync target; `storage.sourceOfTruth` decides who wins on conflicts.

## Tech stacks

The framework analyses your repository by reading files, so it is **language-agnostic**.
Stage 0.1 recognises, among others:

- **Manifests:** `package.json`, `*.csproj`/`*.sln`, `pom.xml`, `build.gradle`,
  `pyproject.toml`, `requirements.txt`, `go.mod`, `Gemfile`
- **Test frameworks:** xUnit/NUnit/MSTest, Jest/Vitest, Playwright/Cypress/Selenium, pytest,
  JUnit, SpecFlow/Reqnroll/Cucumber (`.feature`), k6/JMeter, Postman
- **CI/CD:** GitHub Actions, Azure Pipelines, GitLab CI, Jenkins
- **Contracts:** OpenAPI/Swagger, GraphQL, DB migrations, ORM models
- **Observability:** Application Insights, OpenTelemetry, Datadog, Grafana/Prometheus, ELK, Sentry

Anything not recognised is still read as plain source — detection is a head start, not a limit.

## What's in each release

| Area | MVP (0.1) | Later |
|---|---|---|
| Setup & domain (Phase 0, G0) | ✅ incl. docs-led + evidence-led discovery, DCPs | Live app crawl via Playwright (v2) |
| Requirements → AC → risk → gaps → plan (Phase 1, G1, G2) | ✅ | — |
| Test case design (2.1, G3) | ✅ | — |
| Test data, automation gap, observability design (2.2–2.4) | Draft rules | Hardened in v2 |
| Execution: manual, automation, defects, regression (Phase 3, G4) | Stubs | v2 |
| Exploratory testing via Playwright MCP (3.2b) | Design only | v2 |
| Release verification, escape analysis, metrics (Phase 4, G5) | Stubs | v4 |
| Gates | Advisory | Per-gate *blocking* option already in config |

## Not supported (by design)

- Running agents against **production** — blocked by default (`environments.yaml → agentsAllowed: false`).
- Storing secrets in config or artifacts — secrets live only in a gitignored `.env`
  (see [Credentials & test accounts](03-credentials-and-test-accounts.md)).
- Creating defects without a human confirming them.
