# Question Protocol

Questions are how the AI gets missing knowledge from humans. They live in
`ITEM_DIR/questions.md` (work item) or `PROJECT_DIR/questions.md` (Phase 0 / domain).

## 1. Rules for writing questions

1. **Specific, never open-ended.** Not "Explain leave approval." Instead state what you
   found and offer choices.
2. **Show the evidence.** Quote the sources (doc, code path, test, error message, story).
3. **Offer options A/B/C** plus "Other". Mark a **suggested** option when the evidence
   favours one, and say why (e.g. "2 of 3 sources").
4. **Say why it matters**: which artifact/test depends on the answer.
5. **Classify**: `blocking` (stage cannot complete) or `non-blocking` (assumption used meanwhile).
6. **Batch**: group related questions; aim for ≤ 10 per round; most important first.
7. Never re-ask a resolved question; reference it (`see Q-03`).

## 2. Format

```markdown
### Q-07 — Leave limit (BR-012)  `blocking`  `status: open`
**Context:** Code validator `LeaveValidator.cs:42` allows 30 days. Unit test
`LeaveTests.MaxDays` asserts 20. Error message: "maximum 20 days".
**Why it matters:** AC-03 boundary values and TC-004..TC-006.
**Options:**
- A) 20 days — the validator is a bug   ← suggested (2 of 3 sources)
- B) 30 days — test and message are outdated
- C) Depends on role/contract type (explain)
- D) Other
**Assumption until answered:** none (blocking)

[Answer]:
[Answered by]:
```

## 3. Processing answers

- An answer is any non-empty text after `[Answer]:` (a letter is enough).
- On processing: set `status: resolved`, apply to artifacts, log in `audit.md`, raise
  DCPs for domain facts that were confirmed/changed (an answered question about a rule
  is strong evidence → status `confirmed` in the DCP).
- If an answer is unclear, add a follow-up question `Q-07a`; don't guess.

## 4. AI-DLC write-back (v2)

When `integrations.aidlc.writeBack.questions: true` and the question concerns a
requirement owned by AI-DLC, also write it in AI-DLC's question format at the location
defined in `integrations/aidlc/writeback-formats.md`, and link both copies.
