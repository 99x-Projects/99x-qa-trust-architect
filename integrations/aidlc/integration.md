# AI-DLC Integration

Implements `core/workflow-integration.md` for AWS AI-DLC (AI-Driven Development Lifecycle).

| Mode | Release | Changes to AI-DLC |
|---|---|---|
| `companion` | **MVP** | None — read-only |
| gate alignment + question write-back | v2 | Optional writes, opt-in flags |
| `embedded` | v3 | Adds `embedded/qa-trust-extension.md` to AI-DLC rules |

## 1. Detection (stage 0.1)

AI-DLC is **detected** when `integrations.aidlc.enabled` is `auto`/`true` and either:
- `<docsPath>/aidlc-state.md` exists (default docsPath `aidlc-docs`), or
- AI-DLC rule files exist (e.g. a `aidlc-rules/` folder, `.amazonq/rules/aws-aidlc-*`,
  or a `CLAUDE.md` / agent rules file referencing "AI-DLC" core workflow).

Then:
1. Read `aidlc-state.md` → record current phase/stage and completed stages.
2. For each entry in `mapping.yaml`, glob the patterns; record which matched →
   `qa-profile.yaml → integrations.aidlc.layoutVersion` (`matched: [...]`, `missing: [...]`).
3. Suggest `companion` mode; ask the user to confirm (question in `_project/questions.md`).

## 2. Companion mode behaviour

- **Read-only.** Never create, edit or delete files under `docsPath`.
- **Domain discovery (0.2):** AI-DLC artifacts mapped as `domainSources` are treated as
  documentation (`source type: aidlc`) → features in their scope use `docs-led` discovery.
  Facts keep `sources[].ref: "aidlc:<path>"` and a hash.
- **Intake (1.1):** when `keyBy: unit`, a QA work item = an AI-DLC unit of work.
  `ITEM_DIR` = `storage.repo.layout` with `{intent}`/`{unit}` resolved from AI-DLC.
  When `keyBy: workItem`, units are linked to tracker items (`unitToWorkItem: from-tracker`
  → look for the tracker ID in unit/story docs) and AI-DLC artifacts are loaded as extra sources.
- **Requirements & stories** from AI-DLC are inputs to 1.1–1.3 (REQ statements, existing AC).
  QA does not copy them — it links them and analyses them for testability.
- **Readiness:** the orchestrator only starts a QA stage when its AI-DLC prerequisite is done
  per `aidlc-state.md` (see `gate-alignment.md`, "prerequisite" column). If not done, tell the
  user what AI-DLC stage is pending; the user may proceed anyway (advisory, logged).
- **Change sync (`domainSync: dcp`):** on `/qa-status`, `/qa-domain refresh`, and before each
  stage, recompute hashes of mapped AI-DLC artifacts; changed → raise DCPs with the AI-DLC
  artifact as origin.
- **Graceful degradation:** missing mapped artifact → warn once, fall back to normal stages.

## 3. Things never to do
- Never mark AI-DLC stages complete or edit `aidlc-state.md` / AI-DLC `audit.md`
  (unless `writeBack.auditEntries: true`, v2).
- Never answer AI-DLC's questions on the user's behalf.
