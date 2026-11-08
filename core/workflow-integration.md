# Workflow Integration Contract

QA Trust Architect can run alongside other SDLC workflows (AI-DLC today; others later,
e.g. Spec Kit, BMAD, in-house processes). Each lives in `integrations/<name>/` and
implements this contract.

## 1. Required files per integration

| File | Purpose |
|---|---|
| `integration.md` | Detection, modes, behaviour |
| `mapping.yaml` | Glob-based map: their artifacts → our inputs (stage/slice), versioned |
| `gate-alignment.md` | Their approval points ↔ our gates |
| `writeback-formats.md` | How (if at all) we write into their workflow |

## 2. Modes

| Mode | Changes to the other workflow | Behaviour |
|---|---|---|
| `standalone` | – | Integration inactive |
| `companion` | None | Read their artifacts read-only; run our stages alongside |
| `embedded` | One extension rule file added to their rules | Their workflow invokes our stages at its approval points; joint gates |

## 3. Behavioural rules

1. **Detection** happens in stage 0.1; result stored in `_project/qa-profile.yaml` →
   `integrations.<name>.detected`, `layoutVersion`.
2. **Reference, don't copy.** Our artifacts link to theirs (`source: aidlc:<path>`) rather
   than duplicating content. Extracted facts keep the source path + hash.
3. **Read-only by default.** Never write into their folder unless a `writeBack` flag is on.
4. **Their changes → our DCPs.** When a mapped artifact's hash changes, raise DCPs with
   that artifact as source (`domainSync: dcp`).
5. **Graceful degradation.** If a mapped artifact is missing or the layout is unknown,
   warn once and fall back to our own discovery/stages.
6. **Keying.** Work may be keyed by their unit of work (`keyBy: unit`) or by tracker work
   item (`keyBy: workItem`); `storage.repo.layout` must use the matching placeholders.
