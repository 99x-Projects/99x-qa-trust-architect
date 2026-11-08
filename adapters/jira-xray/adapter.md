# Jira + Xray Adapter  *(planned: v2 — not implemented)*

If selected in config before v2: tell the user it is not yet available; offer repo-only
storage (`storage.platform.enabled: false`) meanwhile.

## Design (agreed)
- **Stories, bugs, comments, labels:** Atlassian MCP (Jira REST).
- **Test entities:** Xray API — **Cloud** (GraphQL + REST v2, client id/secret from env
  `XRAY_CLIENT_ID` / `XRAY_CLIENT_SECRET`) or **Server/DC** (REST `raven/2.0`, PAT).
  Select via `platform.jira-xray.xrayDeployment: cloud | server`.
- **Mapping:**
  | Canonical | Xray |
  |---|---|
  | Gherkin TC | Test, type **Cucumber** (Gherkin stored as-is) |
  | Rule-table TC | Test, type **Manual** (steps: action / data / expected result) |
  | Automated TC | Test, type **Generic** (definition = automation path) |
  | Preconditions | **Precondition** issue, linked |
  | Test plan | **Test Plan** issue |
  | Run | **Test Execution** issue + test runs |
  | Requirement link | Xray "tests" requirement coverage link |
  | Gate status | Jira label `qa-gate:G2-approved` or custom field |
