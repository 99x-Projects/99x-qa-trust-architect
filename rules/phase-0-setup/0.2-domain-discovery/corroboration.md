# Corroboration & Confidence

## Independent source types
`doc`, `aidlc` (AI-DLC artifact), `test`, `error-message`, `code`, `schema`,
`tracker-story`, `tracker-bug`, `api-spec`, `config`, `live-app`, `human`.
Two sources of the **same type** count as one (e.g. two unit tests).
`code` and `error-message` from the same method count as one.

## Confidence

Let N = number of independent agreeing source types; `highConfidence` from config (default 2).

| Condition | Confidence |
|---|---|
| `human` confirmed | high (status → `confirmed`) |
| N ≥ highConfidence and no conflicting source | high |
| N = 1, source is test / doc(verified) / aidlc / tracker-bug | medium |
| N = 1, source is code / schema / config only | low |
| Any conflicting source | status `disputed`, confidence n/a |

## Status rules
- Doc/AI-DLC + evidence agree → `documented`, `verified: true`
- Only evidence → `observed`
- Derived indirectly (naming, flow order, analogy) → `inferred`
- Human answer / G0 / DCP acceptance → `confirmed`

## Oracle eligibility (used by context loader)
`confirmed` OR (`documented` AND `verified: true`). Everything else is provisional.
