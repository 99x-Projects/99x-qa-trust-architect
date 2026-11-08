# QA Trust Architect

A gated, AI-assisted **QA lifecycle** for Claude Code, inspired by AWS AI-DLC.
The AI drafts every QA artifact and asks the questions it cannot answer; humans
answer, review and approve at defined **gates**. Everything is persisted as files
in the repo (state + audit), and optionally synced to your work item platform.

- Works on **new** (greenfield) and **existing** (brownfield) projects
- **Platform-agnostic**: Azure DevOps (MVP), Jira + Xray (v2), GitHub (v3)
- **Domain-aware**: every agent works from a shared, reviewed *domain context*
- **AI-DLC compatible**: detects `aidlc-docs/` and reuses its artifacts (companion mode)
- **Adaptive**: Light / Standard / Comprehensive tiers decide which stages run
- **Advisory gates** by default: warn, record overrides, never silently skip

## Lifecycle

```
PHASE 0  SETUP       0.1 Workspace detection · 0.2 Domain discovery
                     0.3 QA reverse engineering (brownfield) · 0.4 Quality standards   ──► G0 QA Baseline
PHASE 1  INCEPTION   1.1 Intake · 1.2 Requirement analysis · 1.3 Acceptance criteria    ──► G1 Ready for Test Design
                     1.4 Risk & impact · 1.5 Gap analysis · 1.6 Test strategy & plan   ──► G2 Test Plan Approved
PHASE 2  DESIGN      2.1 Test cases · 2.2 Data & env · 2.3 Automation gap · 2.4 Observability ──► G3 Test Design Approved
PHASE 3  EXECUTION   3.2a Manual · 3.2b Exploratory · 3.3 Defects · 3.4 Regression · 3.5 Summary ──► G4 Quality Sign-off
                     (3.1 Automation implementation: v4)
PHASE 4  OPERATIONS  4.1 Release verification · 4.2 Observability validation · 4.3 Escape analysis · 4.4 Retro ──► G5 Release Closure
```

## Commands

| Command | Purpose |
|---|---|
| `/qa-init` | Phase 0 setup: detect workspace, write `qa-trust.config.yaml`, kick off domain discovery |
| `/qa-domain build\|refresh\|crawl\|ask\|review\|accept\|reject` | Build and maintain the domain context; review Domain Change Proposals (DCPs) |
| `/qa-start <work-item-id>` | Intake a work item, choose tier, start Phase 1 |
| `/qa-continue [work-item-id]` | Resume from `qa-state.md` |
| `/qa-gate <G0..G5> [work-item-id]` | Read → analyse → decide → record a gate |
| `/qa-status [work-item-id]` | State, gates, coverage, pending DCPs, stale domain areas |
| `/qa-sync [work-item-id]` | Push/pull artifacts with the work item platform |
| `/qa-execute [id] [--sheet\|--ingest\|--import <file>]` | Phase 3: run test cases (in chat or offline sheet), import JUnit/TRX results, record runs |
| `/qa-defect [id] list\|confirm\|retest\|refresh…` | Review drafted defects; create confirmed ones in ADO; retest fixes |
| `/qa-explore [id] charters\|run <CH>\|retest <DEF>\|smoke` | Exploratory, focused and re-verification sessions in the browser via Playwright MCP (autonomous, guided or pair) |

## Quick start

1. Clone this repo, then in **the project you want to test** start Claude Code with
   `claude --plugin-dir <path-to>/99x-qa-trust-architect`.
2. Copy `config/.env.example` to the project's `.env` (gitignored) and fill in `ADO_PAT`;
   set `ADO_ORG` in your shell for the Azure DevOps MCP server.
3. `/qa-init` → answer the setup and domain questions → `/qa-gate G0`.
4. Pick a story: `/qa-start 1234` → answer `questions.md` → `/qa-gate G1` → …

## Documentation

| Page | Covers |
|---|---|
| [Supported projects](docs/01-supported-projects.md) | Project types, platforms, tech stacks, what's in each release |
| [Installation & setup](docs/02-installation-and-setup.md) | Prerequisites, install, `/qa-init`, configuration reference, troubleshooting |
| [Credentials & test accounts](docs/03-credentials-and-test-accounts.md) | Azure DevOps PAT, `.env`, MCP/CLI auth, test usernames & passwords |
| [Existing projects](docs/04-existing-projects.md) | With docs, without docs, with AI-DLC; keeping the domain current |
| [Agents & commands](docs/05-agents-and-commands.md) | Every `/qa-*` command and specialist agent, stage-to-agent map, tiers |
| [Daily workflow](docs/06-daily-workflow.md) | One story from `/qa-start` to approved test cases in ADO |

## Repository layout

| Folder | Contents |
|---|---|
| `core/` | Lifecycle engine: workflow, routing, gate/question/DCP protocols, context loader, workflow-integration contract |
| `rules/` | One rule file per stage (what the AI does, inputs, outputs, checks) |
| `gates/` | Gate checklists |
| `templates/` | Artifact skeletons (incl. `templates/domain/`) |
| `schemas/` | Canonical, platform-neutral JSON schemas |
| `adapters/` | Work item platform adapters (`azure-devops` MVP, `jira-xray` v2, `github` v3) |
| `integrations/` | Other SDLC workflows (`aidlc`) |
| `agents/` | Specialist sub-agents (domain, requirement, risk-gap, test design, automation, execution, exploratory, sync) |
| `scripts/` | Framework helpers (`import_results.py` — JUnit/TRX normaliser) |
| `skills/` | User-facing `/qa-*` commands — they orchestrate in the main session, because questions and gates need the human |
| `config/` | Example project config |
| `hooks/` | Optional guard hooks |
| `examples/` | Greenfield / brownfield walkthroughs |
| `docs/` | User documentation (start at `docs/README.md`) |

## Roadmap

| Release | Scope |
|---|---|
| **MVP (0.1)** | Phase 0 (incl. domain discovery w/o live crawl), Phase 1, stage 2.1 (+2.2–2.4 drafts), G0–G3 advisory, DCPs, context loader, repo storage, Azure DevOps adapter, AI-DLC companion mode |
| v2 | **Slice A ✅** Phase 3 execution core (manual runs, defects, regression, summary) + G4 · **B ✅** Playwright MCP exploratory testing + live crawl · **C ✅** hardened 2.2–2.4 · F guard hooks · D Jira + Xray · E AI-DLC gate alignment & write-back |
| v3 | GitHub adapter, two-way sync + drift detection, AI-DLC embedded mode |
| v4 | Automation script generation, Phase 4 observability & escape analysis, metrics dashboards |
