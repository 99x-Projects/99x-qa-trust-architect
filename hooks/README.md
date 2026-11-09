# Guard hooks

`hooks.json` registers `qa_guard.py` (standard-library Python 3.8+, started by `run-guard.sh`, which
picks `python3`, `python` or `py`). Guards run only in projects that contain `qa-trust.config.yaml`;
everywhere else they do nothing. Configure them under `guards:` in that file.

| Guard | Event / tools | Default | Behaviour |
|---|---|---|---|
| Secret scan (`secretScan`) | PreToolUse · Write, Edit, MultiEdit, NotebookEdit | block | Blocks private keys, GitHub/Atlassian/Slack/AWS/ADO tokens, JWTs, auth headers, credentials in URLs, and the literal value of any secret-looking variable from the env file or shell — in any file. Inside the QA root and QA config files also blocks `password: <literal>`-style values and legacy 52-char ADO PATs. References (`env:NAME`, `${NAME}`, `{{…}}`) are fine. |
| Secret files (`secretFiles`) | PreToolUse · Read, Grep, Bash, PowerShell, writes | block | The AI may not open, copy, print or edit the env file or `.auth/` recordings (creating the env file from the template is allowed), list all environment variables, or echo/redirect secret variables. Presence checks like `[ -n "$ADO_PAT" ]` and `git check-ignore .env` are allowed. |
| Domain writes (`domainWrites`) | PreToolUse · writes | ask | After G0, a direct edit of a domain file (outside `_proposals/`) asks for approval unless a DCP apply window is open (`qa_guard.py dcp-window open <ids>`). |
| Browser (`browser`) | PreToolUse · Playwright MCP `browser_*` | enforce | Navigation to production / `agentsAllowed: false` origins is denied; other origins not in the allowlist ask. Clicking/typing on elements matching `exploratory.guards.blockActions` asks. Typing into password/OTP fields is denied. Uploading secret files is denied. |
| Gate stale (`gateStale`) | PostToolUse · writes | mark | When an artifact covered by an approved / approved-with-risks gate changes (canonical hash differs from the gate record), sets the gate to `stale` in `qa-state.md`, appends to `audit.md`, and tells the user. Sync bookkeeping keys (`externalIds`, `contentHash`, `published`) are ignored. |

Modes: `block`/`enforce` deny the call · `ask` prompts the user · `warn` shows a message · `off`.

## Helper commands (run from the project root)

```
python <plugin>/hooks/qa_guard.py status                         # which guards are active
python <plugin>/hooks/qa_guard.py hash docs/qa/ADO-1234 G3       # artifacts list for a gate record
python <plugin>/hooks/qa_guard.py dcp-window open DCP-0007       # allow applying accepted DCPs (30 min)
python <plugin>/hooks/qa_guard.py dcp-window close
```

## Limits

- Guards are a safety net, not a sandbox: they read tool inputs, not what a program does at run time
  (e.g. a script that reads `.env` itself is allowed — that is how the ADO helper works).
- If Python is missing or a guard hits an internal error, the call proceeds and a warning is printed
  (fail open). Matches are reported by pattern or variable name; secret values are never printed.
- False positive? Add the string or a regex to `guards.secretScan.allow`, or set a guard to `warn`.
