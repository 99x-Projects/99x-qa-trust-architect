# GitHub Adapter  *(planned: v3 — not implemented)*

## Design (agreed)
- Access via `gh` CLI / GitHub MCP.
- Requirement = Issue; AC = `## Acceptance Criteria` section in the issue body.
- **Test cases stay in the repo** (GitHub has no test management); the issue gets a
  comment/checklist linking to `docs/qa/<key>/2-design/test-cases/`.
- Gate status = label `qa-gate:G2-approved` (or GitHub Projects custom field).
- Defect = Issue with label `bug`; run results = Check run / workflow summary.
