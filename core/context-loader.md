# Context Loader

Agents must not ingest the whole domain context. The context loader gives each agent
the **relevant slices** only.

## 1. Resolve the feature scope

For a work item:
1. Read `DOMAIN_DIR/feature-map.yaml`.
2. Match features by, in order of strength:
   - explicit link (work item ↔ epic/feature already mapped, or AI-DLC unit ↔ feature)
   - code paths touched (PR diff / linked commits) ↔ `feature.codePaths`
   - routes / APIs mentioned ↔ `feature.routes`, `feature.apis`
   - glossary terms / keywords in title, description, AC ↔ `feature.keywords`
3. Result: `scope.features = [F-..]` with match reasons. If no match → ask (Q) and
   consider a new feature DCP. If a matched feature has `depth: skeleton` and
   `domain.discovery.depth.lazy: true` → run focused discovery for it first
   (`rules/phase-0-setup/0.2-domain-discovery/0.2-overview.md` §5 "Lazy deepening").
4. Expand one hop: features listed in `feature.dependsOn` / `integrations` → add as
   `scope.adjacent` (used for risk/regression only).

## 2. Slices

| Slice | Source | Filter |
|---|---|---|
| `overview` | `domain-overview.md` | whole (it is ≤ 1 page) |
| `glossary` | `glossary.md` | always included (whole) |
| `features` | `feature-map.yaml` | scope + adjacent |
| `rules` | `business-rules.yaml` | `rule.features ∩ scope` |
| `journeys` | `journeys/*.md` | journeys touching scope |
| `entities` | `entities-states.yaml` | entities used by scope features |
| `roles` | `personas-roles.yaml` | roles with permissions on scope |
| `appmap` | `app-map/app-map.yaml` | pages of scope features |
| `integrations` | `integrations.yaml` | integrations of scope + adjacent |
| `environments` | `environments.yaml` | whole (no secrets ever stored) |
| `hotspots` | `risk-hotspots.md` | entries for scope + adjacent |
| `quirks` | `known-quirks.md` | entries for scope |
| `nfr` | `_project/quality-standards.md` §NFR | whole |
| `existingTests` | `_project/feature-test-map.yaml` | scope + adjacent |
| `discrepancies` | `discrepancies.md` | open, for scope |
| `pendingDcps` | `_proposals/DCP-*.md` | pending, touching scope |

## 3. Agent → slices

| Agent / stage | Slices |
|---|---|
| requirement-analyst (1.1–1.3) | overview, glossary, features, rules, entities, roles, discrepancies, pendingDcps |
| risk-gap-analyst (1.4–1.6) | features, rules, hotspots, integrations, existingTests, nfr, quirks |
| test-designer (2.1–2.2) | glossary, rules, entities, roles, journeys, nfr, environments, quirks |
| automation-analyst (2.3) | features, existingTests, appmap |
| observability (2.4) | integrations, nfr, features |
| execution-analyst (3.2a–3.5) | rules, quirks, roles, features, environments, existingTests, hotspots, integrations, discrepancies, pendingDcps |
| exploratory-tester (v2) | appmap, journeys, roles, rules, quirks, environments |
| domain-analyst | everything (it maintains the context) |

## 4. Fact status handling

Every fact has a `status` (see `domain-change-protocol.md` §2):
- `confirmed` / verified `documented` → may be used as a test oracle.
- `observed`, `inferred`, `disputed`, or **pending DCP** (provisional) → may inform
  analysis, but anything derived must be tagged `basis: provisional (<id>)`, and it
  **cannot be the sole basis of a failed test or a defect** when
  `domain.provisionalFacts.canFailTests: false` — raise a question instead.

## 5. Output

The loader writes nothing. It returns to the calling agent:
```
CONTEXT (domain v1.14) — scope: F-leave-request, F-leave-approval (+adjacent F-notifications)
[glossary] ...
[rules] BR-012 (confirmed) ..., BR-015 (observed, provisional) ...
...
```
Always state the domain context version (from `domain-overview.md` front-matter) so it
can be recorded in gate records.
