# Acceptance Criteria — {{workItemKey}}

> Stage 1.3 · {{isoDate}} · Domain context v{{domainVersion}}
> Formats: Gherkin (behaviour/flows) and rule tables (combinations/calculations).

## Coverage
| REQ | AC | Negative AC present | Boundaries |
|---|---|---|---|
| REQ-01 | AC-01, AC-02, AC-03 | ✔ (AC-03) | ✔ |

## Criteria

### AC-01 — {{title}}
`format: gherkin` · `traces: REQ-01, BR-012, ROLE-employee` · `basis: confirmed`
```gherkin
Given {{precondition}}
When {{action}}
Then {{observable outcome}}
```

### AC-02 — {{title}}
`format: rule-table` · `traces: REQ-02, BR-020` · `basis: provisional (DCP-0007)`

{{one-line rule description}}

| {{condition 1}} | {{condition 2}} | {{expected outcome}} |
|---|---|---|
| | | |

## Provisional criteria
| AC | Depends on | Question / DCP |
|---|---|---|

## Self-check
- [ ] Every REQ has ≥ 1 AC; negative AC where input exists
- [ ] Exact boundary values
- [ ] Atomic, observable, unambiguous, implementation-independent, glossary terms
- [ ] Provisional AC tagged
