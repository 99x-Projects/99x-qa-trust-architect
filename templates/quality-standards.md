# Quality Standards — {{project}}

> Stage 0.4 · Approved at G0. Values marked `default` were not changed by the team.

## Definition of Ready for test design (G1)
- Every requirement has acceptance criteria incl. negative paths `default`
- No blocking open questions `default`
- Feature scope identified in the domain context `default`

## Definition of Done for testing (G4)
- Exit criteria met; test summary report published `default`
- All overrides acknowledged `default`

## Severity scale
| Severity | Meaning | Platform value |
|---|---|---|
| Sev1 Critical | Outage, data loss/corruption, security breach, no workaround | {{1 - Critical}} |
| Sev2 High | Major function broken, poor workaround | {{2 - High}} |
| Sev3 Medium | Function impaired, reasonable workaround | {{3 - Medium}} |
| Sev4 Low | Cosmetic/minor | {{4 - Low}} |

## Default entry criteria
- Build deployed to test environment; smoke passing `default`
- Required data sets available `default`

## Default exit criteria
- 100% P1 TCs executed and passed `default`
- ≥ 95% planned TCs executed `default`
- 0 open Sev1/Sev2; Sev3 accepted by PO `default`
- Regression pass rate ≥ 98%, failures triaged `default`

## NFR targets
| Area | Target |
|---|---|
| Performance | {{p95 API latency ≤ 500 ms at N rps}} |
| Accessibility | {{WCAG 2.2 AA}} |
| Security | {{OWASP Top 10 / ASVS L1}} |
| Browsers/devices | {{latest Chrome, Edge, Safari; mobile ≥ 375px}} |
| Localisation | {{languages or n/a}} |

## Test levels policy
- Business rules → unit/API; UI tests for critical journeys only `default`
- Target: ≥ {{70}}% of regression TCs automated `default`

## Evidence standards
- Manual pass: tester, date, build, environment. Fail: screenshot/video + steps + logs `default`
