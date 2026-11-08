---
name: qa-init
description: Set up QA Trust Architect in the current project (Phase 0) — detect workspace, stack, tests, platform and AI-DLC; write qa-trust.config.yaml; build the domain context; inventory existing QA assets; draft quality standards; prepare G0. Use when the user wants to start using QA Trust Architect, initialise QA, or re-baseline.
argument-hint: "[--rebaseline]"
---

# /qa-init — Phase 0 setup

`FRAMEWORK_ROOT` = two levels up from this skill's base directory.

1. Read `FRAMEWORK_ROOT/core/core-workflow.md` (whole) and `core/workflow-integration.md`.
2. If `qa-trust.config.yaml` exists and no `--rebaseline`: show current status (as `/qa-status`)
   and ask whether to re-run Phase 0. Otherwise continue.
3. **0.1 Workspace detection** — follow `rules/phase-0-setup/0.1-workspace-detection.md` inline.
   Write `qa-trust.config.yaml` from `config/qa-trust.config.example.yaml` with detected values,
   and `PROJECT_DIR/qa-profile.yaml`. Ask the setup questions directly in the conversation
   (platform + org/project, storage path, testers, allowed environments, AI-DLC mode) — use
   short multiple-choice prompts. Record answers in `PROJECT_DIR/questions.md` as resolved.
4. **Test adapter connection** (`testConnection`, read one work item the user names). If it
   fails, offer repo-only mode (`storage.platform.enabled: false`) and continue.
5. **0.2 Domain discovery** — delegate to agent `qa-trust-architect:domain-analyst` with task
   `build` (pass FRAMEWORK_ROOT, project root, DOMAIN_DIR, config excerpt `domain`,
   `integrations.aidlc`, detected profile). Large repos: tell the user this may take a while.
6. **0.3 QA reverse engineering** (brownfield only) — follow
   `rules/phase-0-setup/0.3-qa-reverse-engineering.md` (inline or delegate to domain-analyst).
7. **0.4 Quality standards** — follow `rules/phase-0-setup/0.4-quality-standards.md`.
8. Create `PROJECT_DIR/audit.md` (template) and log each stage.
9. Summarise (≤ 12 lines): project type, platform, storage path, AI-DLC status, features
   (skeleton/deep), rules by status, discrepancies, **open interview questions** in
   `PROJECT_DIR/questions.md`, and next step:
   "Answer the questions, then run `/qa-domain review` (optional) and `/qa-gate G0`."
