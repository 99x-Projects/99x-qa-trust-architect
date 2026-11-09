# Domain Change Protocol (DCP)

The domain context is shared truth for every agent. Agents **never edit domain files
directly**; they raise a **Domain Change Proposal (DCP)**. The initial build is approved
at **G0**; everything after that flows through DCPs.

## 1. Proposal lifecycle

```
raised ──► (auto-accept level) ──► accepted ──► applied
   │
   └──► pending ──► reviewed (gate pack or /qa-domain review)
                       ├─► accepted ──► applied
                       ├─► rejected ──► archived
                       ├─► deferred  (stays pending)
                       └─► superseded (by a newer DCP on the same fact)
```

Files: `DOMAIN_DIR/_proposals/DCP-0007-<slug>.md` (from `templates/domain/proposal.md`).
Accepted/rejected/superseded proposals move to `DOMAIN_DIR/_proposals/_archive/`.

## 2. Fact statuses

| Status | Meaning | Usable as test oracle? |
|---|---|---|
| `documented` | Stated in a requirement/document | Yes, once `verified: true` |
| `observed` | Seen in code/tests/running app — what the system **does** | No |
| `inferred` | Derived by AI from indirect clues | No |
| `confirmed` | A human confirmed it (G0, DCP, or answered question) | Yes |
| `disputed` | Sources conflict → `discrepancies.md` | No (becomes a question) |

## 3. Review levels (from `domain.proposals` config)

| Level | Default fact types | Handling |
|---|---|---|
| `auto` | app-map pages/screenshots, feature-map code links, typo fixes | Applied immediately, logged in `audit.md` |
| `review` | glossary, journeys, entities, known quirks, integrations, personas | Any tester (or configured owner) accepts |
| `critical` | business rules, role permissions, state machines | Reviewer must see the **impact list**; configured owner if set |

Removing any fact is at least `review`; removing a business rule is `critical`.

## 4. Sources that raise DCPs

| Source | Typical DCPs | Reviewed at |
|---|---|---|
| 0.2 domain discovery after G0 / `/qa-domain refresh` | any | review queue |
| 1.2–1.3 requirement analysis / AC | new rules, terms, journeys | G1 pack |
| Answered question | confirm/change a rule | G1/G3 pack |
| 2.1 test design | missing rule/state | G3 pack |
| 3.2b exploratory session (v2) | new pages (auto), discrepancies | G4 pack |
| 4.3 escape analysis (v4) | missing/incorrect rules | G5 pack |
| Staleness check (source hash changed) | re-verify fact | review queue |
| AI-DLC artifact changed (integration) | update from AI-DLC source | review queue / aligned gate |

## 5. Provisional facts

While pending, a proposed fact is **provisional**:
- Usable by agents if `domain.provisionalFacts.usableByAgents: true`.
- Anything derived is tagged `basis: provisional (DCP-xxxx)`.
- Cannot by itself fail a test or create a defect if `canFailTests: false` → raise a question.

## 6. Conflicts

Before accepting, check `_proposals/` for other pending DCPs on the same fact ID.
Two conflicting DCPs cannot both be accepted; present them side by side.

## 7. On acceptance

0. Open the **apply window** so the domain write guard allows the edit:
   `python <FRAMEWORK_ROOT>/hooks/qa_guard.py dcp-window open DCP-0007,DCP-0008` (30 minutes by
   default); close it when done: `... dcp-window close`. Auto-level DCPs use the same window.
1. Apply the change to the domain file. Update the fact's `status`, `sources`,
   `lastVerified`, `confidence`.
2. **Impact propagation**: find artifacts referencing the fact ID (test cases `traces.rules`,
   AC `rules`, charters, journeys) across all `ITEM_DIR`s → add a `needs-review` flag
   to each and list them in the owning item's `qa-state.md` → `followUps`.
3. Bump the domain context version in `domain-overview.md` front-matter
   (`domainVersion`: minor bump per accepted batch; major bump on G0 re-baseline).
4. Append to `audit.md` (project-level `_project/audit.md`):
   `DCP-0007 accepted by <name> (critical) — BR-012 max days 20→25; 3 artifacts flagged`.
5. If `domain.notifyPlatform` ≠ none → adapter `addComment` on linked work items
   (or create a "Domain update" work item).

## 8. Staleness

Each fact stores `sources[].ref` and, where it is a file, `sources[].hash`.
`/qa-status` and `/qa-domain refresh` recompute hashes; a changed source marks the fact
`stale` and raises a re-verify DCP. Proposals pending longer than
`domain.proposals.staleAfterDays` are flagged in `/qa-status`.
