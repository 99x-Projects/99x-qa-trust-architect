# Exploratory Charters — {{workItemKey}} {{title}}

> Stage 3.2b · {{isoDate}} · Domain context v{{domainVersion}} · Tier {{tier}}
> One charter per high risk / gap cluster / journey. Mandatory for high risks (standard, comprehensive).

## CH-01 — {{short title}}

**Explore** {{target: feature / page / flow}}
**with** {{resources: heuristics, data sets}}
**to discover** {{information sought: violations of BR-xxx, J-xx step n, error handling…}}

| Field | Value |
|---|---|
| Type | focused / exploratory / re-verification / smoke |
| Risk / gap | R-02 (high), GAP-03 |
| Role | ROLE-employee |
| Environment | test |
| Pages | PAGE-leave-new, PAGE-leave-list |
| Oracles (can fail) | AC-03, AC-04, BR-012 (confirmed) |
| Provisional (observe only) | BR-020 (observed), DCP-0011 |
| Quirks to ignore | QK-01 |
| Heuristics | boundaries, invalid input, double submit, back/refresh, permissions |
| Data | DS-01, DS-02 |
| Time box | 30 min · max actions {{exploratory.guards.maxActions}} |
| Suggested mode | autonomous / guided / pair |
| Status | planned / done (SES-xxx) / skipped (reason) |
