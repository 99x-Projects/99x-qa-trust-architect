# Routing Rules — Adaptive Depth

Routing decides **which stages run** for a work item, so small changes don't drown in
process. It runs at the end of stage 1.1 and writes the decision to `qa-state.md`.

## 1. Inputs

- Canonical work item: `type`, `labels`, `priority`, size/estimate, linked items
- `routing.rules` from `qa-trust.config.yaml` (first match wins), else `routing.defaultTier`
- Signals from the domain context: does the work item touch a feature in
  `risk-hotspots.md` or a `critical` business rule? → escalate one tier
- AI-DLC unit metadata if integration active (e.g. unit marked complex/critical)

## 2. Tier → stages

| Stage | Light | Standard | Comprehensive |
|---|:-:|:-:|:-:|
| 1.1 Intake | ✔ | ✔ | ✔ |
| 1.2 Requirement analysis | lite (ambiguity scan only) | ✔ | ✔ |
| 1.3 Acceptance criteria | lite (validate existing AC) | ✔ | ✔ |
| **G1** | ✔ | ✔ | ✔ |
| 1.4 Risk & impact | – | ✔ | ✔ (+blast radius) |
| 1.5 Gap analysis | – | ✔ | ✔ |
| 1.6 Test plan | – | lite (one-page) | ✔ (full) |
| **G2** | – | ✔ | ✔ (PO recommended) |
| 2.1 Test cases | ✔ | ✔ | ✔ |
| 2.2 Data & env | – | if needed | ✔ |
| 2.3 Automation gap | – | ✔ | ✔ |
| 2.4 Observability | – | if user-facing or integration | ✔ |
| **G3** | ✔ | ✔ | ✔ |
| 3.1 Automation implementation (v4) | – | non-blocking stub | non-blocking stub |
| 3.2a Manual execution | ✔ | ✔ | ✔ |
| 3.2b Exploratory (slice B) | – | high-risk charters | ✔ |
| 3.3 Defect management | ✔ | ✔ | ✔ |
| 3.4 Regression | impacted feature only | scope + adjacent | + two hops, hotspots |
| 3.5 Test summary report | lite (exit criteria + defects) | ✔ | ✔ |
| **G4** | ✔ | ✔ | ✔ (PO recommended) |
| 4.x Operations (v4) | – | 4.1 | all |

## 3. Escalation / de-escalation signals

Escalate one tier (max comprehensive) when any of:
- Touches a feature listed in `risk-hotspots.md`
- Touches a business rule with level `critical` or tags `money`, `pii`, `security`, `compliance`
- More than 3 integrations involved (`integrations.yaml`)
- Requirement analysis (1.2) finds ≥ 5 blocking questions

De-escalate is **never automatic** — only by explicit user override.

## 4. Recording

In `qa-state.md`:
```yaml
tier: standard
tierReason: "type=User Story; touches F-leave-approval (hotspot) → escalated? no (not in hotspots)"
tierOverriddenBy: null
stages: [...]            # list generated from the table above with status per stage
```
