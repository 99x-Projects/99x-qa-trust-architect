# Risk & Impact Assessment — {{workItemKey}}

> Stage 1.4 · {{isoDate}} · Domain context v{{domainVersion}}

**Summary:** {{h}} high · {{m}} medium · {{l}} low

## Risk register
| ID | Risk | Category | AC / Feature | L (1–5) | I (1–5) | Score | Rating | Drivers | Mitigation |
|---|---|---|---|---|---|---|---|---|---|
| R-01 | {{risk}} | functional | AC-03 / F-x | 4 | 4 | 16 | high | hotspot, boundary | BVA TCs + monitoring |

## Impact / blast radius
| Area | Why impacted | Hop | Existing coverage |
|---|---|---|---|
| {{component/feature}} | {{shared service / data consumer}} | 1 | {{tests or none}} |

## Regression candidates
| Test / suite | Covers | Reason selected |
|---|---|---|

## Self-check
- [ ] Every AC in a risk entry or marked low-risk
- [ ] Every high risk has mitigation
- [ ] Regression candidates listed (brownfield)
