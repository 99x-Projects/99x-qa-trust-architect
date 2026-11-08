# Automation Gap — {{workItemKey}} {{title}}

> Stage 2.3 · {{isoDate}} · Domain context v{{domainVersion}} · Tier {{tier}}
> Value = (F + R + S + D) − E · ≥ 12 automate now · 8–11 backlog · < 8 keep manual

## 1. Summary
| Total TCs | Already automated | Extend existing | Automate now | Backlog | Manual-only | Exploratory | Automation ratio | Policy target |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | {{x}}% | {{70}}% |

## 2. Classification
| TC | Level | Status | F | R | S | D | E | Value | Recommendation | Target (framework · path · stage) | Blockers | Reason / notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TC-001 | api | candidate | 5 | 5 | 4 | 5 | 2 | 17 | automate now | xunit · tests/Api/LeaveTests.cs · PR | – | name `TC-001_rejects_21_days` |
| TC-007 | manual | manual-only | | | | | | | keep manual | | | visual judgement of calendar layout |

## 3. Existing automation reused
| TC | Kind | Existing test | Evidence (assertion) |
|---|---|---|---|
| TC-002 | already-automated | tests/LeaveTests.cs::MaxDays | `Assert.Equal(400, …)` for 21 days |
| TC-003 | extends | e2e/leave.spec.ts::submit request | same flow, add 0-day case |

## 4. Suggested level splits (for 2.1)
| TC | Today | Suggest |
|---|---|---|

## 5. Framework gaps
| GAP | Missing capability | Impact (TCs) | Proposal |
|---|---|---|---|

## 6. Dev asks (testability)
| # | Ask | Unblocks | Create on platform? |
|---|---|---|---|
| DA-01 | `data-testid` on leave form fields | TC-004, TC-005 | ask at G3 |

## 7. Automation backlog
| Item | TCs | Level | Framework · path | Pipeline | Estimate | Blockers | Done when | Create on platform? |
|---|---|---|---|---|---|---|---|---|
| AB-01 | TC-001, TC-002 | api | xunit · tests/Api/LeaveTests.cs | PR | S | – | tests named with TC ids, run in PR pipeline, TRX published | ask at G3 |

## Self-check
- [ ] Every TC has level + status
- [ ] Every reuse claim has evidence
- [ ] Candidates scored; manual-only reasons given
- [ ] Every backlog item has target, TC-id naming, pipeline, done-when
- [ ] Framework gaps and dev asks listed
