# Domain Discovery — Evidence-led (Scenario B: no written requirements)

**Principle:** reconstruct from evidence, then confirm with humans.
**Golden rule:** code tells you what the system **does**, not what it **should** do.
Facts start as `observed`/`inferred` and become oracles only once `confirmed`.

## 1. Sources (most → least reliable for *intent*)

| Source | Reveals | Where to look |
|---|---|---|
| Existing tests | Behaviour developers intended and asserted | test projects; assertion messages; test names; `.feature` files |
| Validation & error messages | Business rules in plain language | resource files (`.resx`, i18n JSON), exception messages, `ValidationException`, FluentValidation/Joi/Zod/Pydantic schemas |
| Code logic | Rules, states, permissions | validators, guards, `if` conditions with domain constants, enums, state transition methods, authorization attributes/policies |
| Data model | Entities, relationships, limits | migrations, ORM models, DB constraints (NOT NULL, CHECK, UNIQUE, FK), lookup/seed tables |
| Tracker history | Past intent; **bug reports reveal expected behaviour** | closed stories' AC, bugs' "expected result" field, epic descriptions |
| API specs / routes | Feature surface, operations, inputs | OpenAPI, controllers, GraphQL schema, route config |
| Config & feature flags | Variants, limits, env differences | appsettings, `.env.example`, flag definitions |
| Live app | Screens, flows, roles as users experience them | Playwright crawl per role (`live-crawl.md`) |
| Logs / analytics (optional) | Which journeys matter most | provided exports only |

## 2. Rule-mining patterns (examples)

- **Constants near comparisons:** `if (days > MaxLeaveDays)` → limit rule; resolve the constant.
- **Enum + switch/transition methods:** `Status.Draft → Submitted → Approved|Rejected` → state machine.
- **Authorization:** `[Authorize(Policy="Manager")]`, `@PreAuthorize`, route guards → permission facts.
- **Validation schemas:** `RuleFor(x => x.Days).LessThanOrEqualTo(20)` → rule with exact boundary.
- **DB constraints:** `CHECK (end_date >= start_date)` → rule.
- **Error message catalogue:** each user-facing message usually encodes one rule; link message → code path.
- **Test names:** `Should_Reject_Overlapping_Leave` → rule candidate (assertion confirms specifics).
- **Bug history:** "Expected: manager cannot approve own leave" → rule candidate, strong intent signal.

## 3. Procedure

1. **Skeleton** (from overview §3) if not done.
2. **Mine** rules, permissions, states, journeys for the feature (patterns above).
3. **Corroborate**: merge candidates describing the same behaviour; score confidence
   (`corroboration.md`). Conflicts → `disputed` + DISC entry.
4. **Journeys**: reconstruct from route/navigation order, controller call chains,
   E2E tests, and tracker epics. Mark `inferred` unless an E2E test asserts the flow.
5. **Targeted interview** (`targeted-interview.md`): one question per disputed or
   high-impact low-confidence fact; multiple-choice with suggested default.
6. **Prioritise**: deep-dive `top-risk`/`top-usage` features; others stay `skeleton`
   (lazy deepening later).

## Pitfalls
- **Bugs that became features.** A long-standing behaviour is not necessarily correct.
  Never promote `observed` → `confirmed` without a human.
- **Tacit knowledge** ("we never run payroll on the 1st") exists only in people's heads —
  always include a closing open-but-bounded question per deep feature:
  "Any rule about <feature> that the system does not enforce but users must follow?"
- **Dead code.** Check the code path is reachable (referenced, routed, flag on) before
  mining a rule from it.
