---
workItemKey: "{{workItemKey}}"          # e.g. ADO-1234
title: "{{title}}"
platform: "{{platform}}"
source: "{{sourceUrl}}"
aidlcUnit: null                        # e.g. aidlc-docs/construction/leave-unit (companion mode)
tier: "{{tier}}"                       # light | standard | comprehensive
tierReason: "{{tierReason}}"
tierOverriddenBy: null
domainVersionAtStart: "{{domainVersion}}"
created: "{{isoDate}}"
updated: "{{isoDate}}"
---

# QA State — {{workItemKey}} {{title}}

## Stages
| Stage | Status | Artifact | Updated |
|---|---|---|---|
| 1.1 Requirement intake | pending | 1-inception/requirement.md | |
| 1.2 Requirement analysis | pending | 1-inception/requirement-analysis.md | |
| 1.3 Acceptance criteria | pending | 1-inception/acceptance-criteria.md | |
| 1.4 Risk & impact | pending | 1-inception/risk-assessment.md | |
| 1.5 Gap analysis | pending | 1-inception/gap-analysis.md | |
| 1.6 Test plan | pending | 1-inception/test-plan.md | |
| 2.1 Test cases | pending | 2-design/test-cases/ | |
| 2.2 Test data & env | pending | 2-design/test-data.md | |
| 2.3 Automation gap | pending | 2-design/automation-gap.md | |
| 2.4 Observability | pending | 2-design/observability-plan.md | |

<!-- Status values: pending | in-progress | blocked-on-questions | done | skipped (tier) | not-implemented -->
<!-- Remove rows for stages the tier skips, or mark them `skipped (tier)`. -->

## Gates
| Gate | Status | Decided by | Date | Domain version | Record |
|---|---|---|---|---|---|
| G1 | pending | | | | gates/G1.md |
| G2 | pending | | | | gates/G2.md |
| G3 | pending | | | | gates/G3.md |

<!-- Gate status: pending | approved | approved-with-risks | rejected | overridden | stale -->

## Open items
- Questions: 0 open (0 blocking)
- Pending DCPs raised by this item: none
- Follow-ups (needs-review from accepted DCPs): none

## Sync
| Artifact | Platform ID | Last sync | Hash |
|---|---|---|---|
