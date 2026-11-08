---
name: qa-explore
description: Exploratory, focused, smoke and bug re-verification testing of a web app through the Playwright MCP server, driven by QA Trust Architect charters and domain context — plan charters for a work item, run a session in autonomous, guided or pair mode, retest a defect in the browser, and turn findings into defect drafts, questions, DCPs and test-case suggestions. Use when a tester wants to explore, poke at, smoke test or re-verify a feature in the browser.
argument-hint: "[work-item-id] charters | run <CH-id> [--mode autonomous|guided|pair] [--env <env>] [--role <ROLE-id>] [--minutes N] | retest <DEF-id> | smoke | report <SES-id>"
---

# /qa-explore

`FRAMEWORK_ROOT` = two levels up from this skill's base directory. Arguments: `$ARGUMENTS`

1. Read `core/core-workflow.md` §0–1 and `rules/phase-3-execution/3.2b-exploratory-playwright.md`.
   Resolve the work item (default: most recent, confirm). Confirm the tester's name once.
2. **Preflight** (every sub-command that uses the browser):
   - Playwright MCP tools available (`browser_snapshot`, `browser_navigate`, …)? If not: explain how to
     enable the `playwright` server (`docs/02-installation-and-setup.md`) and stop.
   - Environment (`--env`, else `execution.defaultEnvironment`) passes 3.2b §4.1; resolve its base URL
     from `environments.yaml`. Production → refuse.
   - Role (`--role`, else the charter's role) has an account reference in `environments.yaml`.
   - Build/version: ask (suggest the latest known); recorded on the session.

## charters
Delegate `plan-charters` to `qa-trust-architect:exploratory-tester`. Show the list (id, title, risk,
role, time box, suggested mode). The tester may edit/remove; save. Mark stage 3.2b `in-progress`.

## run <CH-id>
1. Allocate `SES-xxx`, create `3-execution/sessions/SES-xxx/` with `charter.md`; audit `SESSION-STARTED`.
2. **Login** per `exploratory.auth.strategy` (3.2b §4.3). `manual`: navigate to the base URL and say
   "Please log in as <role> using the account in `<ref env var>` in the browser window, then tell me
   when done." Verify the signed-in state in the snapshot. Never ask for or type credentials.
3. **Mode** (`--mode`, else the charter's suggestion, else ask):
   - `autonomous` → delegate `session` to `exploratory-tester` with FRAMEWORK_ROOT, ITEM_DIR, DOMAIN_DIR,
     the charter, SES id, env base URL + allowed origins, guards, build. Wait for its report.
   - `guided` → run the loop (3.2b §5) **here**: after each few actions summarise what you see and
     propose the next 2–3 probes; follow the tester's steering. Ask before any blocked action.
   - `pair` → the tester drives the headed browser. On "note"/"check" take a snapshot (+ screenshot if
     useful), compare against oracles, log it. Offer probes when asked. On "done" end the session.
4. **Wrap-up:** write/complete `session-report.md`; copy evidence; audit `SESSION-ENDED`.
   - Defect candidates → delegate `draft-defects` to `qa-trust-architect:execution-analyst` (with
     `traces.session`), then offer `/qa-defect confirm`.
   - Questions/discrepancies/DCPs written → list them; app-map DCPs at `auto` level are applied per
     `core/domain-change-protocol.md`.
   - TC / automation suggestions → ask whether to add them (2.1 / 2.3 artifacts get `needs-review`).
   - Update the charter status; show a ≤ 10-line summary and remaining high-risk charters.

## retest <DEF-id>
Login as the defect's role; delegate `retest` (autonomous) or do it guided if the tester prefers. Record a
run (`mode: exploratory`, `set: retest`, `retestOf`) and update the defect per 3.3 §6 — platform changes
only after the tester confirms.

## smoke
Session type `smoke` over the key journeys of the item's scope features (no charter file needed;
generate an ad-hoc charter in the session folder). Autonomous by default.

## report <SES-id>
Show the session report summary and open follow-ups.

When all mandatory charters are done (or skipped with reason), mark 3.2b `done`.
