# Targeted Interview

Humans confirm domain knowledge fastest when asked **specific, evidence-backed,
multiple-choice** questions. Follow `core/question-protocol.md` plus these rules.

## What to ask about (priority order)
1. `disputed` facts on critical rules / permissions / states
2. `low`-confidence facts on deep (top-risk/top-usage) features
3. Undocumented behaviour that looks suspicious (possible bug-turned-feature)
4. Document version ambiguity
5. Tacit-knowledge probe per deep feature (one bounded open question)

## Shape

```markdown
### Q-07 — Leave limit (BR-012)  `blocking`  `status: open`
**Context:** Validator allows 30 (src/Leave/LeaveValidator.cs:42). Test asserts 20
(tests/LeaveTests.cs#MaxDays). Error message says "maximum 20 days".
**Why it matters:** oracle for leave-request boundary tests in every future work item.
**Options:**
- A) 20 days — the validator is a bug   ← suggested (2 of 3 sources)
- B) 30 days — test and message are outdated
- C) Depends on role/contract type (explain)
- D) Other
[Answer]:
[Answered by]:
```

## Who to ask
Suggest the audience per question: `PO` (business intent), `dev` (implementation
detail, dead code), `tester` (known quirks, flaky areas), `support` (user complaints).

## Session tips (tell the user)
- 20 questions ≈ 15 minutes with a PO; answer letters only where possible.
- Answers become `confirmed` facts and are applied after G0 (or via DCP after G0).
