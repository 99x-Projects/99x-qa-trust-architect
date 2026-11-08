# 0.2 — Live Crawl (Playwright MCP)

**Goal:** see the application as each role sees it — pages, navigation, key elements, labels,
visible actions — and record it in `app-map/app-map.yaml`, with evidence for other domain files.
**Runs:** `/qa-domain crawl [--env <env>] [--role <ROLE-id>|all]`, or during `/qa-init` when
`domain.discovery.sources.liveApp: true`. **Agent:** `exploratory-tester` (task `crawl`).
**Safety:** exactly as `rules/phase-3-execution/3.2b-exploratory-playwright.md` §4 (allowed
environments and origins, no production, manual or storage-state login, no credentials seen).

The crawl is **read-mostly**: it navigates and opens menus, tabs and dialogs but never submits a
form, saves, deletes, approves or sends anything. Opening a "New …" form to read its fields is
allowed; leaving it without saving is required.

## Steps (per role)
1. Log in as the role (3.2b §4.3). Record the landing page.
2. **Breadth-first over navigation:** main menu, sub-menus, tabs, list → first detail item,
   "New/Create" forms (read fields, then cancel/back). Limits: `domain.discovery.crawl.maxPages`
   (default 60) and `maxDepth` (default 4) per role; same-origin only; skip logout links and
   anything matching `blockActions`.
3. Per page record: path pattern (replace ids with `{id}`), title/heading, breadcrumb/navigation
   path, key elements (accessible role + name: inputs with labels, buttons, links, tables + column
   headers), visible actions, validation hints/help texts, and one screenshot
   (`app-map/screenshots/<PAGE-id>-<ROLE>.png`).
4. Note console errors and failed requests seen while crawling (candidate quality issues, not defects).
5. Map pages to features (`feature-map.yaml` routes/keywords); unmapped pages → feature question.

## Output → domain context (all as DCPs; G0 for the initial build)
| Finding | Target | DCP level |
|---|---|---|
| Pages, navigation, key elements, screenshots | `app-map/app-map.yaml` (`source: crawl`) | auto |
| Role can see/do X (menu entries, buttons per role) | `personas-roles.yaml` permissions — `status: observed` | critical |
| Field labels, help texts, validation hints ("max 20 days") | evidence for `business-rules.yaml` (corroboration source `type: ui`) | review |
| New terms in labels/menus | `glossary.md` | review |
| Page with no mapped feature | `feature-map.yaml` new feature or question | review |
| Console errors / 5xx while crawling | `risk-hotspots.md` note | review |

UI evidence counts as **one independent source** for corroboration (`corroboration.md`); a
permission seen in the UI is `observed`, never `confirmed` — the UI hiding a button is not proof the
API forbids the action.

## Self-check
- [ ] No form submitted; no blocked action clicked; same-origin only
- [ ] Every page has a path pattern, role and ≥ 1 key element
- [ ] Permissions recorded as observed, with role and page evidence
