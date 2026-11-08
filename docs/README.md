# QA Trust Architect — Documentation

Start here, in this order:

| # | Page | Read it when you want to know… |
|---|---|---|
| 1 | [Supported projects](01-supported-projects.md) | Will this work for my project, platform and tech stack? What is in the MVP? |
| 2 | [Installation & setup](02-installation-and-setup.md) | How do I install the plugin and set it up in a project? |
| 3 | [Credentials & test accounts](03-credentials-and-test-accounts.md) | How do I configure the Azure DevOps PAT and test usernames/passwords safely? |
| 4 | [Existing projects](04-existing-projects.md) | How do I adopt it on a project that already has code, tests — with or without written requirements, or with AI-DLC? |
| 5 | [Agents & commands](05-agents-and-commands.md) | What does each `/qa-*` command and each specialist agent do? |
| 6 | [Daily workflow](06-daily-workflow.md) | How does a tester take a story from intake to approved test cases? |

Reference material (for people extending the framework) lives next to the code:
`core/` (lifecycle engine), `rules/` (one file per stage), `gates/`, `templates/`,
`schemas/`, `adapters/`, `integrations/`.

## Glossary of framework terms

| Term | Meaning |
|---|---|
| **Gate (G0–G5)** | A review point where a tester reads the AI's artifacts, analyses them and records a decision: *approved*, *approved-with-risks*, *rejected* or *overridden*. Gates are **advisory** by default. |
| **Tier** | How much process a work item gets: *light* (bugs/hotfixes), *standard*, *comprehensive* (epics, payments, PII, security). |
| **Domain context** | The shared, reviewed knowledge about the application under test (features, roles, business rules, journeys…) that every agent works from. |
| **DCP** | *Domain Change Proposal* — the only way the domain context changes after G0. Reviewed with `/qa-domain review`. |
| **Provisional fact** | A domain fact in a pending DCP. Agents may use it, but it can never be the reason a test fails. |
| **`questions.md`** | Where the AI asks what it cannot work out. You answer in the `[Answer]:` slots. |
| **`qa-state.md` / `audit.md`** | Per work item: where it is in the lifecycle, and the full trail of decisions. |
