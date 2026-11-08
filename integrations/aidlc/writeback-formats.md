# AI-DLC Write-back Formats  *(v2 — disabled in MVP)*

Only active when `integrations.aidlc.writeBack.*` flags are `true`.

## Questions (`writeBack.questions`)
AI-DLC asks humans via question files with multiple-choice options and an `[Answer]:` tag.
QA testability findings on AI-DLC requirements are written as a new question file next to
AI-DLC's current-stage questions, named `qa-trust-questions-<stage>.md`, using AI-DLC's
format (options A/B/C…, `[Answer]:` line). Each question carries `QA-ref: <work item> Q-xx`
so answers flow back to the QA `questions.md`.

## Audit (`writeBack.auditEntries`)
Append-only lines to AI-DLC `audit.md` in its existing entry format, prefixed
`[QA Trust Architect]`, for gate decisions only.

Verify the current AI-DLC format by reading existing question/audit files before the first
write; mirror it exactly.
