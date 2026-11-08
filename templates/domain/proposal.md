---
id: DCP-{{0007}}
title: "{{BR-012 max leave days 20 → 25}}"
status: pending               # pending | accepted | rejected | deferred | superseded
level: critical               # auto | review | critical
change: modify                # add | modify | remove
targetFile: business-rules.yaml
targetFactId: BR-012
raisedBy: "{{agent or person}}"
raisedAt: "{{isoDateTime}}"
origin: "{{ADO-1234 stage 1.2 | session CH-03 | staleness check | aidlc:<path>}}"
confidence: high
supersedes: null
conflictsWith: []             # other pending DCP ids on the same fact
decidedBy: null
decidedAt: null
decisionReason: null
---

# DCP-{{0007}} — {{title}}

## Change
```diff
- statement: "An employee cannot request more than 20 leave days in a single request."
+ statement: "An employee cannot request more than 25 leave days in a single request."
```

## Evidence
| Type | Reference | Quote |
|---|---|---|
| tracker-story | {{ADO-1234 AC-03}} | "{{quote}}" |

## Impact (artifacts referencing this fact)
| Artifact | Work item | Will be flagged |
|---|---|---|
| TC-004 | ADO-1100 | needs-review |

## Decision
{{filled on review}}
