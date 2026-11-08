# Hooks (planned)

MVP ships no active hooks; guard behaviour is enforced by the rule files. Planned guards:

| Hook | Event | Behaviour |
|---|---|---|
| Domain write guard | PreToolUse (Write/Edit) | After G0, warn when a domain file is edited directly instead of via a DCP |
| Gate-stale detector | PostToolUse (Write/Edit) | Mark a gate `stale` when an artifact it covers changes |
| Secret scan | PreToolUse (Write) | Block writes of likely secrets into the QA root |
