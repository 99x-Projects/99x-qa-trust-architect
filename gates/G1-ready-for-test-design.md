# G1 — Ready for Test Design

**When:** after 1.1–1.3. **Record:** `ITEM_DIR/gates/G1.md`.
**Recommended session:** three-amigos (PO + dev + tester) review of AC.

## Checklist
| # | Item | Evidence |
|---|---|---|
| C1 | All REQs have ≥ 1 AC | AC coverage table |
| C2 | Every input-accepting REQ has negative AC | acceptance-criteria.md |
| C3 | All limits have exact boundary values | acceptance-criteria.md |
| C4 | No open **blocking** questions | questions.md |
| C5 | No open `blocking`/`major` requirement-analysis findings without decision | requirement-analysis.md |
| C6 | AC use glossary terms; new terms raised as DCPs | DCP list |
| C7 | Provisional AC are tagged and listed | acceptance-criteria.md |
| C8 | Feature scope resolved; skeleton features deepened (if lazy) | requirement.md |
| C9 | Tier decision recorded | qa-state.md |

## Pack must also show
DCPs raised by this item (review individually), requirement quality score, stale earlier gates (n/a).

## On approval → sync
- `updateAcceptanceCriteria` (if `acceptanceCriteria.pushToPlatform`)
- `setGateStatus G1`
- `addComment`: short summary + link to repo artifacts
