# Audit Log — {{scope}}

Append-only. One line per event, newest at the bottom. Never edit or delete past lines.

Format: `<ISO-8601 timestamp> | <EVENT> | <actor> | <details>`

Events: `STAGE-START`, `STAGE-DONE`, `QUESTION-RAISED`, `QUESTION-ANSWERED`,
`GATE` (approved|approved-with-risks|rejected|overridden|stale), `TIER-SET`, `TIER-OVERRIDE`,
`DCP-RAISED`, `DCP-ACCEPTED`, `DCP-REJECTED`, `DCP-AUTO-ACCEPTED`, `SYNC`, `SYNC-DRIFT`,
`INTEGRATION`, `CYCLE-OPENED`, `RUN-RECORDED`, `RUNS-IMPORTED`, `DEFECT-DRAFTED`, `DEFECT-CONFIRMED`,
`DEFECT-LOGGED`, `DEFECT-STATUS`, `RETEST`, `RISK-ACCEPTED`, `SESSION-STARTED`, `SESSION-ENDED`,
`SESSION-SAFETY-STOP`, `CRAWL`.

| Timestamp | Event | Actor | Details |
|---|---|---|---|
| {{isoDateTime}} | STAGE-START | qa-orchestrator | 1.1 Requirement intake |
